---
title: "[2026 주요정보통신기반시설] W-37 비인가된 NFS 데이터 접근 제한"
slug: "2026-주정통/W-37"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "예약된 작업에 의심스러운 명령의 등록 여부 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-37 비인가된 NFS 데이터 접근 제한

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-37 |
| **점검내용** | 예약된 작업에 의심스러운 명령의 등록 여부 점검 |
| **점검대상** | Windows 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | 불필요한 명령어나 파일 등 주기적인 예약 작업의 존재 여부를 주기적으로 점검하고 제거한 경우 |
| **취약기준** | 불필요한 명령어나 파일 등 주기적인 예약 작업의 존재 여부를 주기적으로 점검하지 않거나, 불필요한 작업을 제거하지 않은 경우 |
| **조치방법** | 예약 작업에 대한 주기적인 확인 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: NFS 공유 설정 시 접근 가능한 클라이언트를 IP 주소 단위로 제한한 경우
- **취약**: 모든 클라이언트(All Machines)에 대해 접근을 허용하거나, 'Everyone' 권한이 부여된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| "모든 컴퓨터"에 읽기/쓰기 권한 | 취약 | 매우 위험 |
| "모든 컴퓨터"에 읽기 전용 | 주의 | 정보 유출 가능 |
| 특정 IP에만 권한 | 양호 | 화이트리스트 구성 |
| 루트 액세스 허용 | 취약 | 최고 권한 노출 |
| 내부망 대역 허용 | 양호 | 네트워크 분할 필요 |
| NFS 서비스 중지 | 양호 | 불필요한 경우 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| NFS 공유 | 클라이언트 제한 | 특정 IP만 허용 | 화이트리스트 |
| NFS 공유 | Everyone 권한 | 제거 | 불필요한 권한 삭제 |
| NFS 공유 | 루트 액세스 | 사용 안 함 | Squash Root |
| 방화벽 | NFS 포트 | 허용 IP로 제한 | 2049/nfs 등 |
| NFS 서비스 | 상태 | 필요 시만 실행 | 불필요 시 중지 |

### 2. 점검 방법

#### Windows NFS 서비스 점검

NFS 공유에 접근 제어가 설정되지 않으면, 권한 없는 사용자가 데이터에 접근할 수 있습니다.

```powershell
# NFS 공유 권한 확인 (Server for NFS 설치 시)
# 명령 프롬프트에서
nfshare
```

**양호 출력 예시:**
```text
Name      Path                          Anonymous  Unrestricted
----      ----                          ---------  ------------
data      C:\NFS\data                   No         No
Allowed clients: 192.168.1.100, 192.168.1.101
```

**취약 출력 예시:**
```text
Name      Path                          Anonymous  Unrestricted
----      ----                          ---------  ------------
data      C:\NFS\data                   Yes        No
Allowed clients: All Machines
```

```powershell
# NFS 서비스 상태 확인
Get-Service -Name "*NFS*" -ErrorAction SilentlyContinue | Select-Object Name, Status, StartType
```

```cmd
# NFS 포트 확인
netstat -an | findstr ":2049"
```

### 3. 조치 방법

#### Windows NFS 서비스 설정

1. **NFS 공유 클라이언트 제한 설정**
   ```cmd
   # 특정 IP에만 읽기/쓰기 권한 부여
   nfshare data C:\NFS\data -o rw=192.168.1.100,192.168.1.101

   # 특정 IP에만 읽기 전용 권한 부여
   nfshare data C:\NFS\data -o ro=192.168.1.100,192.168.1.101
   ```

2. **서버 관리자에서 설정 (GUI)**
   ```
   1. 서버 관리자 > 파일 및 스토리지 서비스 > 공유
   2. 프로토콜이 "NFS"인 공유 우클릭 > 속성
   3. [공유 사용 권한] 탭
   4. "모든 컴퓨터" 항목 제거
   5. [추가] 클릭 > 허용할 클라이언트 IP 입력
   6. 사용 권한(읽기/쓰기) 선택 > [확인]
   ```

3. **루트 액세스 비활성화**
   ```
   1. NFS 공유 속성 > [고급] 또는 [보안] 탭
   2. "루트 액세스 허용" 체크 해제
   ```

4. **NFS 서비스 비활성화 (사용하지 않는 경우)**
   ```powershell
   # Server for NFS 서비스 중지
   Stop-Service -Name "NfsService" -Force

   # 시작 유형 변경
   Set-Service -Name "NfsService" -StartupType Disabled
   ```

5. **서비스 재시작**
   ```powershell
   # NFS 서비스 재시작
   Restart-Service -Name "NfsService"
   ```

### 4. 참고 자료

- [Microsoft Docs: Network File System](https://docs.microsoft.com/ko-kr/windows-server/storage/nfs/nfs-overview)
- [CIS Benchmark: 18.5.20.1 Ensure 'NFS Server' is set to 'Disabled' or 'Secure'](https://www.cisecurity.org/)
- [RFC 3530: Network File System (NFS) version 4 Protocol](https://tools.ietf.org/html/rfc3530)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.