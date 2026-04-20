import streamlit as st
import json, os, io
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(
    page_title="Trade Calculator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── FONT PATHS (DejaVu — always available on Linux / Streamlit Cloud) ────────
_F = "/usr/share/fonts/truetype/dejavu/"
FONT_SANS_B = _F + "DejaVuSans-Bold.ttf"
FONT_MONO   = _F + "DejaVuSansMono.ttf"
FONT_MONO_B = _F + "DejaVuSansMono-Bold.ttf"

# ─── PERSIST ──────────────────────────────────────────────────────────────────
SAVE_FILE = "trade_data.json"

def load_saved():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_data(data: dict):
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

saved = load_saved()

def _init(key, default):
    if key not in st.session_state:
        st.session_state[key] = saved.get(key, default)

for i in range(1, 4):
    _init(f"mil_tk_{i}", "")
    _init(f"mil_pc_{i}", 0.0)
    _init(f"mil_cl_{i}", 0.0)   # chiusura precedente
    _init(f"mil_q_{i}",  0)
    _init(f"mil_gl_{i}", 0.0)
    _init(f"mil_lo_{i}", 0.0)   # perdita tollerata
    _init(f"nas_tk_{i}", "")
    _init(f"nas_pc_{i}", 0.0)
    _init(f"nas_cl_{i}", 0.0)
    _init(f"nas_q_{i}",  0)
    _init(f"nas_gl_{i}", 0.0)
    _init(f"nas_lo_{i}", 0.0)

# ─── JPEG GENERATOR ───────────────────────────────────────────────────────────
def build_jpeg(slots_mil, slots_nas) -> bytes:
    """
    slots_mil / slots_nas: list of 3 dicts with keys:
      pc, q, Ka, gl, Pv, pct, comm_v   (None if slot inactive)
    Returns JPEG bytes.
    """
    BG       = "#0a0d14"
    CARD_MIL = "#0d1a30"
    CARD_NAS = "#1a1000"
    BORDER_M = "#3b82f6"
    BORDER_N = "#f59e0b"
    GREEN    = "#10b981"
    WHITE    = "#f0f4ff"
    MUTED    = "#8b9ec7"
    LABEL_M  = "#93c5fd"
    LABEL_N  = "#fbbf24"

    COL_W = 520
    PAD   = 36
    W     = PAD + COL_W + PAD + COL_W + PAD   # ~1140

    # --- measure height needed ---
    HEADER_H  = 110
    COL_HDR_H = 52
    SLOT_H    = 230   # approx per active slot; adjusted below
    FOOTER_H  = 52
    H = HEADER_H + COL_HDR_H + 3 * SLOT_H + FOOTER_H + 20

    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    try:
        fnt_title  = ImageFont.truetype(FONT_SANS_B, 30)
        fnt_sub    = ImageFont.truetype(FONT_MONO,   13)
        fnt_col    = ImageFont.truetype(FONT_SANS_B, 17)
        fnt_slot   = ImageFont.truetype(FONT_MONO,   11)
        fnt_label  = ImageFont.truetype(FONT_MONO,   13)
        fnt_val    = ImageFont.truetype(FONT_MONO_B, 15)
        fnt_big    = ImageFont.truetype(FONT_MONO_B, 22)
        fnt_pct    = ImageFont.truetype(FONT_MONO_B, 14)
    except Exception:
        fnt_title = fnt_sub = fnt_col = fnt_slot = fnt_label = fnt_val = fnt_big = fnt_pct = ImageFont.load_default()

    def rr(x1, y1, x2, y2, r, fill=None, outline=None, width=1):
        """Rounded rectangle helper."""
        draw.rounded_rectangle([x1, y1, x2, y2], radius=r, fill=fill, outline=outline, width=width)

    def hline(y, x1, x2, color="#1f2a44"):
        draw.line([(x1, y), (x2, y)], fill=color, width=1)

    # HEADER
    draw.text((W // 2, 28), "Trade Calculator", font=fnt_title, fill=WHITE, anchor="mt")
    draw.text((W // 2, 66), "RIEPILOGO POSIZIONI · PREZZO DI CARICO & TARGET DI VENDITA", font=fnt_sub, fill=MUTED, anchor="mt")
    ts = datetime.now().strftime("%d/%m/%Y  %H:%M")
    draw.text((W // 2, 84), ts, font=fnt_sub, fill=MUTED, anchor="mt")
    hline(104, PAD, W - PAD, "#1f2a44")

    y0 = HEADER_H + 8

    def draw_col_header(x, label, color, border):
        rr(x, y0, x + COL_W, y0 + COL_HDR_H - 4, 10, outline=border, width=2)
        draw.text((x + COL_W // 2, y0 + (COL_HDR_H - 4) // 2), label, font=fnt_col, fill=color, anchor="mm")

    draw_col_header(PAD,               "🇮🇹  MILANO — EUR", LABEL_M, BORDER_M)
    draw_col_header(PAD + COL_W + PAD, "🇺🇸  NASDAQ — USD", LABEL_N, BORDER_N)

    slot_top = y0 + COL_HDR_H + 8

    def draw_slot(col_x, idx, s, card_bg, border_col, sym, is_nas=False):
        nonlocal slot_top
        SH = 215
        sx, sy = col_x, slot_top + idx * (SH + 10)
        ex = sx + COL_W

        # Card bg
        rr(sx, sy, ex, sy + SH, 12, fill=card_bg, outline=border_col, width=2)
        # Left accent bar
        rr(sx, sy + 10, sx + 3, sy + SH - 10, 2, fill=border_col)

        tx = sx + 16
        ty = sy + 14

        # Slot number + ticker name
        tk_name = s.get("tk", "").upper().strip() if s else ""
        if tk_name:
            draw.text((tx, ty), f"· {tk_name}", font=fnt_col, fill=border_col)
        else:
            draw.text((tx, ty), f"· SLOT {idx + 1}", font=fnt_slot, fill=MUTED)
        ty += 22

        if s is None:
            draw.text((tx, ty + 60), "— nessun dato inserito —", font=fnt_label, fill=MUTED)
            return

        # Row helper
        def row(lbl, val, color=WHITE):
            draw.text((tx, ty),          lbl,  font=fnt_label, fill=MUTED)
            draw.text((ex - 16, ty),     val,  font=fnt_val,   fill=color, anchor="ra")

        def big_row(lbl, val, pct_str, val_color):
            draw.text((tx, ty),      lbl,      font=fnt_slot,  fill=MUTED)
            draw.text((tx, ty + 16), val,      font=fnt_big,   fill=val_color)
            # badge
            bx = tx + draw.textlength(val, font=fnt_big) + 10
            rr(bx, ty + 18, bx + draw.textlength(pct_str, font=fnt_pct) + 12, ty + 18 + 20, 4,
               fill="#0d2e1f", outline=GREEN, width=1)
            draw.text((bx + 6, ty + 18), pct_str, font=fnt_pct, fill=GREEN)

        ty_ref = ty

        # Carico & Kₐ
        row("Prezzo di carico",        f"{sym} {s['pc']:,.4f}")
        ty += 22
        row("Quantita",                f"{s['q']:,}")
        ty += 22
        hline(ty, tx, ex - 16, "#1f2a44")
        ty += 8
        row("Costo totale Ka",         f"{sym} {s['Ka']:,.2f}", border_col)
        ty += 22
        hline(ty, tx, ex - 16, "#1f2a44")
        ty += 8

        # Commission
        if not is_nas:
            row("Comm. vendita (0.19%)", f"{sym} {s['comm_v']:,.2f}")
        else:
            row("Comm. vendita (flat)",  f"$ 9.00")
        ty += 22
        row("Guadagno lordo target",   f"{sym} {s['gl']:,.2f}")
        ty += 26

        # Target price — big
        big_row("PREZZO DI VENDITA TARGET", f"{sym} {s['Pv']:,.4f}", f"+{s['pct']:.2f}%", GREEN)

    # Compute slot data
    def mil_slot(i):
        pc = st.session_state.get(f"mil_pc_{i}_inp", 0.0) or 0.0
        q  = st.session_state.get(f"mil_q_{i}_inp",  0)   or 0
        gl = st.session_state.get(f"mil_gl_{i}_inp", 0.0) or 0.0
        tk = st.session_state.get(f"mil_tk_{i}_inp", "") or ""
        if pc <= 0 or q <= 0:
            return None
        Ka   = pc * q
        Pv   = (gl + Ka) / (q * (1 - 0.0019))
        pct  = ((Pv * q) - Ka) / Ka * 100
        comm = Pv * q * 0.0019
        return dict(tk=tk, pc=pc, q=q, Ka=Ka, gl=gl, Pv=Pv, pct=pct, comm_v=comm)

    def nas_slot(i):
        pc = st.session_state.get(f"nas_pc_{i}_inp", 0.0) or 0.0
        q  = st.session_state.get(f"nas_q_{i}_inp",  0)   or 0
        gl = st.session_state.get(f"nas_gl_{i}_inp", 0.0) or 0.0
        tk = st.session_state.get(f"nas_tk_{i}_inp", "") or ""
        if pc <= 0 or q <= 0:
            return None
        Ka  = pc * q
        Pv  = (gl + Ka + 9.0) / q
        pct = ((Pv * q) - Ka) / Ka * 100
        return dict(tk=tk, pc=pc, q=q, Ka=Ka, gl=gl, Pv=Pv, pct=pct, comm_v=9.0)

    for i in range(3):
        draw_slot(PAD,               i, mil_slot(i + 1), CARD_MIL, BORDER_M, "€", is_nas=False)
        draw_slot(PAD + COL_W + PAD, i, nas_slot(i + 1), CARD_NAS, BORDER_N, "$", is_nas=True)

    # Footer
    fy = H - FOOTER_H + 10
    hline(fy, PAD, W - PAD, "#1f2a44")
    draw.text((W // 2, fy + 18), "Trade Calculator · os gioffre", font=fnt_sub, fill=MUTED, anchor="mt")

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=93)
    return buf.getvalue()

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&family=DM+Sans:wght@400;500;600&display=swap');
:root{--bg:#0a0d14;--surface:#111520;--card:#161c2d;--border:#1f2a44;--accent:#3b82f6;--gold:#f59e0b;--green:#10b981;--text:#f0f4ff;--muted:#8b9ec7;--mono:'DM Mono',monospace;--sans:'DM Sans',sans-serif;--display:'Syne',sans-serif}
html,body,[class*="css"],.stApp{background-color:var(--bg)!important;color:var(--text)!important;font-family:var(--sans)!important}
.main-header{text-align:center;padding:1.6rem 0 1.2rem;border-bottom:1px solid var(--border);margin-bottom:1.8rem}
.main-header h1{font-family:var(--display);font-size:2rem;font-weight:800;color:var(--text);letter-spacing:-0.03em;margin:0}
.main-header .sub{font-family:var(--mono);font-size:0.7rem;color:var(--muted);margin-top:.35rem;letter-spacing:.15em;text-transform:uppercase}
.col-header{font-family:var(--display);font-size:1.05rem;font-weight:800;padding:.55rem .9rem;border-radius:10px;margin-bottom:1.2rem;text-align:center}
.col-header-mil{background:rgba(59,130,246,.12);border:1.5px solid rgba(59,130,246,.35);color:#93c5fd}
.col-header-nas{background:rgba(245,158,11,.11);border:1.5px solid rgba(245,158,11,.32);color:#fbbf24}
.slot-num{font-family:var(--mono);font-size:.62rem;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);margin-bottom:.5rem}
.stTextInput label{font-family:var(--sans)!important;font-size:.88rem!important;font-weight:600!important;color:var(--text)!important}
.stTextInput input{font-family:var(--mono)!important;font-size:1.1rem!important;font-weight:700!important;color:var(--text)!important;background-color:var(--surface)!important;border:1.5px solid var(--border)!important;border-radius:9px!important;padding:.75rem .9rem!important;height:3.0rem!important;caret-color:var(--accent)!important;letter-spacing:.1em}
.stTextInput input:focus{border-color:var(--accent)!important;box-shadow:0 0 0 3px rgba(59,130,246,.15)!important;outline:none!important}
.stNumberInput label{font-family:var(--sans)!important;font-size:.88rem!important;font-weight:600!important;color:var(--text)!important}
.stNumberInput input{font-family:var(--mono)!important;font-size:1.25rem!important;font-weight:500!important;color:var(--text)!important;background-color:var(--surface)!important;border:1.5px solid var(--border)!important;border-radius:9px!important;padding:.8rem .9rem!important;height:3.15rem!important;caret-color:var(--accent)!important;transition:border-color .2s}
.stNumberInput input:focus{border-color:var(--accent)!important;box-shadow:0 0 0 3px rgba(59,130,246,.15)!important;outline:none!important}
.stNumberInput [data-testid="stNumberInputStepDown"],.stNumberInput [data-testid="stNumberInputStepUp"]{width:2.6rem!important;height:3.15rem!important;font-size:1.1rem!important;background:var(--card)!important;border-color:var(--border)!important;color:var(--muted)!important}
.res-row{display:flex;justify-content:space-between;align-items:center;padding:.28rem 0}
.res-label{font-family:var(--sans);font-size:.82rem;font-weight:500;color:var(--muted)}
.res-val{font-family:var(--mono);font-size:.95rem;font-weight:500;color:var(--text)}
.hr-thin{height:1px;background:var(--border);margin:.35rem 0;opacity:.6}
.carico-box{background:linear-gradient(135deg,#0f1f3d,#0d1a30);border:1.5px solid var(--accent);border-radius:10px;padding:.7rem .9rem;margin:.6rem 0}
.carico-box-nas{background:linear-gradient(135deg,#1f1400,#160f00);border-color:var(--gold)}
.carico-label{font-family:var(--mono);font-size:.6rem;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);margin-bottom:.2rem}
.carico-val{font-family:var(--mono);font-size:1.35rem;font-weight:500;color:#fff;letter-spacing:-.015em}
.target-box{background:linear-gradient(135deg,#062818,#041f13);border:1.5px solid var(--green);border-radius:10px;padding:.7rem .9rem;margin-top:.5rem}
.loss-box{background:linear-gradient(135deg,#1f0808,#130404);border:1.5px solid #ef4444;border-radius:10px;padding:.7rem .9rem;margin-top:.5rem}
.target-val{font-family:var(--mono);font-size:1.35rem;font-weight:500;color:var(--green);letter-spacing:-.015em}
.loss-val{font-family:var(--mono);font-size:1.35rem;font-weight:500;color:#f87171;letter-spacing:-.015em}
.badge-pct{display:inline-block;background:rgba(16,185,129,.18);color:var(--green);font-family:var(--mono);font-size:.78rem;border-radius:5px;padding:.15rem .5rem;margin-left:.5rem;vertical-align:middle}
.badge-loss{display:inline-block;background:rgba(239,68,68,.18);color:#f87171;font-family:var(--mono);font-size:.78rem;border-radius:5px;padding:.15rem .5rem;margin-left:.5rem;vertical-align:middle}
.badge-cl{display:inline-block;background:rgba(139,158,199,.12);color:#8b9ec7;font-family:var(--mono);font-size:.72rem;border-radius:5px;padding:.13rem .45rem;margin-left:.35rem;vertical-align:middle;border:1px solid rgba(139,158,199,.22)}
.inactive{font-family:var(--mono);font-size:.8rem;color:var(--muted);opacity:.5;padding:.4rem 0}
div[data-testid="stButton"]>button{font-family:var(--display)!important;font-size:1rem!important;font-weight:700!important;background:var(--accent)!important;color:#fff!important;border:none!important;border-radius:10px!important;padding:.75rem 2rem!important;letter-spacing:.03em;transition:all .2s;width:100%}
div[data-testid="stButton"]>button:hover{background:#2563eb!important;transform:translateY(-1px);box-shadow:0 4px 16px rgba(59,130,246,.35)!important}
div[data-testid="stDownloadButton"]>button{font-family:var(--display)!important;font-size:1rem!important;font-weight:700!important;background:var(--surface)!important;color:var(--green)!important;border:1.5px solid var(--green)!important;border-radius:10px!important;padding:.75rem 2rem!important;width:100%}
div[data-testid="stDownloadButton"]>button:hover{background:rgba(16,185,129,.1)!important}
.save-ok{font-family:var(--mono);font-size:.78rem;color:var(--green);text-align:center;letter-spacing:.1em;margin-top:.4rem}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding-top:.6rem!important;max-width:1100px!important}
::-webkit-scrollbar{width:4px}::-webkit-scrollbar-track{background:var(--bg)}::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
  <h1>Trade Calculator</h1>
  <div class="sub">Prezzo di carico &amp; target di vendita · Milano + NASDAQ</div>
</div>
""", unsafe_allow_html=True)

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def rrow(label, value):
    st.markdown(f'<div class="res-row"><span class="res-label">{label}</span>'
                f'<span class="res-val">{value}</span></div>', unsafe_allow_html=True)

def thin_hr():
    st.markdown('<div class="hr-thin"></div>', unsafe_allow_html=True)

# ─── SLOT RENDERERS ───────────────────────────────────────────────────────────
def slot_milano(i):
    sym = "€"
    with st.container():
        st.markdown(f'<div class="slot-num">· Slot {i}</div>', unsafe_allow_html=True)
        tk = st.text_input("Ticker / Titolo", value=st.session_state[f"mil_tk_{i}"],
                            placeholder="es. ENI, ENEL, ISP…", key=f"mil_tk_{i}_inp", max_chars=12)
        c1, c2 = st.columns(2)
        with c1:
            pc = st.number_input(f"Prezzo di carico {sym}", min_value=0.0,
                                  value=float(st.session_state[f"mil_pc_{i}"]),
                                  step=0.01, format="%.4f", key=f"mil_pc_{i}_inp")
        with c2:
            q = st.number_input("Quantità", min_value=0,
                                 value=int(st.session_state[f"mil_q_{i}"]),
                                 step=1, key=f"mil_q_{i}_inp")
        cl = st.number_input(f"Chiusura precedente {sym} (opzionale)",
                              min_value=0.0, value=float(st.session_state[f"mil_cl_{i}"]),
                              step=0.01, format="%.4f", key=f"mil_cl_{i}_inp")
        if pc > 0 and q > 0:
            Ka = pc * q
            st.markdown(f'<div class="carico-box"><div class="carico-label">📌 Costo totale Kₐ</div>'
                        f'<div class="carico-val">{sym} {Ka:,.2f}</div></div>', unsafe_allow_html=True)

            c_gl, c_lo = st.columns(2)
            with c_gl:
                gl = st.number_input(f"Guadagno target {sym}", min_value=0.0,
                                      value=float(st.session_state[f"mil_gl_{i}"]),
                                      step=1.0, format="%.2f", key=f"mil_gl_{i}_inp")
            with c_lo:
                lo = st.number_input(f"Perdita tollerata {sym}", min_value=0.0,
                                      value=float(st.session_state[f"mil_lo_{i}"]),
                                      step=1.0, format="%.2f", key=f"mil_lo_{i}_inp")

            # ── TARGET GUADAGNO ──
            Pv   = (gl + Ka) / (q * (1 - 0.0019))
            pct  = ((Pv * q) - Ka) / Ka * 100
            cv   = Pv * q * 0.0019
            cl_badge = ""
            if cl > 0:
                pct_cl = (Pv - cl) / cl * 100
                sign = "+" if pct_cl >= 0 else ""
                cl_badge = f'<span class="badge-cl">vs chius. {sign}{pct_cl:.2f}%</span>'
            rrow("Commissione vendita (0.19%)", f"{sym} {cv:,.2f}")
            thin_hr()
            rrow("Ricavo netto stimato", f"{sym} {Pv * q * (1 - 0.0019):,.2f}")
            st.markdown(
                f'<div class="target-box">'
                f'<div class="carico-label">🎯 Prezzo di vendita target</div>'
                f'<span class="target-val">{sym} {Pv:,.4f}</span>'
                f'<span class="badge-pct">+{pct:.2f}%</span>'
                f'{cl_badge}'
                f'</div>', unsafe_allow_html=True)

            # ── STOP LOSS ──
            if lo > 0:
                Ps     = (Ka - lo) / (q * (1 + 0.0019))
                pct_s  = ((Ps * q) - Ka) / Ka * 100
                cl_stop = ""
                if cl > 0:
                    pct_cl_s = (Ps - cl) / cl * 100
                    sign = "+" if pct_cl_s >= 0 else ""
                    cl_stop = f'<span class="badge-cl">vs chius. {sign}{pct_cl_s:.2f}%</span>'
                st.markdown(
                    f'<div class="loss-box">'
                    f'<div class="carico-label">🛑 Prezzo stop loss</div>'
                    f'<span class="loss-val">{sym} {Ps:,.4f}</span>'
                    f'<span class="badge-loss">{pct_s:.2f}%</span>'
                    f'{cl_stop}'
                    f'</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="inactive">— inserisci carico e quantità —</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
    st.session_state[f"mil_tk_{i}"] = st.session_state.get(f"mil_tk_{i}_inp", st.session_state[f"mil_tk_{i}"])
    st.session_state[f"mil_pc_{i}"] = st.session_state.get(f"mil_pc_{i}_inp", st.session_state[f"mil_pc_{i}"])
    st.session_state[f"mil_cl_{i}"] = st.session_state.get(f"mil_cl_{i}_inp", st.session_state[f"mil_cl_{i}"])
    st.session_state[f"mil_q_{i}"]  = st.session_state.get(f"mil_q_{i}_inp",  st.session_state[f"mil_q_{i}"])
    st.session_state[f"mil_gl_{i}"] = st.session_state.get(f"mil_gl_{i}_inp", st.session_state[f"mil_gl_{i}"])
    st.session_state[f"mil_lo_{i}"] = st.session_state.get(f"mil_lo_{i}_inp", st.session_state[f"mil_lo_{i}"])

def slot_nasdaq(i):
    sym = "$"
    with st.container():
        st.markdown(f'<div class="slot-num">· Slot {i}</div>', unsafe_allow_html=True)
        tk = st.text_input("Ticker / Titolo", value=st.session_state[f"nas_tk_{i}"],
                            placeholder="es. AAPL, NVDA, TSLA…", key=f"nas_tk_{i}_inp", max_chars=12)
        c1, c2 = st.columns(2)
        with c1:
            pc = st.number_input(f"Prezzo di carico {sym}", min_value=0.0,
                                  value=float(st.session_state[f"nas_pc_{i}"]),
                                  step=0.01, format="%.4f", key=f"nas_pc_{i}_inp")
        with c2:
            q = st.number_input("Quantità", min_value=0,
                                 value=int(st.session_state[f"nas_q_{i}"]),
                                 step=1, key=f"nas_q_{i}_inp")
        cl = st.number_input(f"Chiusura precedente {sym} (opzionale)",
                              min_value=0.0, value=float(st.session_state[f"nas_cl_{i}"]),
                              step=0.01, format="%.4f", key=f"nas_cl_{i}_inp")
        if pc > 0 and q > 0:
            Ka  = pc * q
            st.markdown(f'<div class="carico-box carico-box-nas"><div class="carico-label">📌 Costo totale Kₐ</div>'
                        f'<div class="carico-val">{sym} {Ka:,.2f}</div></div>', unsafe_allow_html=True)

            c_gl, c_lo = st.columns(2)
            with c_gl:
                gl = st.number_input(f"Guadagno target {sym}", min_value=0.0,
                                      value=float(st.session_state[f"nas_gl_{i}"]),
                                      step=1.0, format="%.2f", key=f"nas_gl_{i}_inp")
            with c_lo:
                lo = st.number_input(f"Perdita tollerata {sym}", min_value=0.0,
                                      value=float(st.session_state[f"nas_lo_{i}"]),
                                      step=1.0, format="%.2f", key=f"nas_lo_{i}_inp")

            # ── TARGET GUADAGNO ──
            Pv  = (gl + Ka + 9.0) / q
            pct = ((Pv * q) - Ka) / Ka * 100
            cl_badge = ""
            if cl > 0:
                pct_cl = (Pv - cl) / cl * 100
                sign = "+" if pct_cl >= 0 else ""
                cl_badge = f'<span class="badge-cl">vs chius. {sign}{pct_cl:.2f}%</span>'
            rrow("Commissione vendita (flat)", "$ 9.00")
            thin_hr()
            rrow("Ricavo lordo vendita", f"{sym} {Pv * q:,.2f}")
            st.markdown(
                f'<div class="target-box">'
                f'<div class="carico-label">🎯 Prezzo di vendita target</div>'
                f'<span class="target-val">{sym} {Pv:,.4f}</span>'
                f'<span class="badge-pct">+{pct:.2f}%</span>'
                f'{cl_badge}'
                f'</div>', unsafe_allow_html=True)

            # ── STOP LOSS ──
            if lo > 0:
                Ps    = (Ka - lo - 9.0) / q
                pct_s = ((Ps * q) - Ka) / Ka * 100
                cl_stop = ""
                if cl > 0:
                    pct_cl_s = (Ps - cl) / cl * 100
                    sign = "+" if pct_cl_s >= 0 else ""
                    cl_stop = f'<span class="badge-cl">vs chius. {sign}{pct_cl_s:.2f}%</span>'
                st.markdown(
                    f'<div class="loss-box">'
                    f'<div class="carico-label">🛑 Prezzo stop loss</div>'
                    f'<span class="loss-val">{sym} {Ps:,.4f}</span>'
                    f'<span class="badge-loss">{pct_s:.2f}%</span>'
                    f'{cl_stop}'
                    f'</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="inactive">— inserisci carico e quantità —</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
    st.session_state[f"nas_tk_{i}"] = st.session_state.get(f"nas_tk_{i}_inp", st.session_state[f"nas_tk_{i}"])
    st.session_state[f"nas_pc_{i}"] = st.session_state.get(f"nas_pc_{i}_inp", st.session_state[f"nas_pc_{i}"])
    st.session_state[f"nas_cl_{i}"] = st.session_state.get(f"nas_cl_{i}_inp", st.session_state[f"nas_cl_{i}"])
    st.session_state[f"nas_q_{i}"]  = st.session_state.get(f"nas_q_{i}_inp",  st.session_state[f"nas_q_{i}"])
    st.session_state[f"nas_gl_{i}"] = st.session_state.get(f"nas_gl_{i}_inp", st.session_state[f"nas_gl_{i}"])
    st.session_state[f"nas_lo_{i}"] = st.session_state.get(f"nas_lo_{i}_inp", st.session_state[f"nas_lo_{i}"])

# ─── MAIN LAYOUT ──────────────────────────────────────────────────────────────
col_mil, col_nas = st.columns(2, gap="large")

with col_mil:
    st.markdown('<div class="col-header col-header-mil">🇮🇹 MILANO — EUR</div>', unsafe_allow_html=True)
    for i in range(1, 4):
        with st.container(border=True):
            slot_milano(i)

with col_nas:
    st.markdown('<div class="col-header col-header-nas">🇺🇸 NASDAQ — USD</div>', unsafe_allow_html=True)
    for i in range(1, 4):
        with st.container(border=True):
            slot_nasdaq(i)

# ─── ACTION BAR ───────────────────────────────────────────────────────────────
st.markdown("---")
c1, c2, c3 = st.columns([1, 1, 2])

with c1:
    if st.button("💾  Salva dati", use_container_width=True):
        data_to_save = {}
        for i in range(1, 4):
            data_to_save[f"mil_tk_{i}"] = st.session_state.get(f"mil_tk_{i}_inp", "")
            data_to_save[f"mil_pc_{i}"] = st.session_state.get(f"mil_pc_{i}_inp", 0.0)
            data_to_save[f"mil_cl_{i}"] = st.session_state.get(f"mil_cl_{i}_inp", 0.0)
            data_to_save[f"mil_q_{i}"]  = st.session_state.get(f"mil_q_{i}_inp",  0)
            data_to_save[f"mil_gl_{i}"] = st.session_state.get(f"mil_gl_{i}_inp", 0.0)
            data_to_save[f"mil_lo_{i}"] = st.session_state.get(f"mil_lo_{i}_inp", 0.0)
            data_to_save[f"nas_tk_{i}"] = st.session_state.get(f"nas_tk_{i}_inp", "")
            data_to_save[f"nas_pc_{i}"] = st.session_state.get(f"nas_pc_{i}_inp", 0.0)
            data_to_save[f"nas_cl_{i}"] = st.session_state.get(f"nas_cl_{i}_inp", 0.0)
            data_to_save[f"nas_q_{i}"]  = st.session_state.get(f"nas_q_{i}_inp",  0)
            data_to_save[f"nas_gl_{i}"] = st.session_state.get(f"nas_gl_{i}_inp", 0.0)
            data_to_save[f"nas_lo_{i}"] = st.session_state.get(f"nas_lo_{i}_inp", 0.0)
        save_data(data_to_save)
        st.session_state["_saved_ok"] = True

with c2:
    jpeg_bytes = build_jpeg(None, None)
    fname = f"trade_riepilogo_{datetime.now().strftime('%Y%m%d_%H%M')}.jpg"
    st.download_button(
        label="📸  Scarica JPEG",
        data=jpeg_bytes,
        file_name=fname,
        mime="image/jpeg",
        use_container_width=True
    )

with c3:
    if st.session_state.get("_saved_ok"):
        st.markdown('<div class="save-ok">✓ Dati salvati correttamente</div>', unsafe_allow_html=True)
