import sys
import os
import threading
import socket
import time

# ── Add repo root to path ──────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def _port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def _start_backend():
    if _port_open(8000):
        return
    import uvicorn
    from backend.main import app as _fastapi_app
    uvicorn.run(_fastapi_app, host="0.0.0.0", port=8000, log_level="error")


if "backend_started" not in sys.modules:
    sys.modules["backend_started"] = True
    threading.Thread(target=_start_backend, daemon=True).start()
    for _ in range(20):
        if _port_open(8000):
            break
        time.sleep(0.3)

import json
import streamlit as st
from datetime import date, timedelta
from frontend.utils import (
    generate_qr,
    api_signup, api_login,
    api_get_events, api_get_event, api_get_categories, api_get_zones,
    api_create_booking, api_my_bookings, api_get_booking, api_cancel_booking,
    api_initiate_payment, api_confirm_payment, api_get_payment,
    fmt_price, fmt_date, seats_color_class, status_color,
)

st.set_page_config(
    page_title="LocalPulse",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Category → Unsplash image IDs ────────────────────────────────────────────
CATEGORY_IMAGES = {
    "Music":     ["1540039155733-5bb30b99a842","1493225457124-a3eb161ffa5f","1470225620780-dba8ba36b745","1501386761520-749d2ca2c90a"],
    "Comedy":    ["1527529482837-4698179dc6ce","1585211969224-1e8b31d08231"],
    "Food":      ["1555939594-58d7cb561ad1","1504674900247-0877df9cc836","1414235077428-338989a2e8c0"],
    "Sports":    ["1540747913346-19e32dc3e97e","1459865264687-595d652de67e","1489944440615-453fc2b6a9a9"],
    "Workshop":  ["1531482615713-2afd69097998","1522071820081-009f0129c71c","1559136555-9303baea8ebd"],
    "Arts":      ["1578321272125-c7e2e0b06cf7","1536924430914-91f9e2041b83","1547891654-e71823a3ba53"],
    "Nightlife": ["1516450360452-9312f5e86fc7","1481833761820-0509d3217856","1545128485-c35305837e1c"],
    "Theatre":   ["1507676184212-d03ab07a01bf","1559304285-0e8f1f41cd7f"],
}

def get_event_image(category: str, event_id: int, w: int = 800, h: int = 480) -> str:
    pool = CATEGORY_IMAGES.get(category, CATEGORY_IMAGES["Music"])
    pid  = pool[event_id % len(pool)]
    return f"https://images.unsplash.com/photo-{pid}?w={w}&h={h}&fit=crop&q=80&auto=format"

# Auth background image
AUTH_BG = "https://images.unsplash.com/photo-1540039155733-5bb30b99a842?w=1600&h=900&fit=crop&q=60&auto=format"
HERO_BG  = "https://images.unsplash.com/photo-1501386761520-749d2ca2c90a?w=1600&h=600&fit=crop&q=70&auto=format"

# ── CSS ────────────────────────────────────────────────────────────────────────
DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

* { font-family: 'Inter', sans-serif !important; box-sizing: border-box; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton, [data-testid="stToolbar"] { display: none; }

/* ── Global dark background ── */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: #080808 !important;
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] {
    background-color: #0E0E0E !important;
    border-right: 1px solid #1E1E1E !important;
}
.block-container { padding-top: 0.5rem !important; max-width: 1200px; }

/* ── Inputs ── */
.stTextInput > div > div > input,
.stDateInput > div > div > input {
    background-color: #181818 !important;
    border: 1px solid #2E2E2E !important;
    color: #FFFFFF !important;
    border-radius: 10px !important;
    font-size: 0.9rem !important;
}
.stTextInput > div > div > input::placeholder { color: #555 !important; }
.stNumberInput > div > div > input {
    background-color: #181818 !important;
    border: 1px solid #2E2E2E !important;
    color: #FFFFFF !important;
    border-radius: 10px !important;
}
[data-baseweb="select"] > div {
    background-color: #181818 !important;
    border-color: #2E2E2E !important;
    color: #FFFFFF !important;
}
[data-baseweb="popover"], [data-baseweb="menu"] { background-color: #181818 !important; }
[data-baseweb="option"] { background-color: #181818 !important; color: #FFFFFF !important; }
[data-baseweb="option"]:hover { background-color: #252525 !important; }

/* ── All buttons → coral-red ── */
.stButton > button {
    background: linear-gradient(135deg, #E8456A 0%, #C62A47 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.3px !important;
    padding: 0.55rem 1.5rem !important;
    transition: all 0.25s ease !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #FF5580 0%, #E8456A 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 24px rgba(232, 69, 106, 0.45) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background-color: #111111 !important;
    border-bottom: 1px solid #222 !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    color: #777 !important; font-weight: 600 !important;
    padding: 0.7rem 1.5rem !important;
}
.stTabs [aria-selected="true"] {
    color: #E8456A !important;
    border-bottom: 2px solid #E8456A !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 0 !important; }

/* ── Progress bar ── */
.stProgress > div > div > div > div { background-color: #E8456A !important; }

/* ── Sliders ── */
.stSlider [data-baseweb="slider"] [role="slider"] { background: #E8456A !important; border-color: #E8456A !important; }
.stSlider [data-baseweb="slider"] [data-testid="stSliderTrackActive"] { background: #E8456A !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #111 !important;
    border: 1px solid #1E1E1E !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] summary {
    color: #DDD !important;
    font-weight: 600 !important;
    padding: 0.8rem 1rem !important;
}

/* ── Divider ── */
hr { border-color: #1E1E1E !important; margin: 0.8rem 0 !important; }

/* ── Metric ── */
[data-testid="stMetric"] {
    background: #111; border: 1px solid #1E1E1E;
    border-radius: 12px; padding: 1rem;
}
[data-testid="stMetricValue"] { color: #E8456A !important; }

/* ══════════════════════════════════════════════════════
   ANIMATIONS
══════════════════════════════════════════════════════ */

@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(24px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.55; }
}
@keyframes shimmer {
    0%   { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
@keyframes floatUp {
    0%, 100% { transform: translateY(0px); }
    50%       { transform: translateY(-8px); }
}
@keyframes glowPulse {
    0%, 100% { box-shadow: 0 0 20px rgba(232,69,106,0.3); }
    50%       { box-shadow: 0 0 40px rgba(232,69,106,0.7); }
}

/* ══════════════════════════════════════════════════════
   AUTH PAGE
══════════════════════════════════════════════════════ */

.auth-page-bg {
    position: fixed;
    inset: 0;
    background: linear-gradient(135deg, rgba(8,8,8,0.82) 0%, rgba(30,10,20,0.88) 100%);
    z-index: 0;
}
.auth-glass {
    background: rgba(16,16,16,0.92);
    border: 1px solid rgba(232,69,106,0.2);
    border-radius: 20px;
    padding: 2.5rem 2rem;
    backdrop-filter: blur(20px);
    animation: fadeSlideUp 0.6s ease forwards;
    box-shadow: 0 24px 80px rgba(0,0,0,0.7), 0 0 0 1px rgba(232,69,106,0.1);
}
.auth-logo {
    font-size: 2.4rem;
    font-weight: 900;
    background: linear-gradient(135deg, #E8456A, #FF6B35);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1.5px;
    line-height: 1;
}
.auth-tagline {
    color: #888;
    font-size: 0.9rem;
    margin-top: 0.4rem;
    margin-bottom: 2rem;
    font-weight: 400;
}

/* ══════════════════════════════════════════════════════
   HERO BANNER
══════════════════════════════════════════════════════ */

.hero-banner {
    position: relative;
    width: 100%;
    height: 320px;
    border-radius: 20px;
    overflow: hidden;
    margin-bottom: 2rem;
}
.hero-bg-img {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center 40%;
    transition: transform 8s ease;
}
.hero-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(
        135deg,
        rgba(8,8,8,0.75) 0%,
        rgba(180,30,60,0.45) 50%,
        rgba(8,8,8,0.65) 100%
    );
}
.hero-content {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 2.5rem 3rem;
    animation: fadeSlideUp 0.8s ease forwards;
}
.hero-title {
    font-size: 2.8rem;
    font-weight: 900;
    color: #FFFFFF;
    line-height: 1.1;
    letter-spacing: -1px;
    margin-bottom: 0.6rem;
    text-shadow: 0 2px 20px rgba(0,0,0,0.5);
}
.hero-title span {
    background: linear-gradient(90deg, #E8456A, #FF9A56);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    color: rgba(255,255,255,0.8);
    font-size: 1.05rem;
    font-weight: 400;
    max-width: 480px;
}
.hero-stat-row {
    display: flex;
    gap: 2rem;
    margin-top: 1.5rem;
}
.hero-stat {
    text-align: left;
}
.hero-stat-num {
    font-size: 1.5rem;
    font-weight: 800;
    color: #E8456A;
}
.hero-stat-label {
    font-size: 0.75rem;
    color: rgba(255,255,255,0.6);
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

/* ══════════════════════════════════════════════════════
   EVENT CARDS  (image-first, District style)
══════════════════════════════════════════════════════ */

.ev-card {
    background: #111;
    border: 1px solid #1E1E1E;
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 1.4rem;
    transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
    animation: fadeSlideUp 0.5s ease forwards;
}
.ev-card:hover {
    transform: translateY(-5px);
    border-color: rgba(232,69,106,0.5);
    box-shadow: 0 16px 48px rgba(232,69,106,0.18);
}
.ev-img-wrap {
    position: relative;
    width: 100%;
    height: 190px;
    overflow: hidden;
}
.ev-img-wrap img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center;
    transition: transform 0.4s ease;
    display: block;
}
.ev-card:hover .ev-img-wrap img { transform: scale(1.05); }
.ev-img-gradient {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 70%;
    background: linear-gradient(transparent, rgba(0,0,0,0.88));
    pointer-events: none;
}
.ev-img-top {
    position: absolute;
    top: 0.7rem; left: 0.7rem; right: 0.7rem;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}
.ev-cat-badge {
    display: inline-block;
    background: rgba(232,69,106,0.9);
    color: #fff;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.7px;
    backdrop-filter: blur(8px);
}
.ev-seats-badge {
    display: inline-block;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.3px;
    backdrop-filter: blur(8px);
}
.ev-seats-ok  { background: rgba(34,197,94,0.85); color: #fff; }
.ev-seats-low {
    background: rgba(239,68,68,0.9); color: #fff;
    animation: pulse 1.5s ease-in-out infinite;
}
.ev-seats-sold { background: rgba(100,100,100,0.9); color: #ccc; }
.ev-img-price {
    position: absolute;
    bottom: 0.7rem; right: 0.8rem;
    font-size: 1.15rem;
    font-weight: 800;
    color: #fff;
    text-shadow: 0 2px 8px rgba(0,0,0,0.6);
}
.ev-body {
    padding: 0.9rem 1rem 0.7rem 1rem;
}
.ev-title {
    color: #FFFFFF;
    font-size: 0.98rem;
    font-weight: 700;
    margin: 0 0 0.4rem 0;
    line-height: 1.3;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.ev-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.3rem 0.8rem;
    margin-bottom: 0;
}
.ev-meta span {
    color: #888;
    font-size: 0.76rem;
    white-space: nowrap;
}

/* ══════════════════════════════════════════════════════
   SECTION HEADER
══════════════════════════════════════════════════════ */

.sec-head {
    font-size: 1.4rem;
    font-weight: 800;
    color: #FFFFFF;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.7rem;
}
.sec-head::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, #E8456A33, transparent);
    margin-left: 0.5rem;
}

/* ══════════════════════════════════════════════════════
   CATEGORY CHIPS
══════════════════════════════════════════════════════ */

.chip-row {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-bottom: 1.2rem;
}
.chip {
    display: inline-block;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    border: 1px solid #2A2A2A;
    color: #AAA;
    background: #141414;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.chip.active, .chip:hover {
    background: rgba(232,69,106,0.15);
    border-color: rgba(232,69,106,0.5);
    color: #E8456A;
}

/* ══════════════════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════════════════ */

.sb-logo {
    font-size: 1.6rem;
    font-weight: 900;
    background: linear-gradient(135deg, #E8456A, #FF6B35);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1px;
}
.sb-greeting { color: #666; font-size: 0.8rem; margin-top: 0.15rem; }
.filter-label {
    color: #555;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin: 1rem 0 0.4rem 0;
}

/* ══════════════════════════════════════════════════════
   EVENT DETAIL  –  hero
══════════════════════════════════════════════════════ */

.detail-hero {
    position: relative;
    width: 100%;
    height: 360px;
    border-radius: 20px;
    overflow: hidden;
    margin-bottom: 2rem;
}
.detail-hero img {
    width: 100%; height: 100%;
    object-fit: cover; object-position: center 35%;
    display: block;
}
.detail-hero-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(
        to bottom,
        rgba(0,0,0,0.1) 0%,
        rgba(0,0,0,0.82) 100%
    );
}
.detail-hero-content {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    padding: 2rem;
    animation: fadeSlideUp 0.6s ease forwards;
}

/* ══════════════════════════════════════════════════════
   PRICE / INFO CARD
══════════════════════════════════════════════════════ */

.info-card {
    background: #111;
    border: 1px solid #1E1E1E;
    border-radius: 16px;
    padding: 1.5rem;
}
.info-card-title {
    color: #fff;
    font-weight: 700;
    font-size: 0.95rem;
    margin-bottom: 1rem;
}
.price-big {
    font-size: 2.2rem;
    font-weight: 900;
    color: #E8456A;
}
.price-sub { color: #555; font-size: 0.8rem; }

/* ══════════════════════════════════════════════════════
   TICKET CARD
══════════════════════════════════════════════════════ */

.ticket-wrap {
    background: linear-gradient(135deg, #111 0%, #1A0A12 100%);
    border: 1px solid rgba(232,69,106,0.35);
    border-radius: 20px;
    overflow: hidden;
    position: relative;
    animation: glowPulse 3s ease-in-out infinite;
}
.ticket-stripe {
    height: 4px;
    background: linear-gradient(90deg, #E8456A, #FF6B35, #E8456A);
    background-size: 200% 100%;
    animation: shimmer 2.5s linear infinite;
}
.ticket-body { padding: 1.8rem; }
.ticket-ref {
    color: #E8456A;
    font-size: 1.8rem;
    font-weight: 900;
    letter-spacing: 4px;
}
.ticket-dots {
    border-top: 2px dashed #222;
    margin: 1rem 0;
}

/* ══════════════════════════════════════════════════════
   BOOKING SUMMARY
══════════════════════════════════════════════════════ */

.summary-card {
    background: #111;
    border: 1px solid #1E1E1E;
    border-radius: 16px;
    padding: 1.4rem;
    position: sticky;
    top: 1rem;
}

/* ══════════════════════════════════════════════════════
   PAYMENT  –  UPI QR
══════════════════════════════════════════════════════ */

.qr-frame {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 1rem;
    display: inline-block;
    box-shadow: 0 8px 32px rgba(232,69,106,0.25);
    animation: floatUp 3s ease-in-out infinite;
}

/* ══════════════════════════════════════════════════════
   SUCCESS / ERROR BANNERS
══════════════════════════════════════════════════════ */

.success-banner {
    background: linear-gradient(135deg, rgba(34,197,94,0.15), rgba(34,197,94,0.05));
    border: 1px solid rgba(34,197,94,0.4);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    color: #4ADE80;
    font-weight: 600;
}
.error-banner {
    background: linear-gradient(135deg, rgba(239,68,68,0.15), rgba(239,68,68,0.05));
    border: 1px solid rgba(239,68,68,0.4);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    color: #F87171;
    font-weight: 600;
}

/* ── category badge inline ── */
.cat-badge-inline {
    display: inline-block;
    background: rgba(232,69,106,0.12);
    color: #E8456A;
    border: 1px solid rgba(232,69,106,0.3);
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}
.city-badge {
    display: inline-block;
    background: rgba(255,255,255,0.06);
    color: #AAA;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 11px;
    font-weight: 600;
    margin-left: 6px;
}
</style>
"""

st.markdown(DARK_CSS, unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────

def init_state():
    defaults = {
        "page": "home", "token": None, "user": None,
        "selected_event_id": None, "booking_id": None,
        "payment_id": None, "city_filter": "Bangalore",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

def go(page, **kwargs):
    st.session_state.page = page
    for k, v in kwargs.items():
        st.session_state[k] = v
    st.rerun()

def logout():
    for k in ["token", "user", "page", "selected_event_id", "booking_id", "payment_id"]:
        st.session_state[k] = None
    st.session_state.page = "home"
    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  AUTH PAGE
# ══════════════════════════════════════════════════════════════════════════════

def page_auth():
    # Full-page background image behind everything
    st.markdown(f"""
<style>
.stApp {{
    background-image: url('{AUTH_BG}') !important;
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
}}
.stApp::before {{
    content: '';
    position: fixed;
    inset: 0;
    background: linear-gradient(135deg,
        rgba(8,8,8,0.88) 0%,
        rgba(40,8,20,0.85) 50%,
        rgba(8,8,8,0.92) 100%);
    z-index: 0;
}}
[data-testid="stSidebar"] {{ display: none !important; }}
</style>""", unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("""
<div style="text-align:center; padding:2rem 0 1.5rem 0; animation:fadeSlideUp 0.6s ease;">
  <div class="auth-logo">LocalPulse</div>
  <div class="auth-tagline">Find Your Pulse: Events, Anytime, Nearby</div>
</div>""", unsafe_allow_html=True)

        # Decorative city images strip
        st.markdown(f"""
<div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:6px; border-radius:14px; overflow:hidden; margin-bottom:1.5rem; height:80px;">
  <img src="https://images.unsplash.com/photo-1540039155733-5bb30b99a842?w=300&h=120&fit=crop&q=60" style="width:100%;height:100%;object-fit:cover;">
  <img src="https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=300&h=120&fit=crop&q=60" style="width:100%;height:100%;object-fit:cover;">
  <img src="https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=300&h=120&fit=crop&q=60" style="width:100%;height:100%;object-fit:cover;">
</div>""", unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["Sign In", "Create Account"])

        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            email    = st.text_input("Email", key="login_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="login_password", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In →", key="btn_login"):
                if not email or not password:
                    st.error("Enter email and password.")
                else:
                    with st.spinner("Signing in..."):
                        try:
                            data, status = api_login(email, password)
                            if status == 200:
                                st.session_state.token = data["access_token"]
                                st.session_state.user  = data["user"]
                                st.session_state.city_filter = data["user"]["city"]
                                st.rerun()
                            else:
                                st.error(data.get("detail", "Login failed"))
                        except Exception as e:
                            st.error(f"Cannot connect to API: {e}")

        with tab_signup:
            st.markdown("<br>", unsafe_allow_html=True)
            s_name     = st.text_input("Full Name",   key="sig_name",     placeholder="Arjun Kumar")
            s_email    = st.text_input("Email",       key="sig_email",    placeholder="you@example.com")
            s_phone    = st.text_input("Phone",       key="sig_phone",    placeholder="+91 98765 43210")
            s_password = st.text_input("Password",    type="password", key="sig_password", placeholder="Min 6 characters")
            s_city     = st.selectbox("City",         ["Bangalore", "Chennai"], key="sig_city")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account →", key="btn_signup"):
                if not all([s_name, s_email, s_phone, s_password]):
                    st.error("Fill in all fields.")
                elif len(s_password) < 6:
                    st.error("Password must be ≥ 6 characters.")
                else:
                    with st.spinner("Creating account..."):
                        try:
                            data, status = api_signup(s_name, s_email, s_phone, s_password, s_city)
                            if status == 200:
                                st.session_state.token = data["access_token"]
                                st.session_state.user  = data["user"]
                                st.session_state.city_filter = data["user"]["city"]
                                st.rerun()
                            else:
                                st.error(data.get("detail", "Signup failed"))
                        except Exception as e:
                            st.error(f"Cannot connect to API: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

def render_sidebar():
    with st.sidebar:
        st.markdown(f"""
<div style="padding:0.5rem 0 0.2rem 0;">
  <div class="sb-logo">LocalPulse</div>
  <div class="sb-greeting">Hey, {st.session_state.user["name"].split()[0]} 👋</div>
</div>""", unsafe_allow_html=True)
        st.markdown("---")

        if st.button("🏠  Discover Events", key="nav_home"):
            go("home")
        if st.button("🎟️  My Bookings", key="nav_bookings"):
            go("my_bookings")

        st.markdown("---")
        st.markdown('<div class="filter-label">Filters</div>', unsafe_allow_html=True)

        city = st.selectbox("City", ["Bangalore", "Chennai"],
                            index=0 if st.session_state.city_filter == "Bangalore" else 1,
                            key="sidebar_city")
        st.session_state.city_filter = city

        try:
            cats, _ = api_get_categories()
            cat_options = ["All"] + cats
        except Exception:
            cat_options = ["All"]
        category = st.selectbox("Category", cat_options, key="sidebar_cat")

        try:
            zones, _ = api_get_zones(city)
            zone_options = ["All"] + zones
        except Exception:
            zone_options = ["All"]
        zone = st.selectbox("Zone", zone_options, key="sidebar_zone")

        st.markdown('<div class="filter-label">Date Range</div>', unsafe_allow_html=True)
        today    = date.today()
        date_from = st.date_input("From", value=today,                  key="sidebar_date_from", label_visibility="collapsed")
        date_to   = st.date_input("To",   value=today + timedelta(days=30), key="sidebar_date_to",   label_visibility="collapsed")

        price_range = st.slider("Price (₹)", 0, 2000, (0, 2000), step=50, key="sidebar_price")

        st.markdown("---")
        if st.button("🚪  Sign Out", key="btn_logout"):
            logout()

    return {
        "city":      city,
        "category":  None if category == "All" else category,
        "zone":      None if zone == "All" else zone,
        "date_from": str(date_from),
        "date_to":   str(date_to),
        "min_price": price_range[0] if price_range[0] > 0 else None,
        "max_price": price_range[1] if price_range[1] < 2000 else None,
    }


# ══════════════════════════════════════════════════════════════════════════════
#  HOME / DISCOVERY
# ══════════════════════════════════════════════════════════════════════════════

def page_home(filters: dict):
    city = filters["city"]

    # ── Hero banner ──
    st.markdown(f"""
<div class="hero-banner">
  <img class="hero-bg-img" src="{HERO_BG}" alt="hero">
  <div class="hero-overlay"></div>
  <div class="hero-content">
    <div class="hero-title">What's On in<br><span>{city}</span></div>
    <div class="hero-sub">Discover live concerts, comedy shows, food festivals & more — all near you.</div>
    <div class="hero-stat-row">
      <div class="hero-stat"><div class="hero-stat-num">30+</div><div class="hero-stat-label">Events</div></div>
      <div class="hero-stat"><div class="hero-stat-num">2</div><div class="hero-stat-label">Cities</div></div>
      <div class="hero-stat"><div class="hero-stat-num">8</div><div class="hero-stat-label">Categories</div></div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── Search bar ──
    search = st.text_input("search_bar", placeholder="🔍  Search events, venues, artists...",
                           label_visibility="collapsed", key="search_input")

    # ── Load events ──
    with st.spinner(""):
        try:
            params = {**filters}
            if search:
                params["search"] = search
            events, status = api_get_events(**params)
        except Exception as e:
            st.error(f"Cannot reach API. Make sure the backend is running. ({e})")
            return

    if not events or (isinstance(events, dict) and "detail" in events):
        st.markdown("""
<div style="text-align:center; color:#444; padding:4rem 0;">
  <div style="font-size:4rem; margin-bottom:1rem;">🔍</div>
  <p style="font-size:1.1rem; color:#555;">No events match your filters.</p>
  <p style="font-size:0.85rem; color:#444;">Try adjusting the category, zone, or date range.</p>
</div>""", unsafe_allow_html=True)
        return

    st.markdown(f'<div class="sec-head">🔥 {len(events)} Events Found</div>', unsafe_allow_html=True)

    # ── 2-column card grid ──
    cols = st.columns(2, gap="medium")
    for i, ev in enumerate(events):
        with cols[i % 2]:
            img_url = get_event_image(ev["category"], ev["id"])
            avail   = ev["available_seats"]
            if avail == 0:
                seats_cls, seats_txt = "ev-seats-sold", "Sold Out"
            elif avail < 10:
                seats_cls, seats_txt = "ev-seats-low", f"🔥 {avail} left"
            else:
                seats_cls, seats_txt = "ev-seats-ok", f"✓ {avail} seats"

            st.markdown(f"""
<div class="ev-card">
  <div class="ev-img-wrap">
    <img src="{img_url}" alt="{ev['title']}" loading="lazy">
    <div class="ev-img-gradient"></div>
    <div class="ev-img-top">
      <span class="ev-cat-badge">{ev['category']}</span>
      <span class="ev-seats-badge {seats_cls}">{seats_txt}</span>
    </div>
    <div class="ev-img-price">{fmt_price(ev['price'])}</div>
  </div>
  <div class="ev-body">
    <div class="ev-title">{ev['title']}</div>
    <div class="ev-meta">
      <span>📍 {ev['zone']}</span>
      <span>📅 {fmt_date(ev['event_date'])}</span>
      <span>⏰ {ev['event_time']}</span>
    </div>
  </div>
</div>""", unsafe_allow_html=True)
            if st.button("View Details →", key=f"ev_{ev['id']}"):
                go("event_detail", selected_event_id=ev["id"])


# ══════════════════════════════════════════════════════════════════════════════
#  EVENT DETAIL
# ══════════════════════════════════════════════════════════════════════════════

def page_event_detail():
    if st.button("← Back", key="back_detail"):
        go("home")

    event_id = st.session_state.selected_event_id
    if not event_id:
        st.error("No event selected.")
        return

    with st.spinner("Loading..."):
        try:
            event, status = api_get_event(event_id)
        except Exception as e:
            st.error(f"Error: {e}"); return

    if status != 200 or "detail" in event:
        st.error("Event not found."); return

    img_url = get_event_image(event["category"], event_id, w=1400, h=600)
    avail   = event["available_seats"]
    total   = event["total_seats"]
    pct     = avail / total if total > 0 else 0

    # ── Hero with image ──
    st.markdown(f"""
<div class="detail-hero">
  <img src="{img_url}" alt="{event['title']}">
  <div class="detail-hero-overlay"></div>
  <div class="detail-hero-content">
    <div style="margin-bottom:0.6rem;">
      <span class="cat-badge-inline">{event['category']}</span>
      <span class="city-badge">{event['city']} · {event['zone']}</span>
    </div>
    <h1 style="color:#FFF;font-size:2rem;font-weight:900;margin:0 0 0.4rem 0;text-shadow:0 2px 16px rgba(0,0,0,0.5);">{event['title']}</h1>
    <p style="color:rgba(255,255,255,0.75);font-size:0.9rem;margin:0;">By {event['organizer']}</p>
  </div>
</div>""", unsafe_allow_html=True)

    col_left, col_right = st.columns([2, 1], gap="large")

    with col_left:
        st.markdown('<div class="sec-head" style="font-size:1.1rem;">About</div>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#CCCCCC;line-height:1.8;font-size:0.92rem;">{event["description"]}</p>', unsafe_allow_html=True)

        st.markdown('<div class="sec-head" style="font-size:1.1rem; margin-top:1.5rem;">Details</div>', unsafe_allow_html=True)
        for icon, label, value in [
            ("📍","Venue",   event["venue"]),
            ("🗺️","Zone",    f"{event['zone']}, {event['city']}"),
            ("📅","Date",    fmt_date(event["event_date"])),
            ("⏰","Time",    event["event_time"]),
            ("👤","Organizer", event["organizer"]),
        ]:
            st.markdown(f"""
<div style="display:flex;gap:0.8rem;margin-bottom:0.6rem;align-items:flex-start;">
  <span style="color:#E8456A;font-size:1rem;min-width:1.4rem;">{icon}</span>
  <div>
    <div style="color:#555;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.8px;">{label}</div>
    <div style="color:#EEE;font-size:0.88rem;margin-top:0.1rem;">{value}</div>
  </div>
</div>""", unsafe_allow_html=True)

    with col_right:
        seats_color = "#E8456A" if avail < 10 else "#4ADE80" if avail > 0 else "#888"
        st.markdown(f"""
<div class="info-card">
  <div style="margin-bottom:1rem;">
    <div style="color:#555;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:0.3rem;">Price per person</div>
    <div>
      <span class="price-big">{fmt_price(event['price'])}</span>
      <span class="price-sub"> + 5% fee</span>
    </div>
  </div>
  <hr>
  <div style="margin-bottom:0.8rem;">
    <div style="color:#555;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:0.4rem;">Seat Availability</div>
    <div style="color:{seats_color};font-weight:700;font-size:1.1rem;">{avail} / {total} seats</div>
  </div>
</div>""", unsafe_allow_html=True)

        st.progress(pct)
        st.markdown("<br>", unsafe_allow_html=True)

        if avail > 0:
            if st.button("🎟️  Book Now", key="btn_book"):
                go("booking", selected_event_id=event_id)
        else:
            st.markdown('<div class="error-banner" style="text-align:center;">😔 Sold Out</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  BOOKING
# ══════════════════════════════════════════════════════════════════════════════

def page_booking():
    if st.button("← Back to Event", key="back_booking"):
        go("event_detail")

    event_id = st.session_state.selected_event_id
    if not event_id:
        st.error("No event selected."); return

    with st.spinner("Loading..."):
        try:
            event, _ = api_get_event(event_id)
        except Exception as e:
            st.error(f"Error: {e}"); return

    img_url = get_event_image(event["category"], event_id, w=1200, h=300)

    # mini hero
    st.markdown(f"""
<div style="position:relative;height:130px;border-radius:14px;overflow:hidden;margin-bottom:1.5rem;">
  <img src="{img_url}" style="width:100%;height:100%;object-fit:cover;object-position:center 40%;">
  <div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,0.8),rgba(0,0,0,0.3));display:flex;align-items:center;padding:1.5rem 2rem;gap:1rem;">
    <div>
      <div style="color:#FFF;font-size:1.2rem;font-weight:800;">{event['title']}</div>
      <div style="color:rgba(255,255,255,0.65);font-size:0.8rem;margin-top:0.2rem;">
        📅 {fmt_date(event['event_date'])} · ⏰ {event['event_time']} · 📍 {event['venue'][:40]}
      </div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    col_form, col_sum = st.columns([3, 2], gap="large")

    with col_form:
        st.markdown('<div class="sec-head" style="font-size:1.1rem;">Your Seats</div>', unsafe_allow_html=True)
        seats = st.number_input("Number of Seats", min_value=1,
                                max_value=min(20, event["available_seats"]),
                                value=1, key="booking_seats")

        st.markdown(f'<p style="color:#888;font-size:0.82rem;margin:0.8rem 0 0.4rem 0;">Attendee names ({int(seats)} required)</p>', unsafe_allow_html=True)
        attendee_names = []
        for i in range(int(seats)):
            n = st.text_input(f"Person {i+1}", key=f"att_{i}", placeholder=f"Full name of person {i+1}")
            attendee_names.append(n)

    with col_sum:
        base  = seats * event["price"]
        fee   = round(base * 0.05, 2)
        total = round(base + fee, 2)
        st.markdown(f"""
<div class="summary-card">
  <div class="info-card-title">Price Breakdown</div>
  <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem;">
    <span style="color:#888;font-size:0.85rem;">{int(seats)} × {fmt_price(event['price'])}</span>
    <span style="color:#EEE;">{fmt_price(base)}</span>
  </div>
  <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem;">
    <span style="color:#888;font-size:0.85rem;">Convenience (5%)</span>
    <span style="color:#EEE;">{fmt_price(fee)}</span>
  </div>
  <hr>
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <span style="color:#FFF;font-weight:700;">Total</span>
    <span style="color:#E8456A;font-size:1.4rem;font-weight:900;">{fmt_price(total)}</span>
  </div>
  <p style="color:#444;font-size:0.75rem;margin-top:0.6rem;">{event['available_seats']} seats available</p>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Proceed to Payment →", key="btn_pay"):
        if not all(attendee_names) or any(n.strip() == "" for n in attendee_names):
            st.error("Enter all attendee names.")
        else:
            with st.spinner("Creating booking..."):
                try:
                    data, status = api_create_booking(st.session_state.token, event_id,
                                                       int(seats), attendee_names)
                    if status == 200:
                        go("payment", booking_id=data["id"])
                    else:
                        st.error(data.get("detail", "Booking failed"))
                except Exception as e:
                    st.error(f"Error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  PAYMENT
# ══════════════════════════════════════════════════════════════════════════════

def page_payment():
    if st.button("← Back", key="back_pay"):
        go("booking")

    booking_id = st.session_state.booking_id
    if not booking_id:
        st.error("No booking."); return

    with st.spinner("Loading..."):
        try:
            booking, status = api_get_booking(st.session_state.token, booking_id)
        except Exception as e:
            st.error(f"Error: {e}"); return

    if status != 200:
        st.error("Booking not found."); return

    try:
        event, _ = api_get_event(booking["event_id"])
    except Exception:
        event = None

    st.markdown('<div class="sec-head">💳 Complete Payment</div>', unsafe_allow_html=True)

    col_pay, col_sum = st.columns([3, 2], gap="large")

    with col_pay:
        tab_upi, tab_card, tab_wallet = st.tabs(["📱 UPI", "💳 Card", "👛 Wallet"])

        with tab_upi:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<p style="color:#888;font-size:0.88rem;">Scan with GPay, PhonePe, Paytm or any UPI app</p>', unsafe_allow_html=True)

            if st.button("Generate QR Code", key="btn_qr"):
                with st.spinner("Generating..."):
                    try:
                        pd, ps = api_initiate_payment(st.session_state.token, booking_id, "UPI")
                        if ps == 200:
                            st.session_state.payment_id = pd["id"]
                        else:
                            st.error(pd.get("detail", "Failed"))
                    except Exception as e:
                        st.error(f"Error: {e}")

            if st.session_state.payment_id:
                try:
                    pd, _ = api_get_payment(st.session_state.token, booking_id)
                    qr_bytes = generate_qr(pd["qr_data"])
                    col_c, col_q, col_c2 = st.columns([1, 2, 1])
                    with col_q:
                        st.markdown('<div class="qr-frame">', unsafe_allow_html=True)
                        st.image(qr_bytes, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.markdown(f'<p style="color:#555;font-size:0.72rem;text-align:center;word-break:break-all;margin-top:0.5rem;">{pd["qr_data"][:60]}...</p>', unsafe_allow_html=True)
                except Exception:
                    pass
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("✅  I have paid", key="btn_done"):
                    _confirm_pay()

        with tab_card:
            st.markdown("<br>", unsafe_allow_html=True)
            st.text_input("Card Number",  placeholder="4242 4242 4242 4242", key="cnum",  label_visibility="collapsed")
            c1, c2 = st.columns(2)
            with c1: st.text_input("Expiry", placeholder="MM / YY",  key="cexp",  label_visibility="collapsed")
            with c2: st.text_input("CVV",    placeholder="•••", type="password", key="ccvv", label_visibility="collapsed")
            st.text_input("Name on Card",    placeholder="ARJUN KUMAR", key="cname", label_visibility="collapsed")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"Pay {fmt_price(booking['total_amount'])} →", key="btn_card"):
                with st.spinner("Processing..."):
                    try:
                        pd, ps = api_initiate_payment(st.session_state.token, booking_id, "Card")
                        if ps == 200:
                            st.session_state.payment_id = pd["id"]
                            _confirm_pay()
                    except Exception as e:
                        st.error(f"Error: {e}")

        with tab_wallet:
            st.markdown("<br>", unsafe_allow_html=True)
            wallet = st.radio("Wallet", ["📱 PhonePe", "🟢 Google Pay", "🔵 Paytm"],
                              key="wallet_pick", label_visibility="collapsed")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"Pay {fmt_price(booking['total_amount'])} with {wallet}", key="btn_wallet"):
                with st.spinner("Processing..."):
                    try:
                        pd, ps = api_initiate_payment(st.session_state.token, booking_id, "Wallet")
                        if ps == 200:
                            st.session_state.payment_id = pd["id"]
                            _confirm_pay()
                    except Exception as e:
                        st.error(f"Error: {e}")

    with col_sum:
        ev_title  = event["title"]      if event else "Event"
        ev_date   = fmt_date(event["event_date"]) if event else ""
        ev_img    = get_event_image(event["category"], event["id"]) if event else ""
        ev_emoji  = event.get("image_emoji", "🎫") if event else "🎫"

        st.markdown(f"""
<div class="summary-card">
  <div class="info-card-title">Order Summary</div>
  {"<div style='border-radius:10px;overflow:hidden;height:110px;margin-bottom:1rem;'><img src='" + ev_img + "' style='width:100%;height:100%;object-fit:cover;'></div>" if ev_img else ""}
  <div style="margin-bottom:1rem;padding-bottom:1rem;border-bottom:1px solid #1E1E1E;">
    <div style="color:#FFF;font-weight:700;font-size:0.92rem;">{ev_title}</div>
    <div style="color:#666;font-size:0.8rem;margin-top:0.2rem;">{ev_date}</div>
  </div>
  <div style="display:flex;justify-content:space-between;margin-bottom:0.4rem;">
    <span style="color:#888;font-size:0.83rem;">Seats</span>
    <span style="color:#EEE;">{booking['seats']}</span>
  </div>
  <div style="display:flex;justify-content:space-between;margin-bottom:0.4rem;">
    <span style="color:#888;font-size:0.83rem;">Booking Ref</span>
    <span style="color:#E8456A;font-weight:700;font-size:0.83rem;">{booking['booking_ref']}</span>
  </div>
  <hr>
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <span style="color:#FFF;font-weight:700;">Total</span>
    <span style="color:#E8456A;font-size:1.4rem;font-weight:900;">{fmt_price(booking['total_amount'])}</span>
  </div>
</div>""", unsafe_allow_html=True)


def _confirm_pay():
    pid = st.session_state.payment_id
    if not pid:
        st.error("No payment initiated."); return
    try:
        data, status = api_confirm_payment(st.session_state.token, pid)
        if status == 200:
            st.markdown('<div class="success-banner">🎉 Payment successful! Redirecting…</div>', unsafe_allow_html=True)
            time.sleep(0.8)
            go("ticket")
        else:
            st.error(data.get("detail", "Payment confirmation failed"))
    except Exception as e:
        st.error(f"Error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  TICKET
# ══════════════════════════════════════════════════════════════════════════════

def page_ticket():
    booking_id = st.session_state.booking_id
    if not booking_id:
        st.error("No booking."); return

    try:
        booking, _ = api_get_booking(st.session_state.token, booking_id)
        event, _   = api_get_event(booking["event_id"])
    except Exception as e:
        st.error(f"Error: {e}"); return

    img_url = get_event_image(event["category"], event["id"], w=1400, h=400)

    # confetti-style header
    st.markdown(f"""
<div style="text-align:center;padding:2rem 0 1rem 0;animation:fadeSlideUp 0.6s ease;">
  <div style="font-size:3.5rem;animation:floatUp 2s ease-in-out infinite;">🎉</div>
  <h1 style="color:#4ADE80;font-weight:900;font-size:2.2rem;margin:0.4rem 0 0.3rem 0;">Booking Confirmed!</h1>
  <p style="color:#666;">Your tickets are locked in. See you there!</p>
</div>""", unsafe_allow_html=True)

    attendees = []
    try:
        attendees = json.loads(booking["attendee_names"])
    except Exception:
        pass

    col_ticket, col_qr = st.columns([3, 2], gap="large")

    with col_ticket:
        # event image strip
        st.markdown(f"""
<div style="border-radius:14px;overflow:hidden;height:120px;margin-bottom:1.2rem;">
  <img src="{img_url}" style="width:100%;height:100%;object-fit:cover;object-position:center 35%;">
</div>""", unsafe_allow_html=True)

        atts_html = "".join(f'<div style="color:#BBB;font-size:0.85rem;margin:0.15rem 0;">• {n}</div>' for n in attendees)

        st.markdown(f"""
<div class="ticket-wrap">
  <div class="ticket-stripe"></div>
  <div class="ticket-body">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1.2rem;">
      <div>
        <span class="cat-badge-inline">{event.get('category','')}</span>
        <h2 style="color:#FFF;font-size:1.3rem;font-weight:800;margin:0.5rem 0 0.2rem 0;">{event['title']}</h2>
        <p style="color:#666;font-size:0.82rem;margin:0;">By {event['organizer']}</p>
      </div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1.2rem;">
      <div>
        <div style="color:#555;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.8px;">Date</div>
        <div style="color:#FFF;font-weight:600;font-size:0.9rem;margin-top:0.2rem;">{fmt_date(event['event_date'])}</div>
      </div>
      <div>
        <div style="color:#555;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.8px;">Time</div>
        <div style="color:#FFF;font-weight:600;font-size:0.9rem;margin-top:0.2rem;">{event['event_time']}</div>
      </div>
      <div>
        <div style="color:#555;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.8px;">Venue</div>
        <div style="color:#FFF;font-weight:600;font-size:0.9rem;margin-top:0.2rem;">{event['venue']}</div>
      </div>
      <div>
        <div style="color:#555;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.8px;">Seats</div>
        <div style="color:#FFF;font-weight:600;font-size:0.9rem;margin-top:0.2rem;">{booking['seats']}</div>
      </div>
    </div>
    <div class="ticket-dots"></div>
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <div>
        <div style="color:#555;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:0.3rem;">Booking Reference</div>
        <div class="ticket-ref">{booking['booking_ref']}</div>
      </div>
      <div style="text-align:right;">
        <div style="color:#555;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:0.2rem;">Amount Paid</div>
        <div style="color:#4ADE80;font-size:1.2rem;font-weight:800;">{fmt_price(booking['total_amount'])}</div>
      </div>
    </div>
    {("<div style='margin-top:1rem;padding-top:1rem;border-top:1px solid #1E1E1E;'><div style='color:#555;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:0.4rem;'>Attendees</div>" + atts_html + "</div>") if attendees else ""}
  </div>
</div>""", unsafe_allow_html=True)

    with col_qr:
        st.markdown("""
<div style="display:flex;flex-direction:column;align-items:center;padding:1rem 0;">
  <p style="color:#888;text-align:center;font-size:0.82rem;margin-bottom:1rem;">Show at entry gate</p>
</div>""", unsafe_allow_html=True)
        qr_bytes = generate_qr(booking["booking_ref"])
        col_q1, col_q2, col_q3 = st.columns([0.5, 3, 0.5])
        with col_q2:
            st.markdown('<div class="qr-frame">', unsafe_allow_html=True)
            st.image(qr_bytes, use_container_width=True, caption=booking["booking_ref"])
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🎟️  My Bookings", key="btn_myb"):
            go("my_bookings")
    with col_b:
        if st.button("🏠  Discover More", key="btn_more"):
            go("home")


# ══════════════════════════════════════════════════════════════════════════════
#  MY BOOKINGS
# ══════════════════════════════════════════════════════════════════════════════

def page_my_bookings():
    st.markdown('<div class="sec-head">🎟️ My Bookings</div>', unsafe_allow_html=True)

    with st.spinner(""):
        try:
            bookings, status = api_my_bookings(st.session_state.token)
        except Exception as e:
            st.error(f"Error: {e}"); return

    if not bookings:
        st.markdown("""
<div style="text-align:center;color:#444;padding:4rem 0;">
  <div style="font-size:4rem;margin-bottom:1rem;">🎫</div>
  <p style="color:#555;font-size:1rem;">No bookings yet.</p>
  <p style="color:#444;font-size:0.85rem;">Find something exciting and book your first event!</p>
</div>""", unsafe_allow_html=True)
        if st.button("Discover Events", key="btn_disc"):
            go("home")
        return

    for booking in bookings:
        try:
            event, _  = api_get_event(booking["event_id"])
            ev_title  = event["title"]
            ev_date   = fmt_date(event["event_date"])
            ev_venue  = event["venue"]
            ev_cat    = event["category"]
            ev_img    = get_event_image(ev_cat, event["id"], w=600, h=200)
        except Exception:
            ev_title = f"Event #{booking['event_id']}"
            ev_date = ev_venue = ev_cat = ""
            ev_img = ""

        sc  = status_color(booking["status"])
        slabel = booking["status"].upper()
        attendees = []
        try:
            attendees = json.loads(booking["attendee_names"])
        except Exception:
            pass

        with st.expander(f"  {ev_title}  ·  {ev_date}  ·  {slabel}", expanded=False):
            c_info, c_act = st.columns([3, 1])

            with c_info:
                if ev_img:
                    st.markdown(f'<div style="border-radius:10px;overflow:hidden;height:90px;margin-bottom:1rem;"><img src="{ev_img}" style="width:100%;height:100%;object-fit:cover;"></div>', unsafe_allow_html=True)

                st.markdown(f"""
<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.8rem;margin-bottom:0.8rem;">
  <div>
    <div style="color:#555;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.8px;">Booking Ref</div>
    <div style="color:#E8456A;font-weight:700;letter-spacing:2px;font-size:0.9rem;">{booking['booking_ref']}</div>
  </div>
  <div>
    <div style="color:#555;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.8px;">Status</div>
    <div style="color:{sc};font-weight:700;">{slabel}</div>
  </div>
  <div>
    <div style="color:#555;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.8px;">Seats</div>
    <div style="color:#EEE;">{booking['seats']}</div>
  </div>
  <div>
    <div style="color:#555;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.8px;">Paid</div>
    <div style="color:#EEE;">{fmt_price(booking['total_amount'])}</div>
  </div>
</div>""", unsafe_allow_html=True)

                if attendees:
                    st.markdown('<div style="color:#555;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:0.3rem;">Attendees</div>', unsafe_allow_html=True)
                    for n in attendees:
                        st.markdown(f'<div style="color:#BBB;font-size:0.83rem;margin:0.1rem 0;">• {n}</div>', unsafe_allow_html=True)

                if booking["status"] == "confirmed":
                    st.markdown("<br>", unsafe_allow_html=True)
                    qr = generate_qr(booking["booking_ref"])
                    c1, c2, c3 = st.columns([1, 2, 1])
                    with c2:
                        st.image(qr, use_container_width=True, caption="Entry QR")

            with c_act:
                if booking["status"] != "cancelled":
                    if st.button("View Ticket", key=f"vt_{booking['id']}"):
                        st.session_state.booking_id = booking["id"]
                        go("ticket")

                if booking["status"] == "pending" and booking["payment_status"] == "pending":
                    if st.button("Pay Now", key=f"pn_{booking['id']}"):
                        st.session_state.booking_id = booking["id"]
                        st.session_state.selected_event_id = booking["event_id"]
                        go("payment")

                if booking["status"] != "cancelled":
                    if st.button("Cancel", key=f"cx_{booking['id']}"):
                        with st.spinner("Cancelling..."):
                            try:
                                data, s = api_cancel_booking(st.session_state.token, booking["id"])
                                if s == 200:
                                    st.success("Cancelled.")
                                    st.rerun()
                                else:
                                    st.error(data.get("detail", "Failed"))
                            except Exception as e:
                                st.error(f"Error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  ROUTER
# ══════════════════════════════════════════════════════════════════════════════

def main():
    if not st.session_state.token:
        page_auth()
        return

    filters = render_sidebar()
    page    = st.session_state.page

    if page == "home":          page_home(filters)
    elif page == "event_detail": page_event_detail()
    elif page == "booking":     page_booking()
    elif page == "payment":     page_payment()
    elif page == "ticket":      page_ticket()
    elif page == "my_bookings": page_my_bookings()
    else:                       page_home(filters)


if __name__ == "__main__":
    main()
else:
    main()
