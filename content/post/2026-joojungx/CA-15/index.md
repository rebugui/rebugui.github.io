---
title: "[2026 주요정보통신기반시설] CA-15 관계형데이터베이스로깅설정"
slug: "2026-주정통/CA-15"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "관계형 데이터베이스 로깅 설정 여부 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Cloud
---

# CA-15 관계형데이터베이스로깅설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CA-15 |
| **점검내용** | 관계형 데이터베이스 로깅 설정 여부 점검 |
| **점검대상** | 클라우드 플랫폼 |
| **판단기준** | 양호: 관계형 데이터베이스 로깅 설정이 기관 정책에 따라 설정된 경우 |
| **판단기준** | 취약: 관계형 데이터베이스 로깅 설정이 기관 정책에 따라 설정되지 않은 경우 |
| **조치방법** | 관계형 데이터베이스 로깅 설정 |

---
## 상세 설명

### 1. 항목 개요

클라우드 관계형 데이터베이스(RDS, Cloud SQL, Azure SQL 등)의 로깅 설정은 데이터베이스 성능 모니터링, 보안 감사, 문제 해결에 필수적입니다. 느린 쿼리, 오류, 접속 시도, 스키마 변경 등을 기록하여 데이터베이스의 이상 징후를 조기에 발견하고 보안 사고를 조사할 수 있습니다.

### 2. 왜 이 항목이 필요한가요?

**보안 위협 시나리오:**
1. **SQL 인젝션 탐지**: 악의적인 SQL 쿼리 패턴 탐지
2. **비인가 접속 탐지**: 실패한 로그인 시도, 이상 IP에서의 접속
3. **데이터 유출 조사**: 누가, 언제, 어떤 데이터에 접근했는지 추적
4. **성능 이슈 분석**: 느린 쿼리, 잠금 경합 등 성능 문제 식별

**실제 사례**
- SQL 인젝션 공격이 발생했는데 데이터베이스 로그가 없어 공격 경로 추적 불가
- 데이터베이스 성능 저하가 발생했는데 느린 쿼리 로그가 없어 원인 파악 지연

### 3. 점검 대상

- 모든 클라우드 관계형 데이터베이스 (RDS, Cloud SQL, Azure SQL 등)
- 일반 로그 (General Log)
- 느린 쿼리 로그 (Slow Query Log)
- 에러 로그 (Error Log)
- 감사 로그 (Audit Log)

### 4. 판단 기준

| 구분 | 기준 |
|------|------|
| **양호** | 데이터베이스 로깅이 기관 정책(로그 수준, 보관 기간 등)에 따라 설정된 경우 |
| **취약** | 데이터베이스 로깅이 비활성화되거나 기관 정책에 맞지 않게 설정된 경우 |

### 5. 점검 방법

#### Step 1: AWS RDS 로그 설정 확인

```bash
# AWS CLI 예시
# RDS 파라미터 그룹 확인
aws rds describe-db-parameters \
  --db-parameter-group-name mydb-parameter-group \
  --query "Parameters[?ParameterName==`general_log` || ParameterName==`slow_query_log`].{ParameterName:ParameterName,ParameterValue:ParameterValue}"

# 발행된 로그 확인
aws rds describe-db-log-files \
  --db-instance-identifier mydb

# 로그 내용 다운로드
aws rds download-db-log-file-portion \
  --db-instance-identifier mydb \
  --log-file-name error/mysql-error.log
```

#### Step 2: Azure SQL Database 감사 확인

```bash
# Azure CLI 예시
# 감사 설정 확인
az sql db audit-policy show \
  --name database-name \
  --server server-name \
  --resource-group group-name

# 진단 설정 확인
az monitor diagnostic-settings list \
  --resource /subscriptions/subscription-id/resourceGroups/group-name/providers/Microsoft.Sql/servers/server-name/databases/database-name
```

#### Step 3: GCP Cloud SQL 로그 확인

```bash
# GCP CLI 예시
# Cloud SQL 로그 확인
gcloud logging read "resource.type=cloudsql_database" \
  --limit 10

# 감사 로그 확인
gcloud logging read "logName=cloudaudit.googleapis.com%2Factivity" \
  --filter="resource.labels.database_id=instance-name"
```

