---
date: 2026-07-21
type: schema
source: "[[data/data_voc.csv]]"
related_data:
  - "[[02_data/data_customers]]"
tags:
  - 데이터스키마
  - VOC
  - 로그데이터
---

# data_voc

## 개요
- 원본 파일: `data/data_voc.csv`
- 행 수: 1,307건
- 설명: VOC(고객의 소리) 로그. category·sentiment로 분류된 고객 피드백.
- 핵심 연결 키: customer_id

## 컬럼 정리
| 컬럼 | 의미 | 비고 |
|---|---|---|
| voc_id | VOC 식별자 | 기본 키 |
| customer_id | 고객 식별자 | [[02_data/data_customers]]와 연결 |
| voc_date | VOC 접수일 | YYYY-MM-DD |
| channel | 접수 채널 | 앱, 매장, 전화, 홈페이지 |
| category | VOC 유형 | 요금문의, 서비스불만, 상품문의, 결제오류, 기타 (⚠ "해지관련" 유형은 존재하지 않음) |
| sentiment | 감성 | 중립, 부정, 긍정 |
| content_summary | 내용 요약 | ⚠ 실제 자유 서술형 텍스트가 아니라 `"{category} 관련 {sentiment} 피드백"` 형태의 정형 템플릿 문자열로 보임(추정) — 실제 VOC 원문 상세 내용은 이 컬럼만으로는 알 수 없음 |

## 연결 관계
- customer_id로 [[02_data/data_customers]]와 연결해 "특정 VOC 유형을 남긴 고객의 이탈율" 등을 계산할 수 있다(예: [[04_insights/대시보드-개요]] ① 차트).

## 주의
- category='서비스불만' & sentiment='부정' 기준으로 대시보드 ①번 차트를 계산함. "해지관련"이라는 카테고리는 데이터에 없으므로 혼동하지 않도록 함.
