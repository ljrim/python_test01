# 🧭 홋카이도 여행객 · 해외여행 상품 구매 패턴 분석

한국관광공사 합성데이터로 **일본 홋카이도 여행객의 해외여행 상품 구매 패턴**을 분석하는 Streamlit 대시보드입니다.
성별·연령대·한국 방문 경험별 구매 방법 차이를 살펴보고, **OTA(항공+숙박) 구매자**를 심층 프로파일링하여
제휴 마케팅 블로그의 타깃 전략과 제휴처(일본 OTA)를 제안합니다.

## 📊 구성 (5개 탭)

| 탭 | 내용 |
|---|---|
| 📊 전체 구매 방법 현황 | 8개 구매 방법 분포 + 3개 대분류 도넛 |
| 👥 변수별 차이 분석 | 성별·연령·한국경험별 구성비 + 카이제곱 검정 + 자동 인사이트 |
| 🎯 OTA 구매자 심층분석 | 세그먼트별 OTA 침투율·리프트 지수 |
| 🛒 제휴처 추천 (일본 OTA) | 일본 항공·숙박 사이트 점유율 → 제휴 우선순위 |
| 💡 마케팅 인사이트 | 타깃 우선순위 + 실행 제언 |

## 🗂 필요 파일

```
python02/
├── app.py                    # 메인 앱
├── requirements.txt          # 의존성
├── .streamlit/config.toml    # 테마 설정
├── hokkaido_purchase.csv     # 구매패턴 데이터 (UTF-8, 144행)
└── japan_sites.csv           # 일본 온라인 구매사이트 (UTF-8, 20행)
```

> ⚠️ 두 개의 CSV 파일은 앱이 직접 읽으므로 **반드시 저장소에 함께 커밋**해야 합니다.
> 원본 한국관광공사 CP949 CSV는 UTF-8로 변환·경량화하여 위 파일로 정리했습니다.
> (일본 사이트 데이터는 21개국 420행 중 일본 20행만 추출 → 용량 96% 감소)

## 💻 로컬 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```
→ 브라우저에서 http://localhost:8501 접속

## ☁️ Streamlit Community Cloud 배포

1. **GitHub 저장소 생성** 후 이 폴더의 모든 파일(CSV 2개 포함)을 push
   ```bash
   git init
   git add .
   git commit -m "홋카이도 구매패턴 분석 대시보드"
   git branch -M main
   git remote add origin https://github.com/<사용자명>/<저장소명>.git
   git push -u origin main
   ```
2. https://share.streamlit.io 접속 → GitHub 계정 연결
3. **New app** 클릭 후 설정
   - Repository: 방금 만든 저장소
   - Branch: `main`
   - Main file path: `app.py`
   - (Advanced) Python version: **3.11** 권장
4. **Deploy** → 몇 분 후 `https://<앱이름>.streamlit.app` 주소로 공개됩니다.

## 📌 데이터 출처

한국관광공사
- 일본 홋카이도(해외여행 상품 구매 패턴) 합성데이터 (2025-12-02)
- 국가별 해외여행 활용 온라인 구매사이트 (2025-09-01, 일본 2021년 기준)

> 합성 데이터이며 총 144명(여성 편중) 소표본입니다. 수치는 확정 결론이 아니라 가설·A/B 테스트의 출발점으로 활용하세요.
