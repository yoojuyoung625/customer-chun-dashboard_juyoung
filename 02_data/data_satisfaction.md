---
date: 2026-07-21
type: schema
source: "[[data/data_satisfaction.csv]]"
related_data:
  - "[[02_data/data_consultations]]"
  - "[[02_data/data_customers]]"
tags:
  - 데이터스키마
  - 만족도
  - 로그데이터
---

# data_satisfaction

## 개요
- 원본 파일: `data/data_satisfaction.csv`
- 행 수: 1,320건
- 설명: 상담 건별 만족도 조사(CSAT) 결과.
- 핵심 연결 키: consult_id, customer_id

## 컬럼 정리
| 컬럼 | 의미 | 비고 |
|---|---|---|
| consult_id | 상담 식별자 | [[02_data/data_consultations]]와 1:1 연결 |
| customer_id | 고객 식별자 | [[02_data/data_customers]]와 연결 |
| survey_date | 설문 응답일 | YYYY-MM-DD |
| score | CSAT 점수 | 1~5점 (대시보드에서 "CSAT 평균"으로 지칭) |
| comment | 점수에 대응하는 정형 코멘트 | 매우 불만족/불만족/보통/만족/매우 만족 — 자유 서술형이 아니라 score와 1:1 대응하는 정형 라벨로 보임(추정) |

## 연결 관계
- consult_id로 [[02_data/data_consultations]]와 1:1 연결되며, 여기서 channel 등을 가져와 채널별 CSAT를 계산한다.
