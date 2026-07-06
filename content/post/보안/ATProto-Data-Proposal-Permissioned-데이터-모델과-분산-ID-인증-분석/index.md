---
title: "ATProto Data Proposal: Permissioned 데이터 모델과 분산 ID 인증 분석"
date: 2026-07-06T17:29:30+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

최근 소셜 미디어 환경에서 데이터 주권(Data Sovereignty)은 더 이상 추상적인 개념이 아닙니다. 수많은 사용자가 자신의 디지털 정체성과 생성한 콘텐츠를 거대 플랫폼에 맡기고 있지만, 실제로는 플랫폼의 정책 변화나 해킹 사고 한 번으로 모든 데이터를 통제권을 잃을 위험에 노출되어 있습니다. 기존 중앙 집중식 모델에서는 "당신은 이 계정의 소유자입니다"라는 강력한 인증(Authentication)만 제공할 뿐, '누가', '어떤 리소스'에 대해 '무엇을 할 수 있는지'에 대한 세밀한 통제는 부족했습니다.

탈중앙화된 소셜 그래프를 구현하며 큰 주목을 받고 있는 ATProto (AT Protocol) 역시 이 문제를 해결하려는 강력한 대안입니다. ATProto는 사용자의 데이터를 중앙 서버가 아닌 분산된 네트워크 상에 배치함으로써, 데이터의 이동성과 불변성을 보장합니다. 그러나 기존 ATProto 모델은 주로 '사용자 인증' 수준에서 권한을 부여했습니다. 즉, "이 사용자(Actor)는 이 리소스(Resource)를 볼 수 있다" 정도였습니다.

하지만 보안 전문가의 관점에서 보면, 단순 접근 허용만으로는 충분하지 않습니다. 공격자는 단순히 읽기 권한을 얻는 것을 넘어, 중요한 피드나 개인 메시지를 **조작(Mutation)**하거나 **삭제**할 수도 있습니다. 이 간극을 메우는 것이 바로 Bluesky Social에서 제안된 **ATProto Permissioned Data Model**입니다. 이는 탈중앙화의 강력함에 세밀한 접근 통제 기능을 결합하여, 데이터 주권을 한 단계 끌어올리는 혁신적인 방안입니다.

## ATProto와 권한 부여 모델의 기술적 배경

기존 ATProto는 DID(Decentralized Identifier)를 중심으로 사용자의 상태(State)와 리소스(Resource)를 네트워크 상에 기록합니다. 이 구조에서 특정 데이터 객체(예: 게시물, 프로필 이미지 등)가 존재할 때, 해당 데이터를 읽거나 쓸 수 있는 주체를 정의하는 것이 핵심입니다.

Permissioned 모델은 여기에 **읽기 권한 (Read Permission)**과 **쓰기/수정 권한 (Write Permission)**이라는 두 가지 차원의 제어 메커니즘을 추가합니다. 이는 단순히 "당신이 이 데이터의 주인인가?"를 묻는 것을 넘어, "주인일 수도 있고, 초대받은 협력자일 수도 있으며, 읽기 전용 구독자일 수도 있다"와 같이 정교한 역할을 부여하는 것입니다.

### ATProto Permissioned 모델 작동 원리 (Mermaid 다이어그램)

다음 다이어그램은 새로운 권한 부여 모델이 데이터 접근 요청을 처리하는 흐름을 시각적으로 보여줍니다. 모든 요청은 리소스에 도달하기 전에 **권한 검증 단계**를 거칩니다.

```javascript
graph TD
    A["Actor (요청자)"] --> B{"Resource (데이터 객체)"};
    B --> C{Permission Check};
    C -- Read Request --> D{Read Permission 부여?}
    C -- Write/Mutate Request --> E{Write Permission 부여?}
    D -- Yes --> F[Data Access Granted];
    D -- No --> G["Access Denied (403)"];
    E -- Yes --> H[Data Mutation Successful];
    E -- No --> I["Access Denied (Mutation Fail)"];
```

## 핵심 분석: 기존 모델 대비 보안적 우위 비교

Permissioned 모델이 제공하는 가장 큰 가치는 **세분화된 통제(Granularity)**입니다. 이는 일반적인 RBAC(Role-Based Access Control)의 개념을 탈중앙화 환경에 완벽하게 이식한 형태라고 볼 수 있습니다.

| 비교 항목 | 기존 ATProto (Authentication 기반) | Permissioned Model (Authorization 기반) | 보안적 의미/장점 |
| :--- | :--- | :--- | :--- |
| **기본 검증 단위** | 사용자 ID 일치 여부 (Who owns it?) | 액터(Actor)와 리소스 간의 권한 관계 (What can they do to it?) | 통제 범위의 확장 |
| **주요 부여 권한** | 접근 허용/거부 (Read Access) | 읽기, 쓰기, 수정, 삭제 등 세분화된 역할 | 공격 벡터 감소 및 정밀 제어 가능 |
| **데이터 주권 강화** | 데이터가 네트워크에 존재함 (Decentralization) | 누가 어떤 행위를 할지 정의됨 (Granularity) | '소유'를 넘어선 '통제력' 확보 |
| **실패 시 결과** | 접근 자체가 불가능하거나, 소유자만 가능. | 권한이 부족할 경우, 특정 행위(쓰기 등)만 실패함. | 서비스 가용성 유지 및 부분적 조작 허용 |

