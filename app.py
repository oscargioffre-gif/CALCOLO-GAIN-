import streamlit as st

st.set_page_config(
    page_title="Trade Calculator",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ─── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&family=DM+Sans:wght@400;500;600&display=swap');

:root {
    --bg:      #0a0d14;
    --surface: #111520;
    --card:    #161c2d;
    --border:  #1f2a44;
    --accent:  #3b82f6;
    --green:   #10b981;
    --text:    #f0f4ff;
    --muted:   #8b9ec7;
    --mono:    'DM Mono', monospace;
    --sans:    'DM Sans', sans-serif;
    --display: 'Syne', sans-serif;
}

html, body, [class*="css"], .stApp {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
}

/* HEADER */
.main-header {
    text-align: center;
    padding: 2rem 0 1.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
}
.main-header h1 {
    font-family: var(--display);
    font-size: 2.2rem;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -0.03em;
    margin: 0;
}
.main-header .sub {
    font-family: var(--mono);
    font-size: 0.75rem;
    color: var(--muted);
    margin-top: 0.4rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: var(--display) !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    color: var(--muted) !important;
    background: transparent !important;
    border-radius: 8px !important;
    padding: 0.75rem 1.5rem !important;
    transition: all 0.2s ease;
}
.stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: #ffffff !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem !important; }

/* SECTION LABEL */
.section-label {
    font-family: var(--mono);
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.5rem;
    margin-top: 1.5rem;
}

/* INPUTS — large touch targets */
.stNumberInput label {
    font-family: var(--sans) !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    color: var(--text) !important;
    letter-spacing: 0.01em;
}
.stNumberInput input {
    font-family: var(--mono) !important;
    font-size: 1.4rem !important;
    font-weight: 500 !important;
    color: var(--text) !important;
    background-color: var(--card) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 0.9rem 1rem !important;
    height: 3.4rem !important;
    caret-color: var(--accent) !important;
    transition: border-color 0.2s;
}
.stNumberInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
    outline: none !important;
}
.stNumberInput [data-testid="stNumberInputStepDown"],
.stNumberInput [data-testid="stNumberInputStepUp"] {
    width: 2.8rem !important;
    height: 3.4rem !important;
    font-size: 1.2rem !important;
    background: var(--surface) !important;
    border-color: var(--border) !important;
    color: var(--muted) !important;
}

