# -*- coding: utf-8 -*-
"""
한국관광공사 · 일본 홋카이도 해외여행 상품 구매 패턴 분석 리포트
- 성별 / 연령대 / 한국 방문 경험에 따른 상품 구매 방법 차이 분석
- OTA(항공+숙박) 구매자 심층 프로파일링 → 제휴 마케팅 블로그 타깃팅 인사이트
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import chi2_contingency
import streamlit as st

# ──────────────────────────────────────────────────────────────────────────
# 기본 설정 & 팔레트
# ──────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="홋카이도 여행상품 구매패턴 분석", page_icon="🧭", layout="wide")

CSV_PATH = "hokkaido_purchase.csv"

# 색상: OTA(타깃)는 강조색, 나머지는 톤다운
ACCENT = "#2563EB"        # 타깃(OTA) 강조 파랑
ACCENT_SOFT = "#93C5FD"
NEUTRAL = "#94A3B8"
PALETTE = ["#2563EB", "#0EA5E9", "#14B8A6", "#F59E0B", "#8B5CF6", "#EC4899", "#64748B", "#10B981"]

# 구매 방법 → 짧은 라벨 & 대분류
METHOD_SHORT = {
    "이용하고자 하는 항공사에 직접 예약 및 구매": "항공사 직접예약",
    "OTA에서 항공, 숙박 구입": "OTA (항공+숙박)",
    "여행사 홈페이지에서 항공, 호텔숙박 등 구입(자유, 반자유)": "여행사 홈(자유형)",
    "여행사 카운터에서 패키지 여행을 구입(풀패키지)": "여행사 카운터(패키지)",
    "호텔 홈페이지에서 직접 숙박 예약": "호텔 직접예약",
    "여행사 홈페이지에서 패키지 여행상품을 구입(풀패키지)": "여행사 홈(패키지)",
    "에이전시를 통해서": "에이전시",
    "개인적으로 계획": "개인 계획",
}
METHOD_GROUP = {
    "OTA (항공+숙박)": "온라인 개별예약(DIY)",
    "항공사 직접예약": "온라인 개별예약(DIY)",
    "호텔 직접예약": "온라인 개별예약(DIY)",
    "여행사 홈(자유형)": "여행사 경유",
    "여행사 카운터(패키지)": "여행사 경유",
    "여행사 홈(패키지)": "여행사 경유",
    "에이전시": "여행사 경유",
    "개인 계획": "개인 계획",
}
OTA_LABEL = "OTA (항공+숙박)"
AGE_ORDER = ["20대", "30대", "40대"]
EXP_ORDER = ["0회", "1회", "2회", "3회", "4회", "5회", "6회 이상", "모르겠다"]


@st.cache_data
def load_data():
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
    df = df.rename(columns={"구매 방법": "구매 방법(원본)"})
    df["구매 방법"] = df["구매 방법(원본)"].map(METHOD_SHORT).fillna(df["구매 방법(원본)"])
    df["구매 대분류"] = df["구매 방법"].map(METHOD_GROUP).fillna("기타")
    df["연령대"] = pd.Categorical(df["연령대"], categories=AGE_ORDER, ordered=True)
    df["한국 방문 경험"] = pd.Categorical(df["한국 방문 경험"], categories=EXP_ORDER, ordered=True)
    df["OTA 이용"] = np.where(df["구매 방법"] == OTA_LABEL, "OTA 이용", "비이용")
    return df


SITE_CSV_PATH = "japan_sites.csv"

# 사이트 유형 분류 (제휴 전략용)
SITE_TYPE = {
    "Expedia": "글로벌 OTA", "Booking.com": "글로벌 OTA", "agoda": "글로벌 OTA",
    "Agoda": "글로벌 OTA", "Hotels.com": "글로벌 OTA", "Airbnb": "글로벌 OTA",
    "Skyscanner": "메타서치", "Klook": "액티비티 OTA", "Kkday": "액티비티 OTA",
    "Rakuten travel": "일본 OTA", "Rakuten travel=JTB": "일본 OTA", "Jalan": "일본 OTA",
    "ANA": "항공사 직접", "JAL": "항공사 직접", "기타 항공사 홈페이지": "항공사 직접",
    "HIS": "여행사", "JTB": "여행사", "阪急交通社": "여행사", "Lion Travel": "여행사",
}
SITE_TYPE_COLOR = {
    "글로벌 OTA": "#2563EB", "일본 OTA": "#0EA5E9", "액티비티 OTA": "#14B8A6",
    "메타서치": "#8B5CF6", "항공사 직접": "#F59E0B", "여행사": "#94A3B8",
}
ITEM_ORDER = ["항공", "숙박", "여행상품", "체험 프로그램/입장권"]


@st.cache_data
def load_site_data():
    # japan_sites.csv: 항목, 순위, 사이트, 점유율 (일본만, 사전 파싱 완료)
    df = pd.read_csv(SITE_CSV_PATH, encoding="utf-8-sig")
    df["유형"] = df["사이트"].map(SITE_TYPE).fillna("기타")
    return df


df_all = load_data()
df_site = load_site_data()

# ──────────────────────────────────────────────────────────────────────────
# 사이드바 필터
# ──────────────────────────────────────────────────────────────────────────
st.sidebar.header("🔎 필터")
st.sidebar.caption("아래 조건으로 전체 리포트가 함께 갱신됩니다.")

sel_gender = st.sidebar.multiselect("성별", sorted(df_all["성별"].unique()), default=sorted(df_all["성별"].unique()))
sel_age = st.sidebar.multiselect("연령대", AGE_ORDER, default=AGE_ORDER)
sel_exp = st.sidebar.multiselect("한국 방문 경험", EXP_ORDER, default=EXP_ORDER)

df = df_all[
    df_all["성별"].isin(sel_gender)
    & df_all["연령대"].isin(sel_age)
    & df_all["한국 방문 경험"].isin(sel_exp)
].copy()

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**데이터 출처**  \n한국관광공사 · 일본 홋카이도  \n(해외여행 상품 구매 패턴) 합성데이터  \n(2025-12-02)"
)
st.sidebar.info(
    "⚠️ **표본 특성**\n\n"
    f"총 {len(df_all)}명 중 여성 {(df_all['성별']=='여성').sum()}명 / "
    f"남성 {(df_all['성별']=='남성').sum()}명으로 여성 비중이 큽니다. "
    "남성·소표본 그룹의 비율 수치는 참고용으로 해석하세요."
)

if df.empty:
    st.warning("선택한 조건에 해당하는 응답자가 없습니다. 필터를 조정해 주세요.")
    st.stop()

# ──────────────────────────────────────────────────────────────────────────
# 헤더 & 핵심 지표
# ──────────────────────────────────────────────────────────────────────────
st.title("🧭 홋카이도 여행객 · 해외여행 상품 구매 패턴 분석")
st.markdown(
    "성별 · 연령대 · 한국 방문 경험에 따라 **여행 상품 구매 방법**이 어떻게 달라지는지 분석하고, "
    "**OTA(항공+숙박) 구매자**를 심층 프로파일링하여 제휴 마케팅 블로그의 타깃 전략을 제안합니다."
)

ota_rate = (df["구매 방법"] == OTA_LABEL).mean() * 100
diy_rate = (df["구매 대분류"] == "온라인 개별예약(DIY)").mean() * 100
top_method = df["구매 방법"].value_counts().idxmax()

c1, c2, c3, c4 = st.columns(4)
c1.metric("응답자 수", f"{len(df)}명", help="현재 필터 기준")
c2.metric("최다 구매 방법", top_method, f"{df['구매 방법'].value_counts().max()}명")
c3.metric("🎯 OTA 이용률", f"{ota_rate:.1f}%", help="항공+숙박을 OTA에서 구매하는 비율 (타깃 세그먼트)")
c4.metric("온라인 개별예약(DIY) 비중", f"{diy_rate:.1f}%", help="OTA·항공사·호텔 직접예약 합계")

st.markdown("---")

tab1, tab2, tab3, tab5, tab4 = st.tabs(
    ["📊 전체 구매 방법 현황", "👥 변수별 차이 분석", "🎯 OTA 구매자 심층분석",
     "🛒 제휴처 추천 (일본 OTA)", "💡 마케팅 인사이트"]
)

# ══════════════════════════════════════════════════════════════════════════
# TAB 1 · 전체 구매 방법 현황
# ══════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("여행 상품 구매 방법 분포")

    vc = df["구매 방법"].value_counts().reset_index()
    vc.columns = ["구매 방법", "응답자 수"]
    vc["비율(%)"] = (vc["응답자 수"] / len(df) * 100).round(1)
    vc["color"] = np.where(vc["구매 방법"] == OTA_LABEL, ACCENT, NEUTRAL)

    col_a, col_b = st.columns([3, 2])
    with col_a:
        fig = go.Figure(
            go.Bar(
                x=vc["응답자 수"], y=vc["구매 방법"], orientation="h",
                marker_color=vc["color"],
                text=[f"{n}명 ({p}%)" for n, p in zip(vc["응답자 수"], vc["비율(%)"])],
                textposition="auto",
            )
        )
        fig.update_layout(
            height=420, yaxis=dict(autorange="reversed", title=""), xaxis_title="응답자 수",
            margin=dict(l=10, r=10, t=40, b=10), title="구매 방법별 응답자 수 (파랑=타깃 OTA)",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        grp = df["구매 대분류"].value_counts().reset_index()
        grp.columns = ["구매 대분류", "응답자 수"]
        figd = px.pie(grp, names="구매 대분류", values="응답자 수", hole=0.5,
                      color_discrete_sequence=PALETTE, title="구매 방식 대분류")
        figd.update_traces(textinfo="percent+label")
        figd.update_layout(height=420, margin=dict(l=10, r=10, t=40, b=10), showlegend=False)
        st.plotly_chart(figd, use_container_width=True)

    st.markdown(
        "> **읽는 법** · 홋카이도 여행객의 상품 구매는 크게 **온라인 개별예약(DIY)** — "
        "OTA·항공사·호텔에 직접 예약 — 과 **여행사 경유(자유형·패키지)** 로 나뉩니다. "
        "이 중 우리 블로그의 수익원인 **OTA(항공+숙박) 동시 구매자**가 별도 세그먼트로 존재합니다."
    )
    with st.expander("원본 데이터 미리보기"):
        st.dataframe(df[["구분", "성별", "연령대", "한국 방문 경험", "구매 방법", "구매 대분류"]],
                     use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# TAB 2 · 변수별 차이 분석
# ══════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("변수에 따라 구매 방법이 달라지는가?")
    st.caption(
        "복잡한 8개 방법 대신 **3개 대분류**(🔵 온라인 직접예약 · 🟠 여행사 경유 · 🟣 개인 계획)로 묶어 "
        "각 그룹의 구성비(가로 100% 막대)를 비교합니다. 막대가 파랑 쪽으로 길수록 우리 타깃(OTA 포함)에 가깝습니다."
    )

    GROUP_ORDER = ["온라인 개별예약(DIY)", "여행사 경유", "개인 계획"]
    GROUP_COLOR = {"온라인 개별예약(DIY)": "#2563EB", "여행사 경유": "#F59E0B", "개인 계획": "#A78BFA"}

    def stacked_group(var, order=None):
        ct = pd.crosstab(df[var], df["구매 대분류"], normalize="index") * 100
        if order:
            ct = ct.reindex([o for o in order if o in ct.index])
        for c in GROUP_ORDER:
            if c not in ct.columns:
                ct[c] = 0.0
        ct = ct[GROUP_ORDER].dropna(how="all")
        seg = [f"{s} (n={(df[var]==s).sum()})" for s in ct.index.astype(str)]
        fig = go.Figure()
        for grp in GROUP_ORDER:
            vals = ct[grp].values
            fig.add_bar(
                y=seg, x=vals, orientation="h", name=grp, marker_color=GROUP_COLOR[grp],
                text=[f"{v:.0f}%" if v >= 8 else "" for v in vals],
                textposition="inside", insidetextanchor="middle",
                textfont=dict(color="white", size=13),
                hovertemplate=f"%{{y}}<br>{grp}: %{{x:.1f}}%<extra></extra>",
            )
        fig.update_layout(
            barmode="stack", height=110 + 62 * len(seg), bargap=0.35,
            xaxis=dict(title="구성비(%)", range=[0, 100], ticksuffix="%", showgrid=False),
            yaxis=dict(title="", autorange="reversed"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(size=12)),
            margin=dict(l=10, r=10, t=48, b=10), plot_bgcolor="white",
        )
        return fig

    def chi_note(var):
        ct = pd.crosstab(df[var], df["구매 대분류"])
        if ct.shape[0] < 2 or ct.shape[1] < 2:
            return "표본이 부족해 검정을 생략합니다."
        chi2, p, dof, _ = chi2_contingency(ct)
        verdict = "통계적으로 유의한 차이 (p<0.05)" if p < 0.05 else "뚜렷한 통계적 차이는 약함(경향 참고)"
        return f"🔬 카이제곱={chi2:.1f}, p={p:.3f} → **{verdict}** · 합성·소표본 유의"

    def insight(var):
        g = df.groupby(var, observed=True)
        diy = g["구매 대분류"].apply(lambda s: (s == "온라인 개별예약(DIY)").mean() * 100).dropna()
        ota = g["구매 방법"].apply(lambda s: (s == OTA_LABEL).mean() * 100).dropna()
        if len(diy) < 2:
            return "💡 선택된 그룹이 하나뿐이라 비교 인사이트를 생략합니다."
        hi, lo, ohi = diy.idxmax(), diy.idxmin(), ota.idxmax()
        return (
            f"💡 **{hi}**은(는) 온라인 직접예약(DIY) 비중이 **{diy[hi]:.0f}%** 로 가장 높아 "
            f"**{lo}**({diy[lo]:.0f}%)와 대비됩니다. 타깃인 **OTA 이용률**은 "
            f"**{ohi}** 그룹에서 **{ota[ohi]:.0f}%** 로 가장 높습니다."
        )

    for var, order in [("성별", None), ("연령대", AGE_ORDER), ("한국 방문 경험", EXP_ORDER)]:
        st.markdown(f"#### {var}별 구매 방식 구성")
        st.plotly_chart(stacked_group(var, order), use_container_width=True)
        st.success(insight(var))
        st.caption(chi_note(var))
        st.markdown(" ")

    st.info(
        "**요약** · 성별·연령대에 따라 구매 방식 구성이 달라지지만, 표본이 작고 여성 편중이 커 "
        "통계적 유의성보다는 **경향(방향성)** 으로 해석하는 것이 안전합니다. "
        "특히 **한국 방문 경험**은 OTA 이용률과 비선형 관계를 보여(다음 탭 참고) 가장 주목할 변수입니다."
    )

# ══════════════════════════════════════════════════════════════════════════
# TAB 3 · OTA 구매자 심층 분석
# ══════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("🎯 OTA(항공+숙박) 구매자는 누구인가")
    st.caption(
        "각 세그먼트의 **OTA 침투율(=그 그룹 중 OTA 이용 비율)** 과 "
        "**리프트 지수(전체 평균 대비 배수)** 를 함께 봅니다."
    )

    base_rate = (df_all["구매 방법"] == OTA_LABEL).mean() * 100  # 전체 기준선

    def penetration(var, order=None):
        g = df.groupby(var, observed=True).agg(
            응답자수=("구매 방법", "size"),
            OTA수=("구매 방법", lambda s: (s == OTA_LABEL).sum()),
        ).reset_index()
        g["OTA 침투율(%)"] = (g["OTA수"] / g["응답자수"] * 100).round(1)
        g["리프트(배)"] = (g["OTA 침투율(%)"] / base_rate).round(2)
        if order:
            g[var] = pd.Categorical(g[var], categories=order, ordered=True)
            g = g.sort_values(var)
        return g

    st.markdown(f"**전체 OTA 기준 침투율: `{base_rate:.1f}%`** — 아래 막대가 이 선보다 높으면 타깃 우위 세그먼트")

    for var, order in [("성별", None), ("연령대", AGE_ORDER), ("한국 방문 경험", EXP_ORDER)]:
        g = penetration(var, order)
        colL, colR = st.columns([3, 2])
        with colL:
            fig = go.Figure()
            fig.add_bar(
                x=g[var].astype(str), y=g["OTA 침투율(%)"],
                marker_color=np.where(g["OTA 침투율(%)"] >= base_rate, ACCENT, ACCENT_SOFT),
                text=[f"{r}%<br>(n={n})" for r, n in zip(g["OTA 침투율(%)"], g["응답자수"])],
                textposition="outside",
            )
            fig.add_hline(y=base_rate, line_dash="dash", line_color="#EF4444",
                          annotation_text=f"전체 평균 {base_rate:.1f}%", annotation_position="top left")
            fig.update_layout(height=360, title=f"{var}별 OTA 침투율", yaxis_title="OTA 침투율(%)",
                              margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig, use_container_width=True)
        with colR:
            st.markdown(f"**{var}별 상세**")
            st.dataframe(g[[var, "응답자수", "OTA수", "OTA 침투율(%)", "리프트(배)"]],
                         use_container_width=True, hide_index=True)
        st.markdown(" ")

    st.markdown("#### OTA 구매자 내부 구성 (누가 OTA를 쓰는가)")
    ota_df = df[df["구매 방법"] == OTA_LABEL]
    if len(ota_df) > 0:
        cc1, cc2, cc3 = st.columns(3)
        for col, var in [(cc1, "성별"), (cc2, "연령대"), (cc3, "한국 방문 경험")]:
            comp = ota_df[var].value_counts()
            comp = comp[comp > 0].reset_index()
            comp.columns = [var, "명"]
            figp = px.pie(comp, names=var, values="명", hole=0.45, color_discrete_sequence=PALETTE)
            figp.update_traces(textinfo="percent+label")
            figp.update_layout(height=280, title=f"OTA 이용자의 {var} 구성",
                               margin=dict(l=5, r=5, t=40, b=5), showlegend=False)
            col.plotly_chart(figp, use_container_width=True)
    else:
        st.warning("현재 필터에 OTA 이용자가 없습니다.")

# ══════════════════════════════════════════════════════════════════════════
# TAB 5 · 제휴처 추천 (일본인이 실제 쓰는 온라인 구매 사이트)
# ══════════════════════════════════════════════════════════════════════════
with tab5:
    st.subheader("🛒 일본인이 실제로 이용하는 온라인 구매 사이트")
    st.caption(
        "한국관광공사 '국가별 해외여행 온라인 구매사이트'(일본, 2021) 데이터를 결합했습니다. "
        "우리 블로그의 수익 모델인 **항공·숙박 제휴**에 가장 유리한 사이트를 찾습니다."
    )

    # 항공 + 숙박에 집중 (블로그 수익 모델과 직결)
    focus = df_site[df_site["항목"].isin(["항공", "숙박"])].copy()

    colL, colR = st.columns(2)
    for col, item in [(colL, "숙박"), (colR, "항공")]:
        d = df_site[df_site["항목"] == item].sort_values("점유율")
        fig = go.Figure(go.Bar(
            x=d["점유율"], y=d["사이트"], orientation="h",
            marker_color=[SITE_TYPE_COLOR.get(t, "#CBD5E1") for t in d["유형"]],
            text=[f"{v:.1f}%" for v in d["점유율"]], textposition="auto",
        ))
        fig.update_layout(height=320, title=f"일본 · {item} 온라인 구매 사이트 TOP5",
                          xaxis_title="이용률(%)", yaxis_title="",
                          margin=dict(l=10, r=10, t=40, b=10))
        col.plotly_chart(fig, use_container_width=True)

    # 유형 범례
    st.markdown(
        " · ".join(f"<span style='color:{c};font-weight:700'>■</span> {t}"
                   for t, c in SITE_TYPE_COLOR.items()),
        unsafe_allow_html=True,
    )

    # 항공+숙박 양쪽 커버리지 → 제휴 우선순위
    st.markdown("### 🥇 항공·숙박 동시 커버 = 제휴 1순위 후보")
    piv = (focus.pivot_table(index="사이트", columns="항목", values="점유율", aggfunc="max"))
    piv["유형"] = piv.index.map(lambda s: SITE_TYPE.get(s, "기타"))
    piv["양쪽 합계"] = piv[["항공", "숙박"]].sum(axis=1, min_count=1)
    piv["커버"] = piv[["항공", "숙박"]].notna().sum(axis=1)
    piv = piv.sort_values(["커버", "양쪽 합계"], ascending=False)
    show = piv.reset_index()[["사이트", "유형", "숙박", "항공", "양쪽 합계", "커버"]]
    show = show.rename(columns={"숙박": "숙박 이용률(%)", "항공": "항공 이용률(%)", "커버": "커버 항목수"})
    st.dataframe(
        show.style.format({"숙박 이용률(%)": "{:.1f}", "항공 이용률(%)": "{:.1f}", "양쪽 합계": "{:.1f}"},
                          na_rep="—"),
        use_container_width=True, hide_index=True,
    )

    # Expedia 등 핵심 수치 자동 추출
    def share(item, site):
        v = df_site[(df_site["항목"] == item) & (df_site["사이트"] == site)]["점유율"]
        return v.iloc[0] if len(v) else None

    exp_stay, exp_air = share("숙박", "Expedia"), share("항공", "Expedia")

    st.success(f"""
