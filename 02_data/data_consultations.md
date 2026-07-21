---
date: 2026-07-21
type: schema
source: "[[data/data_consultations.csv]]"
related_data:
  - "[[02_data/data_customers]]"
  - "[[02_data/data_satisfaction]]"
tags:
  - 데이터스키마
  - 상담
  - 로그데이터
---

# data_consultations

## 개요
- 원본 파일: `data/data_consultations.csv`
- 행 수: 1,320건
- 설명: 고객센터 상담 이력 로그(채널, 처리시간, 재문의 여부 등).
- 핵심 연결 키: consult_id, customer_id

## 컬럼 정리
| 컬럼 | 의미 | 비고 |
|---|---|---|
| consult_id | 상담 식별자 | 기본 키, [[02_data/data_satisfaction]]과 1:1 연결 |
| customer_id | 고객 식별자 | [[02_data/data_customers]]와 연결 |
| consult_date | 상담일 | YYYY-MM-DD |
| channel | 상담 채널 | 앱, 전화, 매장, 홈페이지 |
| agent_id | 상담원 식별자 | |
| category | 상담 유형 | 요금문의, 상품문의, 서비스불만, 기타, 결제오류 |
| handle_time_min | 처리 시간 | 분 단위 |
| resolved_yn | 해결 여부 | Y/N |
| is_repeat | 재문의 여부 | Y/N — "재문의율" 계산의 기준 컬럼(주의: `is_recontact`라는 이름으로 착각하기 쉬우나 실제 컬럼명은 is_repeat) |

## 연결 관계
- consult_id로 [[02_data/data_satisfaction]]과 1:1 연결(두 파일 모두 1,320행으로 건수 일치).
- customer_id로 [[02_data/data_customers]]와 연결.
