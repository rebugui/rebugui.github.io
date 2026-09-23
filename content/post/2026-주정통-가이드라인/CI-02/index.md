---
title: "[2026 주요정보통신기반시설] CI-02 SQL 인젝션(SQL Injection)"
slug: "2026-주정통/CI-02"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-09-23
description: "웹애플리케이션내 입력값이 SQL 쿼리에 삽입되어 비인가된 데이터베이스 접근과 조작 가능 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
draft: false
---

# SQL 인젝션(SQL Injection)

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CI-02 |
| **점검내용** | 웹애플리케이션내 입력값이 SQL 쿼리에 삽입되어 비인가된 데이터베이스 접근과 조작 가능 여부 점검 |
| **점검대상** | 웹 애플리케이션 소스코드, 웹방화벽 |
| **양호기준** | 임의로 작성된 SQL 쿼리 입력에 대한 적절한 검증을 통해 비정상적인 쿼리가 실행되지 않도록 하는 경우 |
| **취약기준** | 임의로 작성된 SQL 쿼리 입력에 대한 검증이 이루어지지 않아 비정상적인 쿼리가 실행되는 경우 |
| **조치방법** | 소스코드 내 SQL 쿼리를 입력값으로 받는 함수나 코드를 사용할 경우, 임의의 SQL 쿼리 입력에 대한 검증 로직을 구현하여 서버에 검증되지 않는 SQL 쿼리요청 시 에러 페이지가 아닌 정상 페이지가 반환되도록 필터링 처리하고 웹방화벽에 SQL 인젝션 관련 룰셋을 적용하여 SQL 인젝션 공격을 차단함 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 임의로 작성된 SQL 쿼리 입력에 대한 적절한 검증을 통해 비정상적인 쿼리가 실행되지 않도록 하는 경우
- **취약**: 임의로 작성된 SQL 쿼리 입력에 대한 검증이 이루어지지 않아 비정상적인 쿼리가 실행되는 경우

#### 경계 케이스 (Edge Case) 처리 방법
- 사용자 입력의 허용 길이·형식은 업무 목적에 맞게 검증하되, SQL 문법 문자 제거를 인젝션 방어로 사용하지 않음
- SQL 매퍼에서 `${}` 구문은 사용자 입력값이 SQL 구문으로 해석되므로 반드시 파라미터 바인딩(`#{}`) 사용

#### 권장 설정값
- 모든 값은 Prepared Statement/파라미터 바인딩 사용
- 컬럼·정렬 방향처럼 바인딩할 수 없는 SQL 구조는 사전에 정의한 허용 목록에서만 선택

### 2. 점검 방법

#### Step 1: 기본 SQL 인젝션 테스트
```
사용자 입력값 조건에 따른 참, 거짓 SQL 쿼리를 삽입하여 응답의 변화(응답시간, 에러메시지, 응답 내용 등) 유무 확인
```

**테스트 패턴:**
- `' OR '1'='1`
- `' OR '1'='2`
- `' AND 1=1--`
- `' AND 1=2--`

#### Step 2: 인증 페이지 우회 테스트
```
인증 페이지(로그인, 비밀번호 검증 등) 내 참이 되는 SQL 쿼리를 삽입하여 우회 유무 확인
```

### 3. 조치 방법

#### 1. Prepared Statement 사용 (가장 권장)

**Java 예시:**
```java
String sql = "SELECT * FROM users WHERE username = ?";
PreparedStatement preparedStatement = connection.prepareStatement(sql);
preparedStatement.setString(1, userInput);
ResultSet resultSet = preparedStatement.executeQuery();
```

**ASP.NET 예시:**
```csharp
string strQry = "SELECT count(*) FROM users WHERE userName = @username AND Password = @password";
using (SqlCommand cmd = new SqlCommand(strQry, cnx)) {
    cmd.Parameters.Add(new SqlParameter("@username", SqlDbType.VarChar, 50) { Value = txtUser.Text });
    cmd.Parameters.Add(new SqlParameter("@password", SqlDbType.VarChar, 50) { Value = txtPassword.Text });
    int intRecs = (int)cmd.ExecuteScalar();
}
```

**PHP 예시:**
```php
$sql = "SELECT * FROM users WHERE username = ?";
$stmt = $pdo->prepare($sql);
$stmt->execute([$userInput]);
$results = $stmt->fetchAll(PDO::FETCH_ASSOC);
```

#### 2. ORM 파라미터 바인딩 사용

**JPA-Hibernate 예시:**
```java
public List<Item> findItemsByUserInput(String userInput) {
    String jpql = "SELECT i FROM Item i WHERE i.itemID > :userInput";
    Query query = em.createQuery(jpql, Item.class);
    query.setParameter("userInput", userInput);
    return query.getResultList();
}
```

**MyBatis 예시:**
```xml
<!-- 파라미터 바인딩 #{} 사용 -->
<select id="selectUser" resultType="User">
    SELECT * FROM users WHERE username = #{username}
</select>

<!-- 주의: ${}는 SQL 인젝션 취약점 있음 -->
<select id="selectUser" resultType="User">
    SELECT * FROM users WHERE username = ${username}  <!-- 취약함 -->
</select>
```

#### 3. 입력값 검증의 역할

입력 길이·형식 등 업무 규칙을 검증하되, SQL 키워드나 특수문자를 제거하는 블랙리스트를 SQL 인젝션 방어로 사용하지 마세요. 정상 입력을 훼손하고 우회될 수 있습니다. 값은 위와 같이 파라미터에 바인딩하고, SQL 구조를 선택해야 할 때만 고정된 허용 목록을 사용합니다.

#### 4. 에러 메시지 처리
- 시스템에서 제공하는 에러 메시지 및 DBMS에서 제공하는 에러코드가 노출되지 않도록 예외처리
- 일반적인 오류 메시지만 사용자에게 표시

```java
catch (SQLException e) {
    // 브라우저에 일반적인 오류 메시지를 반환
    System.out.println("An error occurred. Please try again later.");
}
```

#### 5. 웹 방화벽 룰셋 적용
- 웹 방화벽(WAF)에 SQL Injection 관련 룰셋 추가

### 4. 참고 자료

**입력 검증과 쿼리 바인딩:**

입력 형식 검증은 업무 요구사항을 위한 것이며, 쿼리 바인딩을 대체하지 않습니다. 화면에 결과를 표시할 때의 출력 인코딩도 SQL 인젝션 방어와 별개의 조치입니다.

**파라미터 바인딩이란?**
- 쿼리를 실행할 때, 쿼리 문자열과 사용자 입력값(파라미터)을 분리하여 처리하는 기법
- 데이터베이스는 쿼리 문자열을 미리 파싱하고 컴파일하며, 쿼리 실행 시점에 파싱된 쿼리 문자열에 파라미터를 바인딩하여 데이터를 전달
- 데이터베이스는 파라미터를 데이터로만 인식
- [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.