**핵심 결론 — 제휴 프로그램 우선순위**

1. **🥇 Expedia** — 숙박 **{exp_stay:.1f}%(1위)** + 항공 **{exp_air:.1f}%(2위)**.
   항공·숙박 모두 상위권인 **유일한 순수 글로벌 OTA**. 우리 블로그 수익 모델과 가장 잘 맞는 **1순위 제휴처**.
2. **🥈 Booking.com · Agoda** — 숙박에 강함(각 18.9% / 12.5%)이나 항공은 약함.
   → **호텔 예약 콘텐츠 전용** 보조 제휴처로 배치.
3. **🥉 Rakuten Travel** — 항공·숙박·여행상품·체험 **4개 항목 모두 등장**하는 유일한 사이트.
   일본 현지 신뢰도가 높아, 일본어권 독자에게 **친숙함 소구용**으로 병행 추천.
4. ⚠️ **항공 1위는 ANA(항공사 직접, 14.8%)** — OTA가 아님. 이는 앞선 분석의
   *'헤비 트래블러는 항공사에 직접 예약'* 경향과 일치. 항공 제휴는 **Expedia로 집중**하는 편이 효율적.
""")

    with st.expander("일본 전체 항목(여행상품·체험 포함) 원본 보기"):
        st.dataframe(
            df_site[["항목", "순위", "사이트", "점유율", "유형"]]
            .assign(항목=lambda x: pd.Categorical(x["항목"], ITEM_ORDER, ordered=True))
            .sort_values(["항목", "순위"]),
            use_container_width=True, hide_index=True,
        )


# ══════════════════════════════════════════════════════════════════════════
# TAB 4 · 마케팅 인사이트
# ══════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("💡 제휴 마케팅 블로그 타깃 전략")

    A = df_all  # 안정적 인사이트는 전체(필터 무관) 기준
    def rate(mask):
        return (A[mask]["구매 방법"] == OTA_LABEL).mean() * 100
    base = (A["구매 방법"] == OTA_LABEL).mean() * 100

    r_female = rate(A["성별"] == "여성")
    r_40 = rate(A["연령대"] == "40대")
    r_20 = rate(A["연령대"] == "20대")
    r_exp_low = rate(A["한국 방문 경험"].isin(["0회", "1회", "2회", "3회"]))
    r_exp_high = rate(A["한국 방문 경험"].isin(["4회", "5회", "6회 이상"]))
    r_exp3 = rate(A["한국 방문 경험"] == "3회")

    st.markdown(
        f"전체 홋카이도 여행객 중 **OTA(항공+숙박) 동시 구매자는 {base:.1f}%**. "
        "아래는 이 세그먼트로 트래픽·전환을 집중하기 위한 데이터 기반 제언입니다."
    )

    st.markdown("### ✅ 1순위 타깃: 명확한 우위 세그먼트")
    st.markdown(f"""
