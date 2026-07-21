# INDEX — 고객 이탈 원인 진단 대시보드

## 배포 링크
- GitHub: https://github.com/yoojuyoung625/customer-chun-dashboard_juyoung
- Streamlit: https://customer-chun-dashboard-juyoung.streamlit.app

## 데이터
- [[02_data/data_customers]] — 고객 마스터 (500명, churn_yn 타깃 변수)
- [[02_data/data_usage_history]] — 월간 이용내역 로그 (6,000건)
- [[02_data/data_consultations]] — 상담 이력 로그 (1,320건)
- [[02_data/data_satisfaction]] — 상담 만족도(CSAT) (1,320건)
- [[02_data/data_voc]] — VOC 로그 (1,307건)

## 인사이트
- [[04_insights/대시보드-개요]] — 6개 차트 요약, 핵심 패턴, 배포 링크 (confidence: 높음)

## 코드
- `app.py` — Streamlit 대시보드 진입점 (6개 차트 + 상단 지표 3개)
- `charts/01_plotly_voc이탈비교.py` ~ `charts/06_plotly_가입기간이용량산점도.py` — 개별 차트 스크립트
- `requirements.txt` — pandas, matplotlib, plotly, streamlit
