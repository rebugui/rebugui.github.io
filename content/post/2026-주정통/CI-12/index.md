---
title: "[2026 주요정보통신기반시설] CI-12 취약한비밀번호복구절차(Weak Password Recovery)"
slug: "2026-주정통/CI-12"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "비밀번호 복구 기능 사용 시, 단순 정보(이름, 사번, 아이디 등)만을 활용하거나 SMS나 이메일 인증 시 발급되는 임시비밀번호가 동일하거나 유추 가능 여부 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Web
---

# 취약한비밀번호복구절차(Weak Password Recovery)

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CI-12 |
| **점검내용** | 비밀번호 복구 기능 사용 시, 단순 정보(이름, 사번, 아이디 등)만을 활용하거나 SMS나 이메일 인증 시 발급되는 임시비밀번호가 동일하거나 유추 가능 여부 점검 |
| **점검대상** | 웹 애플리케이션 소스코드 |
| **양호기준** | 비밀번호 재설정 시 난수를 이용하여, 인증된 사용자 메일이나 SMS로 임시 비밀번호 또는 비밀번호 재설정을 위한 링크가 전송되는 경우 |
| **취약기준** | 비밀번호 재설정 시 일정 패턴으로 재설정되고 웹사이트 화면에 바로 출력되는 경우 |
| **조치방법** | 비밀번호 복구 로직을 강화하고, 인증된 사용자 메일이나 SMS에서만 재설정된 비밀번호를 확인할 수 있도록 하여 비인가자가 비밀번호를 획득하지 못하도록 조치 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 비밀번호 재설정 시 난수를 이용하여, 인증된 사용자 메일이나 SMS로 임시 비밀번호 또는 비밀번호 재설정을 위한 링크가 전송되는 경우
- **취약**: 비밀번호 재설정 시 일정 패턴으로 재설정되고 웹사이트 화면에 바로 출력되는 경우

#### 경계 케이스 (Edge Case) 처리 방법
- 일반적인 경우 영향 없음
- 임시 비밀번호는 반드시 HTTPS를 통해 전송
- 임시 비밀번호는 한 번만 사용 가능하게 설정

#### 권장 설정값
- 임시 비밀번호 최소 12자 이상
- 대소문자, 숫자, 특수문자 조합
- 암호학적으로 안전한 난수 생성
- 재설정 링크 유효기간 1시간 이내 권장

### 2. 점검 방법

#### Step 1: 보안 질문 확인
```
비밀번호 복구 기능 유무를 파악하고, 복구 과정에서 보안 질문이 추측 가능하거나 소셜 엔지니어링으로 쉽게 답을 찾을 수 있는 단순 정보를 요구하는지 확인
```

**취약한 보안 질문 예:**
- "당신의 출생년도는?"
- "어머니의 성함은?"
- "출생 도시는?"
- "좋아하는 색깔은?"

#### Step 2: 임시 비밀번호 패턴 확인
```
비밀번호 복구 시 재설정된 비밀번호에 대하여 추측 가능한 일정 패턴으로 발급 유무 확인
```

#### Step 3: 이메일 무결성 검증 확인
```
비밀번호 복구 과정에서 해당 계정에 등록된 이메일 및 전화번호가 아닌 공격자의 정보로 변조가 가능한지 확인
```

### 3. 조치 방법

#### 1. 안전한 임시 비밀번호 생성

**Java SecureRandom 예시:**
```java
private static final String CHARACTERS =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
private static final int PASSWORD_LENGTH = 12;

private String generateTemporaryPassword() {
    SecureRandom secureRandom = new SecureRandom();
    StringBuilder password = new StringBuilder(PASSWORD_LENGTH);

    for (int i = 0; i < PASSWORD_LENGTH; i++) {
        int randomIndex = secureRandom.nextInt(CHARACTERS.length());
        password.append(CHARACTERS.charAt(randomIndex));
    }

    return password.toString();
}
```

**ASP.NET RNGCryptoServiceProvider 예시:**
```csharp
private string GenerateRandomPassword(int length) {
    const string chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    StringBuilder result = new StringBuilder(length);
    byte[] randomBytes = new byte[4 * length];

    using (var rng = new RNGCryptoServiceProvider()) {
        rng.GetBytes(randomBytes);
        for (int i = 0; i < length; i++) {
            uint randomInt = BitConverter.ToUInt32(randomBytes, i * 4);
            result.Append(chars[(int)(randomInt % (uint)chars.Length)]);
        }
    }

    return result.ToString();
}
```