| 세그먼트 | OTA 침투율 | 전체 대비 | 시사점 |
|---|---|---|---|
| **여성** | **{r_female:.1f}%** | {r_female/base:.1f}배 | 남성(5.3%) 대비 압도적. 콘텐츠 톤·비주얼을 여성 여행객 중심으로 |
| **40대** | **{r_40:.1f}%** | {r_40/base:.1f}배 | 구매력·자유여행 니즈 높음. 항공+숙박 묶음 예약 가이드에 반응 |
| **20대** | **{r_20:.1f}%** | {r_20/base:.1f}배 | 가성비·앱 예약 친숙. 프로모션·쿠폰 소구 |
| **한국 방문 3회** | **{r_exp3:.1f}%** | {r_exp3/base:.1f}배 | 재방문 관심 + 아직 여행사 의존 낮은 '골든존' |
""")

    st.markdown("### 🔑 핵심 인사이트: '한국 방문 경험'의 역U자 패턴")
    exp_g = (A.groupby("한국 방문 경험", observed=True)["구매 방법"]
             .apply(lambda s: (s == OTA_LABEL).mean() * 100).reindex(EXP_ORDER).dropna())
    fig = go.Figure(go.Scatter(x=exp_g.index.astype(str), y=exp_g.values, mode="lines+markers",
                               line=dict(color=ACCENT, width=3), marker=dict(size=9)))
    fig.add_hline(y=base, line_dash="dash", line_color="#EF4444", annotation_text=f"평균 {base:.1f}%")
    fig.update_layout(height=320, title="한국 방문 경험별 OTA 침투율", yaxis_title="OTA 침투율(%)",
                      margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"""