### 6. 조치 방법

#### Step 1: AWS RDS 로깅 활성화

```bash
# 파라미터 그룹 생성
aws rds create-db-parameter-group \
  --db-parameter-group-name mydb-parameter-group \
  --db-parameter-group-family mysql8.0 \
  --description "My parameter group with logging enabled"

# 일반 로그 활성화 (개발/테스트 환경만 권장)
aws rds modify-db-parameter-group \
  --db-parameter-group-name mydb-parameter-group \
  --parameters "ParameterName=general_log,ParameterValue=1,ApplyMethod=immediate"

# 느린 쿼리 로그 활성화
aws rds modify-db-parameter-group \
  --db-parameter-group-name mydb-parameter-group \
  --parameters "ParameterName=slow_query_log,ParameterValue=1,ApplyMethod=immediate" \
  --parameters "ParameterName=long_query_time,ParameterValue=2,ApplyMethod=immediate"

# 로그 출력을 파일로 설정
aws rds modify-db-parameter-group \
  --db-parameter-group-name mydb-parameter-group \
  --parameters "ParameterName=log_output,ParameterValue=FILE,ApplyMethod=immediate"

# 바이너리 로그 활성화 (복구/복제용)
aws rds modify-db-instance \
  --db-instance-identifier mydb \
  --backup-retention-period 7 \
  --apply-immediately

# 파라미터 그룹을 DB 인스턴스에 적용
aws rds modify-db-instance \
  --db-instance-identifier mydb \
  --db-parameter-group-name mydb-parameter-group \
  --apply-immediately
```

#### Step 2: CloudWatch Logs로 RDS 로그 내보내기

```bash
# 로그 내보내기 활성화
aws rds create-db-instance \
  --db-instance-identifier mydb \
  --db-instance-class db.t3.micro \
  --engine mysql \
  --enabled-cloudwatch-logs-exports '["error","general","slowquery"]'

# 기존 인스턴스에 로그 내보내기 추가
aws rds modify-db-instance \
  --db-instance-identifier mydb \
  --cloudwatch-logs-export-configuration '{
    "LogTypesToEnable": ["error","general","slowquery"]
  }' \
  --apply-immediately
```

#### Step 3: PostgreSQL 로깅 설정

```sql
-- PostgreSQL 파라미터 그룹 설정
aws rds modify-db-parameter-group \
  --db-parameter-group-name mydb-parameter-group \
  --parameters "ParameterName=log_statement,ParameterValue=all,ApplyMethod=immediate" \
  --parameters "ParameterName=log_min_duration_statement,ParameterValue=1000,ApplyMethod=immediate" \
  --parameters "ParameterName=log_connections,ParameterValue=1,ApplyMethod=immediate" \
  --parameters "ParameterName=log_disconnections,ParameterValue=1,ApplyMethod=immediate" \
  --parameters "ParameterName=log_lock_waits,ParameterValue=1,ApplyMethod=immediate"
```

#### Step 4: Azure SQL Database 감사 설정

```bash
# 감사 설정 (Storage로)
az sql db audit-policy update \
  --name database-name \
  --server server-name \
  --resource-group group-name \
  --state Enabled \
  --storage-account mystorageaccount \
  --storage-key storage-key \
  --retention-days 90

# 감사 설정 (Log Analytics로)
az sql db audit-policy update \
  --name database-name \
  --server server-name \
  --resource-group group-name \
  --state Enabled \
  --log-analytics-workspace myworkspace

# 진단 설정 추가
az monitor diagnostic-settings create \
  --name my-diagnostic-settings \
  --resource /subscriptions/subscription-id/resourceGroups/group-name/providers/Microsoft.Sql/servers/server-name/databases/database-name \
  --workspace myworkspace \
  --logs '[
    {"category": "SQLInstanceMetrics", "enabled": true},
    {"category": "Errors", "enabled": true},
    {"category": "Timeouts", "enabled": true},
    {"category": "Blocks", "enabled": true},
    {"category": "SQLInsights", "enabled": true}
  ]'
```