**PHP random_int 예시:**
```php
function generateRandomPassword($length = 12) {
    $characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()';
    $charactersLength = strlen($characters);
    $randomPassword = '';

    for ($i = 0; $i < $length; $i++) {
        $randomPassword .= $characters[random_int(0, $charactersLength - 1)];
    }

    return $randomPassword;
}
```

#### 2. 2단계 인증 도입

```java
// 1단계: 본인 확인 (이메일 인증)
@PostMapping("/password/reset/request")
public String requestReset(@RequestParam String userid,
                           @RequestParam String email) {
    User user = userService.findByUserid(userid);

    // 등록된 이메일과 일치하는지 확인
    if (!user.getEmail().equals(email)) {
        return "redirect:/password/reset?error=email_mismatch";
    }

    // 인증 토큰 생성 및 이메일 전송
    String token = generateSecureToken();
    user.setResetToken(token);
    userService.save(user);

    emailService.sendResetEmail(user.getEmail(), token);
    return "redirect:/password/reset/sent";
}

// 2단계: 비밀번호 재설정
@PostMapping("/password/reset/confirm")
public String confirmReset(@RequestParam String token,
                           @RequestParam String newPassword) {
    User user = userService.findByResetToken(token);

    if (user == null || !user.isTokenValid()) {
        return "redirect:/password/reset?error=invalid_token";
    }

    // 비밀번호 재설정
    user.setPassword(passwordEncoder.encode(newPassword));
    user.clearResetToken();
    userService.save(user);

    return "redirect:/login?reset=success";
}
```

#### 3. 이메일/SMS로만 전송

```java
// 임시 비밀번호를 화면이 아닌 이메일로만 전송
@PostMapping("/password/reset")
public String resetPassword(@RequestParam String userid) {
    User user = userService.findByUserid(userid);

    // 안전한 임시 비밀번호 생성
    String tempPassword = generateTemporaryPassword();

    // 비밀번호 업데이트
    user.setPassword(passwordEncoder.encode(tempPassword));
    user.setPasswordChanged(false);
    userService.save(user);

    // 이메일로만 전송 (화면에 표시하지 않음)
    emailService.sendTempPassword(user.getEmail(), tempPassword);

    return "redirect:/login?message=temp_password_sent";
}

// 첫 로그인 시 비밀번호 변경 강제
@GetMapping("/login")
public String login() {
    if (currentUser != null && !currentUser.isPasswordChanged()) {
        return "redirect:/password/change?forced=true";
    }
    return "login";
}
```

#### 4. 토큰 기반 재설정 링크

```java
// 유효기간이 있는 토큰 생성
private String generateResetToken() {
    SecureRandom random = new SecureRandom();
    byte[] token = new byte[32];
    random.nextBytes(token);

    // Base64 URL Safe 인코딩
    return Base64.getUrlEncoder().withoutPadding().encodeToString(token);
}

// 재설정 링크 생성
private String createResetLink(String token) {
    return "https://example.com/password/reset?token=" + token;
}

// 토큰 유효성 검증 (1시간 유효)
public boolean isTokenValid(User user) {
    LocalDateTime expirationTime = user.getTokenCreatedAt().plusHours(1);
    return LocalDateTime.now().isBefore(expirationTime);
}
```

### 4. 참고 자료

**취약한 보안 질문 예시:**
- "어머니의 성함은?" (가족관계증명서로 확인 가능)
- "출생년도는?" (주민등록번호로 확인 가능)
- "좋아하는 색깔은?" (추측 용이)
- "첫째 자녀의 이름은?" (SNS 확인 가능)

**안전한 본인 확인 방법:**
1. 등록된 이메일로 인증번호 전송
2. 등록된 휴대폰으로 SMS 인증
3. OTP 앱 인증
4. 인증서 기반 인증

**비밀번호 복구 절차 권장사항:**

1. **본인 확인 (2단계 이상)**
   - 등록된 이메일/SMS로 인증번호 전송
   - 본인 확인 질문은 피해야 함 (SNS 유출 가능)

2. **임시 비밀번호**
   - 최소 12자 이상
   - 대소문자, 숫자, 특수문자 조합
   - 암호학적으로 안전한 난수 생성

3. **재설정 링크**
   - 일회용 토큰 사용
   - 짧은 유효기간 (1시간 이내 권장)
   - 사용 후 즉시 무효화

4. **강제 비밀번호 변경**
   - 임시 비밀번호로 로그인 후 즉시 변경 요구
   - 변경 전 다른 기능 사용 제한

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.