/* CARDS */
.result-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.25rem 1.4rem;
    margin-bottom: 0.75rem;
}
.result-card-accent {
    background: linear-gradient(135deg, #0f1f3d 0%, #0d1a30 100%);
    border: 1.5px solid var(--accent);
    border-radius: 14px;
    padding: 1.25rem 1.4rem;
    margin-bottom: 0.75rem;
}
.result-card-green {
    background: linear-gradient(135deg, #062818 0%, #041f13 100%);
    border: 1.5px solid var(--green);
    border-radius: 14px;
    padding: 1.4rem 1.5rem;
    margin-bottom: 0.75rem;
}
.card-title {
    font-family: var(--display);
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.85rem;
}
.metric-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.38rem 0;
}
.metric-label { font-family: var(--sans); font-size: 0.9rem; font-weight: 500; color: var(--muted); }
.metric-value { font-family: var(--mono); font-size: 1.05rem; font-weight: 500; color: var(--text); }
.metric-value-large { font-family: var(--mono); font-size: 1.75rem; font-weight: 500; color: #ffffff; letter-spacing: -0.02em; }
.metric-value-green { font-family: var(--mono); font-size: 1.75rem; font-weight: 500; color: var(--green); letter-spacing: -0.02em; }
.badge-pct {
    display: inline-block;
    background: rgba(16,185,129,0.18);
    color: var(--green);
    font-family: var(--mono);
    font-size: 0.85rem;
    font-weight: 500;
    border-radius: 6px;
    padding: 0.2rem 0.6rem;
    margin-left: 0.6rem;
    vertical-align: middle;
}
.hr { height: 1px; background: var(--border); margin: 0.5rem 0; }

/* HIDE streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; max-width: 680px !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ─── HEADER ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>Trade Calculator</h1>
  <div class="sub">Prezzo di carico &amp; target di vendita</div>
</div>
""", unsafe_allow_html=True)

# ─── HELPERS ───────────────────────────────────────────────────────────────
def mrow(label, value):
    st.markdown(f'<div class="metric-row"><span class="metric-label">{label}</span>'
                f'<span class="metric-value">{value}</span></div>', unsafe_allow_html=True)

def hr():
    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

def slabel(text):
    st.markdown(f'<div class="section-label">{text}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB MILANO
# ══════════════════════════════════════════════════════════════
tab_mil, tab_nas = st.tabs(["🇮🇹  MILANO — EUR", "🇺🇸  NASDAQ — USD"])

with tab_mil:
    slabel("Dati di acquisto")
    c1, c2 = st.columns(2)
    with c1:
        pa_m = st.number_input("Prezzo acquisto (€)", min_value=0.0001, value=10.0,
                                step=0.01, format="%.4f", key="pa_m")
    with c2:
        q_m = st.number_input("Quantità azioni", min_value=1, value=100, step=1, key="q_m")

    if pa_m > 0 and q_m > 0:
        cv_m   = pa_m * q_m
        ca_m   = cv_m * 0.0019
        Ka_m   = cv_m + ca_m
        Pc_m   = Ka_m / q_m

        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📥 Riepilogo acquisto</div>', unsafe_allow_html=True)
        mrow("Controvalore", f"€ {cv_m:,.2f}")
        hr()
        mrow("Commissione acquisto (0.19%)", f"€ {ca_m:,.2f}")
        hr()
        mrow("Costo totale Kₐ", f"€ {Ka_m:,.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="result-card-accent">
          <div class="card-title">📌 Prezzo di carico</div>
          <div class="metric-value-large">€ {Pc_m:,.4f}</div>
          <div class="metric-label" style="margin-top:0.3rem">per azione · commissioni incluse</div>
        </div>""", unsafe_allow_html=True)

        slabel("Target di guadagno")
        gl_m = st.number_input("Guadagno lordo desiderato (€)", min_value=0.0, value=100.0,
                                step=1.0, format="%.2f", key="gl_m")

        Pv_m  = (gl_m + Ka_m) / (q_m * (1 - 0.0019))
        cv_m  = Pv_m * q_m
        ca_v  = cv_m * 0.0019
        pct_m = (cv_m - Ka_m) / Ka_m * 100

        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📤 Riepilogo vendita</div>', unsafe_allow_html=True)
        mrow("Commissione vendita (0.19%)", f"€ {ca_v:,.2f}")
        hr()
        mrow("Ricavo netto stimato", f"€ {cv_m - ca_v:,.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="result-card-green">
          <div class="card-title">🎯 Prezzo di vendita target</div>
          <div>
            <span class="metric-value-green">€ {Pv_m:,.4f}</span>
            <span class="badge-pct">+{pct_m:.2f}%</span>
          </div>
          <div class="metric-label" style="margin-top:0.35rem">per azione da inserire nell'ordine</div>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB NASDAQ
# ══════════════════════════════════════════════════════════════
with tab_nas:
    slabel("Dati di acquisto")
    c1, c2 = st.columns(2)
    with c1:
        pa_n = st.number_input("Prezzo acquisto ($)", min_value=0.0001, value=50.0,
                                step=0.01, format="%.4f", key="pa_n")
    with c2:
        q_n = st.number_input("Quantità azioni", min_value=1, value=10, step=1, key="q_n")

    if pa_n > 0 and q_n > 0:
        cv_n = pa_n * q_n
        Ka_n = cv_n + 9.0
        Pc_n = Ka_n / q_n

        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📥 Riepilogo acquisto</div>', unsafe_allow_html=True)
        mrow("Controvalore", f"$ {cv_n:,.2f}")
        hr()
        mrow("Commissione acquisto (flat)", "$ 9.00")
        hr()
        mrow("Costo totale Kₐ", f"$ {Ka_n:,.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="result-card-accent">
          <div class="card-title">📌 Prezzo di carico</div>
          <div class="metric-value-large">$ {Pc_n:,.4f}</div>
          <div class="metric-label" style="margin-top:0.3rem">per azione · commissioni incluse</div>
        </div>""", unsafe_allow_html=True)

        slabel("Target di guadagno")
        gl_n = st.number_input("Guadagno lordo desiderato ($)", min_value=0.0, value=50.0,
                                step=1.0, format="%.2f", key="gl_n")

        Pv_n  = (gl_n + Ka_n + 9.0) / q_n
        pct_n = ((Pv_n * q_n) - Ka_n) / Ka_n * 100

        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📤 Riepilogo vendita</div>', unsafe_allow_html=True)
        mrow("Commissione vendita (flat)", "$ 9.00")
        hr()
        mrow("Ricavo lordo vendita", f"$ {Pv_n * q_n:,.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="result-card-green">
          <div class="card-title">🎯 Prezzo di vendita target</div>
          <div>
            <span class="metric-value-green">$ {Pv_n:,.4f}</span>
            <span class="badge-pct">+{pct_n:.2f}%</span>
          </div>
          <div class="metric-label" style="margin-top:0.35rem">per azione da inserire nell'ordine</div>
        </div>""", unsafe_allow_html=True)