#### Step 5: GCP Cloud SQL 로깅 설정

```bash
# Cloud SQL 인스턴스 업데이트 (로깅 활성화)
gcloud sql instances patch instance-name \
  --database-flags="log_queries=true,log_statement=all,log_duration=true"

# 로그 내보내기 설정
gcloud logging sinks create my-sink \
  bigquery.googleapis.com/projects/my-project/datasets/my_dataset \
  --log-filter='resource.type="cloudsql_database" AND resource.labels.database_id="instance-name"'

# 감사 로그 활성화
gcloud sql instances patch instance-name \
  --audit-log-flags="SUCCESSFUL_READ,FAILED_READ"
```

### 7. 로그 분석 및 모니터링

#### CloudWatch Logs Insights 쿼리 예시

```
# 느린 쿼리 분석
fields @timestamp, user, query_time, sql_text
| filter @logStream like /slowquery/
| parse @message "* execution_time: *" as sql_text, query_time
| sort query_time desc
| limit 100

# 데이터베이스 오류 분석
fields @timestamp, error_code, error_message
| filter @logStream like /error/
| parse @message "* [*]: *" as error_code, error_message
| stats count() by error_code
| sort count desc

# 비정상적인 접속 시도
fields @timestamp, user, host
| filter @message like /Access denied/
| stats count() by user, host
| sort count desc
```

### 8. 성능 고려사항

| 로그 유형 | 영향 | 권장 사항 |
|----------|------|----------|
| **일반 로그 (General Log)** | 높음 | 운영 환경에서는 비활성화, 문제 해결 시에만 일시적 활성화 |
| **느린 쿼리 로그** | 낮음~중간 | 항상 활성화, 임계값은 1~2초 권장 |
| **에러 로그** | 낮음 | 항상 활성화 |
| **감사 로그** | 중간 | 규정 준수가 필요한 경우 활성화 |

### 9. 로그 보관 기간 설정

```bash
# CloudWatch Logs 보관 기간 설정
aws logs put-retention-policy \
  --log-group-name /aws/rds/instance/mydb/slowquery \
  --retention-in-days 90

# S3로 로그 아카이브
aws rds create-db-instance-read-replica \
  --db-instance-identifier mydb-replica \
  --source-db-instance-identifier mydb
```

### 10. 조치 시 주의사항

| 주의사항 | 설명 |
|----------|------|
| **성능 영향** | 일반 로그는 디스크 I/O 증가, 느린 쿼리 로그는 임계값 조정 필요 |
| **스토리지 비용** | 로그 파일이 커질 수 있으므로 정기적 삭제 아카이브 |
| **민감 정보** | 로그에 민감 데이터가 포함될 수 있으므로 마스킹 고려 |
| **접근 권한** | 데이터베이스 로그는 DBA, 보안팀만 접근 허용 |

### 11. 참고 자료

- **AWS RDS Logging Documentation**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_LogAccess.html
- **Azure SQL Database Auditing**: https://docs.microsoft.com/azure/azure-sql/database/auditing-overview
- **GCP Cloud SQL Logging**: https://cloud.google.com/sql/docs/mysql/logging

---

## 요약

**관계형데이터베이스로깅설정**은 데이터베이스의 상태를 모니터링하고 보안 사고를 탐지하는 핵심 항목입니다. 느린 쿼리 로그, 에러 로그, 감사 로그를 활성화하고 CloudWatch Logs, Log Analytics 등 중앙 로깅 시스템으로 수집하여 분석하세요. 일반 로그는 운영 환경에서는 비활성화하고 문제 해결 시에만 일시적으로 활성화하여 성능 영향을 최소화해야 합니다.

**핵심 액션 아이템**
1. 느린 쿼리 로그 항상 활성화 (임계값: 1~2초)
2. 에러 로그 항상 활성화
3. 감사 로그 활성화 (규정 준수 필요 시)
4. CloudWatch Logs/Log Analytics로 중앙 집중화
5. 로그 보관 기간 설정 (최소 90일)
