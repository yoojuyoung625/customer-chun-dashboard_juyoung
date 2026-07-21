---
date: 2026-07-21
type: schema
source: "[[data/data_usage_history.csv]]"
related_data:
  - "[[02_data/data_customers]]"
tags:
  - 데이터스키마
  - 이용내역
  - 로그데이터
---

# data_usage_history

## 개요
- 원본 파일: `data/data_usage_history.csv`
- 행 수: 6,000건
- 설명: 고객별 월간 이용 내역(데이터·통화·문자 사용량) 로그.
- 핵심 연결 키: customer_id

## 컬럼 정리
| 컬럼 | 의미 | 비고 |
|---|---|---|
| usage_id | 이용내역 식별자 | 기본 키 |
| customer_id | 고객 식별자 | [[02_data/data_customers]]와 연결 |
| usage_month | 이용 월 | YYYY-MM |
| data_usage_mb | 데이터 사용량 | MB 단위(대시보드에서는 1024로 나눠 GB로 환산해서 사용) |
| call_minutes | 통화 시간 | 분 단위 |
| sms_count | 문자 발송 건수 | 건 |

## 연결 관계
- customer_id로 [[02_data/data_customers]]와 연결된다.
- 500명 중 15명은 이용 내역이 아예 없다(매칭되는 usage_history 행 없음) — 평균값 계산 시 결측 처리 필요.