### 보안 관점에서의 심층 분석: 왜 Permissioned가 중요한가?

1. **무단 데이터 변조 방지 (Integrity Protection):** 기존 모델에서 A라는 사용자가 B의 게시물에 접근할 수 있다면, A는 해당 게시물을 수정하거나 삭제하는 데 성공합니다. 하지만 Permissioned 모델에서는 A에게 `Read` 권한만 부여했다면, A가 아무리 강력한 API 호출을 시도해도 **쓰기 권한이 없으므로** 데이터 무결성(Integrity)은 완벽하게 보호됩니다.
2. **위협 표면 축소 (Attack Surface Reduction):** 모든 리소스에 대해 '최대 허용 범위'를 설정함으로써, 공격자가 침투했을 때 피해 규모가 전체 그래프로 확산되는 것을 막고 해당 권한이 부여된 특정 노드(Node) 내에서만 활동하도록 강제합니다.
3. **협업 및 관계 정의의 정교화:** 단순히 '친구'라는 관계로 묶는 것이 아니라, "A는 B의 피드를 읽을 수 있고, C는 A와 B가 공동 작성한 문서에 대해 쓰기 권한을 가진다"와 같은 복잡한 보안 정책 구현이 가능해집니다.

## 실무 적용 가이드: Permissioned 모델 활용 단계

실제 시스템 설계 시 ATProto 기반 서비스에서 이 새로운 권한 부여 모델을 적용하는 과정은 다음과 같습니다. 이는 백엔드 API 게이트웨이나 리소스 관리 계층(Resource Manager Layer)에서 구현됩니다.

### Step 1: 리소스 및 액터 정의 (Definition)

먼저, 데이터 객체(리소스)를 식별하고, 해당 데이터를 조작할 주체(액터)를 명확히 합니다. ATProto에서는 DID가 이 액터를 담당합니다.

### Step 2: 권한 정책 할당 (Policy Assignment)

각 리소스에 대해 어떤 액터에게 어떤 권한(`READ`, `WRITE`, `ADMIN` 등)을 부여할지 정의하고, 이를 메타데이터로 저장합니다.

### Step 3: 접근 요청 시 검증 (Enforcement Check)

액터가 특정 리소스에 대한 연산을 요청하면, 시스템은 다음 논리 흐름에 따라 권한 유효성을 확인합니다.

```python
# 개념 설명용 예시 코드: Permission Check Logic
class ResourceManager:
    def __init__(self):
        # {resource_id: {actor_did: [permissions]}} 형태로 저장된다고 가정
        self.policies = {} 

    def check_permission(self, resource_id: str, actor_did: str, required_perm: str) -> bool:
        """요청된 권한이 해당 리소스에 부여되었는지 확인한다."""
        if resource_id not in self.policies:
            return False # 정책 자체가 없다면 기본적으로 접근 불가

        actor_perms = self.policies[resource_id].get(actor_did, [])
        
        # 필요한 권한이 액터의 허용된 권한 목록에 포함되어 있는지 확인
        if required_perm in actor_perms:
            return True
        else:
            print(f"🚨 {actor_did}는 리소스 {resource_id}에 대한 '{required_perm}' 권한이 없습니다.")
            return False

# 사용 예시
rm = ResourceManager()
# Resource 101에 Actor A에게 Read와 Write 권한 부여
rm.policies['R101'] = {'did:actorA': ['READ', 'WRITE']} 

# 테스트 1: 쓰기 요청 (성공 예상)
print(f"쓰기 가능 여부: {rm.check_permission('R101', 'did:actorA', 'WRITE')}") # True

# 테스트 2: 읽기 전용 액터에게 쓰기 요청 (실패 예상)
rm.policies['R102'] = {'did:readerB': ['READ']}
print(f"쓰기 가능 여부: {rm.check_permission('R102', 'did:readerB', 'WRITE')}") # False
```

## 결론

ATProto Permissioned Data Model은 탈중앙화 소셜 그래프의 잠재력을 극대화하는 핵심 보안 기제입니다. 이는 단순한 분산 저장소를 넘어, **'탈중앙화된 권한 부여 시스템(Decentralized Authorization System)'**을 구축했음을 의미합니다. 이 모델 덕분에 우리는 데이터 주권을 '소유권' 수준에서 '통제력' 수준으로 끌어올릴 수 있게 되었습니다.

전문가적인 관점에서 볼 때, 이 Permissioned 기능은 앞으로 DID 기반의 모든 서비스(DeFi, Web3 소셜 등)에서 표준화될 핵심 보안 요구사항이 될 것입니다. 향후 ATProto는 리소스 간 상호 작용에 대한 권한 정책까지 확장하여, 복잡한 스마트 컨트랙트와 유사한 수준의 데이터 흐름 제어를 가능하게 할 것으로 기대됩니다.

결론적으로, Permissioned 모델은 탈중앙화라는 '어디에 있는가'의 문제를 해결했다면, 이제는 **"누가 무엇을 할 수 있는가"**라는 가장 중요한 보안 질문에 명확하고 강력한 답을 제시하고 있습니다.

--- 🔗 **참고 자료:** ATProto Permissioned Data Proposal Draft (Bluesky Social) [https://github.com/bluesky-social/proposals/pull/94](https://github.com/bluesky-social/proposals/pull/94)

---

**출처**: [https://github.com/bluesky-social/proposals/pull/94](https://github.com/bluesky-social/proposals/pull/94)