- **방문 경험 0~3회(입문·성장기) 여행객의 OTA 이용률이 {r_exp_low:.1f}%** 로,
  **4회 이상 헤비 리피터({r_exp_high:.1f}%)** 보다 뚜렷이 높습니다.
- 즉 여행 경험이 아주 많은 사람은 **항공사·호텔에 직접 예약**하며 OTA를 이탈하는 경향이 보입니다.
- 👉 **블로그 타깃은 '경험 많은 헤비 트래블러'가 아니라, 아직 예약 습관이 굳지 않은
  0~3회 방문객'** 입니다. 이들에게 "OTA로 항공+숙박 한 번에 싸게 묶는 법"을 각인시키면
  향후 반복 구매까지 선점할 수 있습니다.
""")

    st.markdown("### 🧭 실행 제언")
    st.markdown("""
1. **페르소나 고정** — "홋카이도 자유여행을 준비하는 20·40대 여성, 여행 경험 0~3회".
   블로그 헤드라인·썸네일·예시를 이 인물 기준으로 통일.
2. **콘텐츠 = 항공+숙박 묶음 예약 가이드** — 우리 수익 모델(OTA 항공·숙박 제휴)과 정확히 일치하는
   "신치토세 항공권 + 삿포로 호텔 한 번에 예약하기" 형식이 전환율 최상.
   제휴 링크는 항공·숙박 모두 상위권인 **Expedia를 메인**, Booking.com·Agoda(숙박)와
   Rakuten Travel(현지 신뢰도)을 보조로 (→ '제휴처 추천' 탭 참고).
3. **패키지 이탈 유도** — 데이터상 여행사 경유 비중도 큼. "패키지보다 OTA 자유예약이 저렴한 이유"
   비교 콘텐츠로 패키지 검토층을 OTA 링크로 전환.
4. **입문자 온보딩** — OTA 앱 사용법·환불규정·수하물 등 초보 친화 콘텐츠로 0~3회 방문객의
   진입장벽을 낮춰 제휴 클릭을 유도.
5. **시즌·목적지 특화** — 홋카이도(겨울 스노우 / 여름 라벤더) 시즌 키워드로 검색 유입을 확보한 뒤
   OTA 제휴 링크로 연결.
""")

    st.warning(
        "📌 **해석 유의** · 본 데이터는 합성 데이터이며 총 144명(여성 편중)의 소표본입니다. "
        "위 수치는 절대적 결론이 아니라 **가설 수립·A/B 테스트의 출발점**으로 활용하세요."
    )

st.markdown("---")
st.caption("데이터: 한국관광공사 · 일본 홋카이도 해외여행 상품 구매 패턴 합성데이터(2025-12-02) · 분석: Streamlit + pandas")
