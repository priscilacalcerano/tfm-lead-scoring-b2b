"""Raona Lead Scoring -- B2B Prospecting Intelligence

Streamlit app con estetica Anthropic (ivory, serif headings, minimalista).
Dos paginas: Dashboard y Lead Scorer.

Uso:
    streamlit run streamlit_app.py
"""
import os
import pickle
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# --- Page config ---
st.set_page_config(
    page_title="Raona Lead Scoring",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={},
)

# --- Anthropic-inspired CSS ---
st.markdown("""
<style>
    /* Hide deploy button, hamburger, footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    [data-testid="stToolbar"] {display: none;}

    /* Global background and typography */
    .stApp {
        background-color: #FAFAF7;
    }
    html, body, [class*="css"] {
        font-family: 'Tiempos Text', 'Georgia', 'Times New Roman', serif;
        color: #141413;
    }

    /* Headings: serif, tight */
    h1 {
        font-family: 'Copernicus', 'Georgia', serif !important;
        font-weight: 700 !important;
        color: #141413 !important;
        letter-spacing: -0.02em !important;
        font-size: 2.4rem !important;
        line-height: 1.1 !important;
        margin-bottom: 0.3rem !important;
    }
    h2 {
        font-family: 'Copernicus', 'Georgia', serif !important;
        font-weight: 600 !important;
        color: #141413 !important;
        font-size: 1.5rem !important;
        letter-spacing: -0.01em !important;
        margin-top: 2rem !important;
    }
    h3 {
        font-family: 'Copernicus', 'Georgia', serif !important;
        font-weight: 600 !important;
        color: #141413 !important;
        font-size: 1.15rem !important;
    }

    /* Body text */
    p, .stMarkdown, label {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif !important;
        color: #3D3D3A !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
    }

    /* Subtitle / lead text */
    .lead-text {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: #6B6B66;
        font-size: 1.1rem;
        line-height: 1.6;
        margin-bottom: 2.5rem;
        max-width: 700px;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E8E8E3;
        border-radius: 8px;
        padding: 1.2rem 1rem;
    }
    [data-testid="stMetricLabel"] {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        color: #8B8B85 !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Copernicus', 'Georgia', serif !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #141413 !important;
    }
    [data-testid="stMetricDelta"] {
        font-family: -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-size: 0.8rem !important;
    }

    /* Dividers */
    hr {
        border: none;
        border-top: 1px solid #E8E8E3;
        margin: 2rem 0;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #F0F0EB;
        border-right: 1px solid #E8E8E3;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
        font-size: 1.1rem !important;
    }

    /* Form styling */
    .stForm {
        background: #FFFFFF;
        border: 1px solid #E8E8E3;
        border-radius: 8px;
        padding: 1.5rem;
    }

    /* Button -- Nuclio gold accent */
    .stFormSubmitButton button {
        background-color: #FFC630 !important;
        color: #141413 !important;
        border: none !important;
        border-radius: 6px !important;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
        padding: 0.6rem 2rem !important;
        transition: background-color 0.2s !important;
    }
    .stFormSubmitButton button:hover {
        background-color: #EDB82D !important;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid #E8E8E3;
        border-radius: 8px;
    }

    /* Radio buttons in sidebar */
    .stRadio label {
        font-family: -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Override Streamlit red/green delta colors */
    [data-testid="stMetricDelta"] svg {
        display: none;
    }
    [data-testid="stMetricDelta"] > div {
        color: #3D3D3A !important;
    }

    /* Remove red from any Streamlit element */
    .stAlert, [data-baseweb="notification"] {
        background-color: #FFF9E6 !important;
        border-color: #FFC630 !important;
        color: #141413 !important;
    }

    /* Top border accent */
    .top-accent {
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, #FFC630 0%, #141413 50%, #E8E8E3 100%);
        margin-bottom: 2rem;
    }

    /* Section label */
    .section-label {
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #8B8B85;
        margin-bottom: 0.5rem;
    }

    /* Recommendation cards */
    .rec-card {
        background: #FFFFFF;
        border: 1px solid #E8E8E3;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 0.5rem 0;
    }
    .rec-card-high {
        border-left: 4px solid #FFC630;
    }
    .rec-card-mid {
        border-left: 4px solid #141413;
    }
    .rec-card-low {
        border-left: 4px solid #D4D4CF;
    }

    /* Slider -- gold accent (multiple selectors for compatibility) */
    .stSlider [data-baseweb="slider"] [role="slider"] {
        background-color: #FFC630 !important;
        border-color: #FFC630 !important;
    }
    .stSlider [data-baseweb="slider"] div[data-testid="stTickBar"] {
        background: #FFC630 !important;
    }
    div[data-baseweb="slider"] > div > div > div[role="progressbar"] > div {
        background-color: #FFC630 !important;
    }
    /* Slider thumb and track */
    .stSlider div[role="slider"] {
        background: #FFC630 !important;
    }
    .stSlider [data-testid="stThumbValue"] {
        color: #141413 !important;
    }
    /* Slider filled track */
    .stSlider div[data-baseweb="slider"] div div div {
        background-color: #FFC630 !important;
    }
    /* Force override on ALL slider inner colored divs */
    [data-testid="stSlider"] div[role="slider"] {
        background: #FFC630 !important;
        border-color: #EDB82D !important;
    }
    [data-testid="stSlider"] div[data-testid="stTickBar"] > div {
        background: #FFC630 !important;
    }

    /* Selectbox / input focus */
    [data-baseweb="select"] [data-baseweb="input"]:focus-within,
    .stNumberInput input:focus {
        border-color: #FFC630 !important;
        box-shadow: 0 0 0 1px #FFC630 !important;
    }

    /* Checkbox gold (multiple selectors) */
    .stCheckbox [data-testid="stCheckbox"] input:checked + div {
        background-color: #FFC630 !important;
        border-color: #FFC630 !important;
    }
    .stCheckbox label span[data-testid="stCheckbox"] {
        color: #FFC630 !important;
    }
    /* Force checkbox checked state */
    input[type="checkbox"]:checked + label > span:first-child,
    [data-testid="stCheckbox"] > label > div:first-child {
        --checkbox-checked-bg: #FFC630 !important;
    }
    .st-emotion-cache-1inwz65,
    .st-emotion-cache-16txtl3 {
        color: #FFC630 !important;
    }
    /* Broadest checkbox override */
    [data-testid="stCheckbox"] svg {
        fill: #FFC630 !important;
        color: #FFC630 !important;
    }
    [data-testid="stCheckbox"] [aria-checked="true"] {
        background-color: #FFC630 !important;
        border-color: #FFC630 !important;
    }
    /* Override Streamlit's primary color everywhere */
    :root {
        --primary-color: #FFC630 !important;
    }

    /* Override any red elements from Streamlit */
    .element-container .stException,
    .stError {
        background-color: #FFF9E6 !important;
        border-color: #FFC630 !important;
    }

    /* Hide fullscreen buttons on charts */
    button[title="View fullscreen"] {display: none;}

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 1px solid #E8E8E3;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.03em !important;
        color: #8B8B85 !important;
        padding: 0.8rem 1.5rem !important;
        border: none !important;
        background: transparent !important;
    }
    .stTabs [aria-selected="true"] {
        color: #141413 !important;
        border-bottom: 3px solid #FFC630 !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #FFC630 !important;
    }
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# --- Plotly theme matching Anthropic ---
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="-apple-system, BlinkMacSystemFont, sans-serif", color="#3D3D3A", size=12),
    margin=dict(t=20, b=40, l=50, r=20),
    colorway=["#141413", "#FFC630", "#6B6B66", "#B5B5AE", "#D4D4CF"],
    xaxis=dict(gridcolor="#E8E8E3", linecolor="#E8E8E3"),
    yaxis=dict(gridcolor="#E8E8E3", linecolor="#E8E8E3"),
)

ACCENT_DARK = "#141413"
ACCENT_MID = "#6B6B66"
ACCENT_LIGHT = "#B5B5AE"
ACCENT_GOLD = "#FFC630"
ACCENT_GOLD_DARK = "#EDB82D"

# --- Load data and models ---
APP_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(APP_DIR, "models")
DATA_DIR = os.path.join(APP_DIR, "data")


@st.cache_data
def load_data():
    df = pd.read_parquet(os.path.join(DATA_DIR, "sample_contacts.parquet"))
    daily = pd.read_parquet(os.path.join(DATA_DIR, "daily_analytics_ES.parquet"))
    return df, daily


@st.cache_resource
def load_models():
    with open(os.path.join(MODEL_DIR, "preprocessor.pkl"), "rb") as f:
        preprocessor = pickle.load(f)
    with open(os.path.join(MODEL_DIR, "lead_scorer.pkl"), "rb") as f:
        lead_scorer = pickle.load(f)
    with open(os.path.join(MODEL_DIR, "clustering.pkl"), "rb") as f:
        clustering = pickle.load(f)
    with open(os.path.join(MODEL_DIR, "feature_names.pkl"), "rb") as f:
        feature_names = pickle.load(f)
    return preprocessor, lead_scorer, clustering, feature_names


df, daily = load_data()
preprocessor, lead_scorer, clustering_bundle, FEATURE_COLS = load_models()

# Global stats (used across pages)
TOTAL_CONTACTS = len(df)
TOTAL_REPLIED = int(df["target_replied"].sum())
GLOBAL_REPLY_RATE = TOTAL_REPLIED / TOTAL_CONTACTS * 100

# Cluster profile labels
CLUSTER_NAMES = {
    0: "Financial Services\nSenior profiles",
    1: "Telecom & Tech\nDirector level",
    2: "Large Telecom\nHigh engagement",
    3: "Enterprise / Gov\n6K+ employees",
    4: "Junior profiles\nGov & Education",
    5: "Industrial SMEs\nLow response",
    6: "Pharma & Wellness\nTop converters",
}

# --- Navigation via tabs ---
tab_dashboard, tab_scorer = st.tabs(["Dashboard", "Lead Scorer"])


# =====================================================
# PAGE 1: DASHBOARD
# =====================================================
with tab_dashboard:
    st.markdown('<div class="top-accent"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Overview</div>', unsafe_allow_html=True)
    st.title("B2B Prospecting Intelligence")
    st.markdown(
        '<div class="lead-text">'
        "An analysis of 10,946 outreach contacts reveals patterns in who responds, "
        "through which channel, and when. The lead scoring model identifies high-potential "
        "leads with 3.6x lift over random selection."
        "</div>",
        unsafe_allow_html=True,
    )

    # --- KPIs ---
    ln_replied = int(df["target_replied_linkedin"].sum())
    em_replied = int(df["target_replied_email"].sum())

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total contacts", f"{TOTAL_CONTACTS:,}")
    col2.metric("Replied", f"{TOTAL_REPLIED:,}")
    col3.metric("Reply rate", f"{GLOBAL_REPLY_RATE:.1f}%")
    col4.metric("LinkedIn", f"{ln_replied:,}")
    col5.metric("Email", f"{em_replied:,}")

    st.markdown("---")

    # --- Row 1: Score distribution + Lift ---
    r1c1, r1c2 = st.columns(2)

    with r1c1:
        st.markdown('<div class="section-label">Distribution</div>', unsafe_allow_html=True)
        st.markdown("### Lead score distribution")
        fig = go.Figure()
        neg_scores = df[df["target_replied"] == 0]["lead_score"]
        pos_scores = df[df["target_replied"] == 1]["lead_score"]
        fig.add_trace(go.Histogram(
            x=neg_scores, nbinsx=50, name="Did not reply",
            marker_color=ACCENT_LIGHT, opacity=0.7,
        ))
        fig.add_trace(go.Histogram(
            x=pos_scores, nbinsx=50, name="Replied",
            marker_color=ACCENT_GOLD, opacity=0.9,
        ))
        fig.update_layout(**PLOTLY_LAYOUT, barmode="overlay", height=340,
                          legend=dict(orientation="h", yanchor="top", y=1.12, x=0))
        fig.update_xaxes(title_text="Lead score")
        fig.update_yaxes(title_text="Count")
        st.plotly_chart(fig, use_container_width=True)

    with r1c2:
        st.markdown('<div class="section-label">Model performance</div>', unsafe_allow_html=True)
        st.markdown("### Cumulative gains")
        sorted_idx = np.argsort(-df["lead_score"].values)
        y_sorted = df["target_replied"].values[sorted_idx]
        n = len(y_sorted)
        cum_pos = np.cumsum(y_sorted)
        total_pos = y_sorted.sum()
        pct_x = np.arange(1, n + 1) / n * 100
        pct_y = cum_pos / total_pos * 100

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=pct_x, y=pct_y, mode="lines", name="Model",
            line=dict(color=ACCENT_GOLD, width=2.5),
        ))
        fig.add_trace(go.Scatter(
            x=[0, 100], y=[0, 100], mode="lines", name="Random",
            line=dict(color=ACCENT_LIGHT, width=1.5, dash="dash"),
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=340,
                          legend=dict(orientation="h", yanchor="top", y=1.12, x=0))
        fig.update_xaxes(title_text="% of contacts (ranked by score)")
        fig.update_yaxes(title_text="% of replies captured")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # --- Row 2: Channel + Timing ---
    r2c1, r2c2 = st.columns(2)

    with r2c1:
        st.markdown('<div class="section-label">Channel analysis</div>', unsafe_allow_html=True)
        st.markdown("### Response rate by channel")
        channel_data = pd.DataFrame({
            "Channel": ["LinkedIn", "Email"],
            "Replies": [ln_replied, em_replied],
            "Rate": [ln_replied / TOTAL_CONTACTS * 100, em_replied / TOTAL_CONTACTS * 100],
        })
        fig = px.bar(
            channel_data, x="Channel", y="Rate", text="Replies",
            color_discrete_sequence=[ACCENT_DARK],
        )
        fig.update_traces(
            texttemplate="%{text} replies", textposition="auto",
            marker_color=[ACCENT_DARK, ACCENT_MID],
        )
        fig.update_layout(**PLOTLY_LAYOUT, height=340, showlegend=False)
        fig.update_yaxes(title_text="Reply rate (%)")
        st.plotly_chart(fig, use_container_width=True)

    with r2c2:
        st.markdown('<div class="section-label">Timing</div>', unsafe_allow_html=True)
        st.markdown("### Best day to reach out")
        if "date" in daily.columns:
            d = daily.copy()
            d["dow"] = d["date"].dt.day_name()
            d["dow_num"] = d["date"].dt.dayofweek
            d["total_sent"] = d["linkedin_messages_sent"] + d["email_sent"]
            d["total_replies"] = d["linkedin_replies"] + d["email_replies"]
            active = d[d["total_sent"] > 0].copy()
            active["rr"] = active["total_replies"] / active["total_sent"] * 100
            dow = active.groupby(["dow_num", "dow"])["rr"].mean().reset_index()
            dow = dow[dow["dow_num"] < 5].sort_values("dow_num")

            colors = [ACCENT_GOLD if r == dow["rr"].max() else ACCENT_DARK for r in dow["rr"]]
            fig = go.Figure(go.Bar(
                x=dow["dow"], y=dow["rr"],
                text=dow["rr"].round(1), textposition="auto",
                marker_color=colors,
            ))
            fig.update_layout(**PLOTLY_LAYOUT, height=340, showlegend=False)
            fig.update_yaxes(title_text="Reply rate (%)")
            fig.update_traces(texttemplate="%{text}%")
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # --- Row 3: Product + Segments ---
    r3c1, r3c2 = st.columns(2)

    with r3c1:
        st.markdown('<div class="section-label">Products</div>', unsafe_allow_html=True)
        st.markdown("### Reply rate by product line")
        if "main_product" in df.columns:
            prod = df[df["main_product"] != "Unknown"].groupby("main_product").agg(
                n=("target_replied", "count"),
                replied=("target_replied", "sum"),
            ).reset_index()
            prod["rate"] = (prod["replied"] / prod["n"] * 100).round(1)
            prod = prod.sort_values("rate", ascending=True)

            fig = go.Figure(go.Bar(
                x=prod["rate"], y=prod["main_product"], orientation="h",
                text=prod["rate"], marker_color=ACCENT_DARK,
            ))
            fig.update_layout(**PLOTLY_LAYOUT, height=340, showlegend=False)
            fig.update_xaxes(title_text="Reply rate (%)")
            fig.update_traces(texttemplate="%{text}%", textposition="auto")
            st.plotly_chart(fig, use_container_width=True)

    with r3c2:
        st.markdown('<div class="section-label">Segmentation</div>', unsafe_allow_html=True)
        st.markdown("### Contact segments")
        cl = df.groupby("cluster").agg(
            n=("target_replied", "count"),
            rate=("target_replied", "mean"),
        ).reset_index()
        cl["rate_pct"] = (cl["rate"] * 100).round(1)

        labels = [CLUSTER_NAMES.get(c, f"Segment {c}") for c in cl["cluster"]]

        fig = go.Figure(go.Bar(
            x=labels,
            y=cl["n"],
            text=cl["rate_pct"],
            marker_color=[ACCENT_GOLD if r > GLOBAL_REPLY_RATE else ACCENT_DARK
                          for r in cl["rate_pct"]],
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=370, showlegend=False)
        fig.update_xaxes(tickangle=-30, tickfont=dict(size=10))
        fig.update_yaxes(title_text="Contacts")
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    # --- Segment profiles detail ---
    st.markdown("---")
    st.markdown('<div class="section-label">Segment detail</div>', unsafe_allow_html=True)
    st.markdown("### Segment profiles")

    CLUSTER_PROFILES = [
        {"Segment": 0, "Profile": "Financial Services -- Senior profiles",
         "Avg employees": "~1,900", "Seniority": "Director", "Reply rate": "9%",
         "Key insight": "Mid-size financial companies, strong fit for DATA & INFRA"},
        {"Segment": 1, "Profile": "Telecom & Tech -- Director level",
         "Avg employees": "~630", "Seniority": "Director", "Reply rate": "8%",
         "Key insight": "Largest segment (2.4K contacts), diversified industries"},
        {"Segment": 2, "Profile": "Large Telecom -- High engagement",
         "Avg employees": "~1,700", "Seniority": "Director", "Reply rate": "11%",
         "Key insight": "Above-average reply rate, Telecom & Retail dominant"},
        {"Segment": 3, "Profile": "Enterprise / Government -- 6K+ employees",
         "Avg employees": "~6,850", "Seniority": "Director", "Reply rate": "9%",
         "Key insight": "Largest companies, Government & Higher Education"},
        {"Segment": 4, "Profile": "Junior profiles -- Gov & Education",
         "Avg employees": "~420", "Seniority": "Junior", "Reply rate": "7%",
         "Key insight": "Lowest seniority, limited decision-making power"},
        {"Segment": 5, "Profile": "Industrial SMEs -- Low response",
         "Avg employees": "~380", "Seniority": "Director", "Reply rate": "3%",
         "Key insight": "Lowest conversion rate, Industrial Machinery sector"},
        {"Segment": 6, "Profile": "Pharma & Wellness -- Top converters",
         "Avg employees": "~1,360", "Seniority": "Director + C-Level", "Reply rate": "12%",
         "Key insight": "Highest reply rate, strong COLABORA & WORKPLACE fit"},
    ]
    st.dataframe(
        pd.DataFrame(CLUSTER_PROFILES),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Reply rate": st.column_config.TextColumn(width="small"),
            "Key insight": st.column_config.TextColumn(width="large"),
        },
    )

    st.markdown("---")

    # --- Top leads table ---
    st.markdown('<div class="section-label">Ranked leads</div>', unsafe_allow_html=True)
    st.markdown("### Highest-scored contacts")
    n_top = st.slider("Number of leads", 10, 100, 25, label_visibility="collapsed")
    top_leads = df.nlargest(n_top, "lead_score")[
        ["Company name", "lead_score", "cluster", "ai_SENIORITY",
         "Industry", "target_replied"]
    ].copy()
    top_leads["lead_score"] = top_leads["lead_score"].round(3)
    top_leads.columns = ["Company", "Score", "Segment", "Seniority", "Industry", "Replied"]
    st.dataframe(top_leads, use_container_width=True, hide_index=True)


# =====================================================
# PAGE 2: LEAD SCORER
# =====================================================
with tab_scorer:
    st.markdown('<div class="top-accent"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Scoring tool</div>', unsafe_allow_html=True)
    st.title("Individual Lead Scorer")
    st.markdown(
        '<div class="lead-text">'
        "Enter a contact's profile to estimate their probability of responding "
        "to outreach. The model returns a score, segment assignment, and channel recommendation."
        "</div>",
        unsafe_allow_html=True,
    )

    # --- Input form ---
    with st.form("lead_form"):
        st.markdown("### Contact profile")
        fc1, fc2, fc3 = st.columns(3)

        with fc1:
            seniority = st.selectbox(
                "Seniority level",
                options=[0, 1, 2, 3, 4, 5],
                format_func=lambda x: {
                    0: "Unknown", 1: "Junior", 2: "Lead / Senior",
                    3: "Manager", 4: "Director", 5: "VP / C-Level"
                }[x],
                index=3,
            )
            connections = st.number_input(
                "LinkedIn connections", min_value=0, max_value=30000, value=500
            )
            years_role = st.number_input(
                "Years in current role", min_value=0.0, max_value=40.0, value=3.0, step=0.5
            )

        with fc2:
            employees = st.number_input(
                "Company employees", min_value=1, max_value=500000, value=200
            )
            year_founded = st.number_input(
                "Year founded", min_value=1800, max_value=2026, value=2005
            )
            company_score = st.selectbox(
                "Company score",
                options=[0, 1, 2, 3],
                format_func=lambda x: {
                    0: "Not evaluated", 1: "Low", 2: "Medium", 3: "High"
                }[x],
                index=2,
            )

        with fc3:
            has_email = st.checkbox("Has professional email", value=True)
            has_bio = st.checkbox("Has LinkedIn bio", value=True)
            microsoft_flag = st.checkbox("Uses Microsoft technology", value=False)
            fit_approved = st.checkbox("FIT approved", value=True)
            hiring = st.checkbox("Active job postings", value=False)

        st.markdown("### Growth indicators")
        gc1, gc2, gc3 = st.columns(3)
        with gc1:
            growth_6m = st.number_input(
                "6-month headcount growth (%)", min_value=-50.0, max_value=100.0,
                value=5.0, step=1.0,
            ) / 100
        with gc2:
            growth_1y = st.number_input(
                "Annual headcount growth (%)", min_value=-50.0, max_value=200.0,
                value=8.0, step=1.0,
            ) / 100
        with gc3:
            growth_2y = st.number_input(
                "2-year headcount growth (%)", min_value=-50.0, max_value=300.0,
                value=15.0, step=1.0,
            ) / 100

        st.markdown("### Enrichment data")
        st.markdown(
            '<p style="font-size:0.85rem; color:#8B8B85; margin-top:-0.5rem">'
            "These fields reflect how much intelligence has been gathered on the contact. "
            "Enriched contacts score significantly higher."
            "</p>",
            unsafe_allow_html=True,
        )
        ec1, ec2, ec3 = st.columns(3)
        with ec1:
            enrichment_level = st.selectbox(
                "Enrichment level",
                options=["none", "basic", "full"],
                format_func=lambda x: {
                    "none": "Not enriched",
                    "basic": "Basic report available",
                    "full": "Full report + company report",
                }[x],
                index=0,
            )
        with ec2:
            has_momentum = st.checkbox("Has momentum signals", value=False)
        with ec3:
            ms_maturity = st.selectbox(
                "Microsoft maturity",
                options=[0, 1, 2, 3, 5, 8],
                format_func=lambda x: {
                    0: "None / Unknown", 1: "Basic (Exchange)",
                    2: "M365 user", 3: "M365 + Azure",
                    5: "Advanced (multi-product)", 8: "Full stack",
                }[x],
                index=0,
            )

        submitted = st.form_submit_button("Score this lead")

    # --- Scoring ---
    if submitted:
        # Map enrichment level to NLP feature values (based on actual data profiles)
        nlp_values = {
            "none": {"nlp_contact_report_length": 0.0, "nlp_report_length": 0.0},
            "basic": {"nlp_contact_report_length": 1200.0, "nlp_report_length": 3000.0},
            "full": {"nlp_contact_report_length": 2700.0, "nlp_report_length": 8000.0},
        }
        nlp = nlp_values[enrichment_level]

        contact_features = {
            "Years in role": years_role,
            "Years in company": years_role,
            "Number of connections": float(connections),
            "Number of employees": float(employees),
            "Year founded": float(year_founded),
            "Hiring on LinkedIn": float(hiring),
            "Six months headcount growth": growth_6m,
            "Two years headcount growth": growth_2y,
            "Yearly headcount growth": growth_1y,
            "fe_seniority_ord": float(seniority),
            "fe_contact_score_ord": float(company_score),
            "fe_company_score_ord": float(company_score),
            "fe_fit_approved": float(fit_approved),
            "fe_fit_data_approved": 0.0,
            "fe_company_age": float(2026 - year_founded),
            "fe_log_employees": float(np.log1p(employees)),
            "fe_company_size_bucket": (
                0 if employees < 10 else
                1 if employees < 50 else
                2 if employees < 250 else
                3 if employees < 1000 else 4
            ),
            "fe_log_connections": float(np.log1p(connections)),
            "fe_headcount_momentum": 0.5 * growth_6m + 0.3 * growth_1y + 0.2 * growth_2y,
            "fe_has_email": float(has_email),
            "fe_has_bio": float(has_bio),
            "fe_microsoft_flag": float(microsoft_flag),
            "fe_department_encoded": 0.08,
            "ext_ms_maturity_score": float(ms_maturity),
            "ext_has_competitor_tech": 0.0,
            "nlp_report_length": nlp["nlp_report_length"],
            "nlp_contact_report_length": nlp["nlp_contact_report_length"],
            "nlp_has_momentum": float(has_momentum),
            "nlp_urgency_score": 1.0 if has_momentum else 0.0,
            "nlp_embedding_01": 4.8,
            "nlp_embedding_02": 3.0,
            "nlp_embedding_03": 5.9,
            "nlp_topic": 0.0,
        }

        df_input = pd.DataFrame([contact_features])
        for col in FEATURE_COLS:
            if col not in df_input.columns:
                df_input[col] = np.nan

        X = preprocessor.transform(df_input[FEATURE_COLS])
        score = float(lead_scorer.predict_proba(X)[:, 1][0])

        cluster_feats = clustering_bundle["features"]
        df_cluster = df_input[cluster_feats].copy()
        X_cluster = clustering_bundle["scaler"].transform(
            clustering_bundle["imputer"].transform(df_cluster)
        )
        cluster = int(clustering_bundle["kmeans"].predict(X_cluster)[0])

        if score >= 0.5:
            risk_level = "High priority"
            risk_css = "rec-card rec-card-high"
        elif score >= 0.2:
            risk_level = "Medium priority"
            risk_css = "rec-card rec-card-mid"
        else:
            risk_level = "Low priority"
            risk_css = "rec-card rec-card-low"

        # --- Results ---
        st.markdown("---")
        st.markdown('<div class="section-label">Results</div>', unsafe_allow_html=True)
        st.markdown("### Scoring output")

        rc1, rc2, rc3, rc4 = st.columns(4)
        rc1.metric("Lead score", f"{score:.1%}")
        rc2.metric("Priority", risk_level)
        rc3.metric("Segment", f"{cluster}")
        rc4.metric("Best channel", "LinkedIn")

        # Gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score * 100,
            number={"suffix": "%", "font": {"family": "Georgia", "size": 40, "color": ACCENT_DARK}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": ACCENT_LIGHT},
                "bar": {"color": ACCENT_GOLD},
                "bgcolor": "#F0F0EB",
                "steps": [
                    {"range": [0, 20], "color": "#E8E8E3"},
                    {"range": [20, 50], "color": "#D4D4CF"},
                    {"range": [50, 100], "color": "#FFF3D1"},
                ],
            },
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", height=250, margin=dict(t=30, b=10),
            font=dict(family="-apple-system, BlinkMacSystemFont, sans-serif"),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Comparison
        st.markdown("---")
        st.markdown('<div class="section-label">Context</div>', unsafe_allow_html=True)
        st.markdown("### Where this contact stands")

        percentile = (df["lead_score"] < score).mean() * 100

        cc1, cc2 = st.columns([1, 1])
        with cc1:
            # Recommendation card
            if score >= 0.5:
                rec_text = (
                    "This contact scores in the **top tier**. Prioritize immediate outreach "
                    "via LinkedIn. Best day: Thursday. The model estimates a high probability "
                    "of engagement."
                )
            elif score >= 0.2:
                rec_text = (
                    "This contact shows **moderate potential**. Consider enriching the profile "
                    "before outreach to improve personalization. LinkedIn remains the preferred channel."
                )
            else:
                rec_text = (
                    "This contact has a **low estimated response probability**. Evaluate whether "
                    "outreach resources are better allocated to higher-scored leads."
                )

            st.markdown(
                f'<div class="{risk_css}">'
                f'<strong style="font-size:0.9rem">{risk_level}</strong><br>'
                f'<span style="font-size:0.85rem; color:#3D3D3A">Score above {percentile:.0f}% of all contacts</span>'
                f'<p style="margin-top:0.8rem; font-size:0.9rem">{rec_text}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )

        with cc2:
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=df["lead_score"], nbinsx=50,
                marker_color=ACCENT_LIGHT, opacity=0.7, name="All contacts",
            ))
            fig.add_vline(x=score, line_dash="dash", line_color=ACCENT_GOLD, line_width=2,
                          annotation_text=f"This contact ({score:.0%})",
                          annotation_font_size=11)
            fig.update_layout(**PLOTLY_LAYOUT, height=260, showlegend=False)
            fig.update_xaxes(title_text="Lead score")
            fig.update_yaxes(title_text="Count")
            st.plotly_chart(fig, use_container_width=True)

        # Cluster profile
        st.markdown("---")
        st.markdown('<div class="section-label">Segment profile</div>', unsafe_allow_html=True)
        cluster_label = CLUSTER_NAMES.get(cluster, f"Segment {cluster}").replace("\n", " -- ")
        st.markdown(f"### Segment {cluster}: {cluster_label}")

        cluster_data = df[df["cluster"] == cluster]
        cluster_reply = cluster_data["target_replied"].mean() * 100
        cluster_size = len(cluster_data)
        delta_vs_global = cluster_reply - GLOBAL_REPLY_RATE

        pc1, pc2, pc3 = st.columns(3)
        pc1.metric("Contacts in segment", f"{cluster_size:,}")
        pc2.metric("Segment reply rate", f"{cluster_reply:.1f}%")
        pc3.metric("vs global average", f"{delta_vs_global:+.1f}pp")

        if "Industry" in cluster_data.columns:
            top_ind = (
                cluster_data["Industry"].dropna().value_counts().head(5).reset_index()
            )
            top_ind.columns = ["Industry", "Contacts"]
            st.dataframe(top_ind, use_container_width=True, hide_index=True)
