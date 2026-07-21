---
date: 2026-07-21
type: schema
source: "[[data/data_customers.csv]]"
related_data:
  - "[[02_data/data_usage_history]]"
  - "[[02_data/data_consultations]]"
  - "[[02_data/data_satisfaction]]"
  - "[[02_data/data_voc]]"
tags:
  - 데이터스키마
  - 고객
  - 마스터데이터
---

# data_customers

## 개요
- 원본 파일: `data/data_customers.csv`
- 행 수: 500명
- 설명: 고객 마스터 데이터. 가입 속성, 요금제, 이탈 여부(타깃 변수)를 담는다.
- 핵심 연결 키: customer_id

## 컬럼 정리
| 컬럼 | 의미 | 비고 |
|---|---|---|
| customer_id | 고객 식별자 | 기본 키 |
| join_date | 가입일 | YYYY-MM-DD |
| age_group | 연령대 | 10대, 20대, 30대, 40대, 50대+ |
| gender | 성별 | F, M |
| region | 지역 | 서울, 인천, 경기, 부산, 대구, 기타 |
| plan_type | 요금제 | 데이터무제한, 청소년요금제, 5G스탠다드, 5G프리미엄, LTE베이직 |
| monthly_fee | 월 요금 | 원 단위 |
| tenure_months | 가입기간(개월) | ⚠ 기준일이 불명확함 — join_date 기준 2024-12-31까지 개월 수와 평균 11개월 차이 남(대시보드에서는 join_date로 직접 재계산해서 씀) |
| churn_yn | 이탈 여부 | Y/N — 이 프로젝트의 핵심 타깃 변수 |

## 연결 관계
- customer_id는 [[02_data/data_usage_history]], [[02_data/data_consultations]], [[02_data/data_satisfaction]], [[02_data/data_voc]] 전부와 연결된다.
- 전체 500명 중 이탈(churn_yn=Y) 고객은 37명, 전체 이탈율 7.4%.
