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
    """Start FastAPI + Uvicorn in a daemon thread (used on Streamlit Cloud)."""
    if _port_open(8000):
        return  # already running (local dev with separate terminal)
    import uvicorn
    from backend.main import app as _fastapi_app
    uvicorn.run(_fastapi_app, host="0.0.0.0", port=8000, log_level="error")


# Start backend once per process (Streamlit reruns share the process)
if "backend_started" not in sys.modules:
    sys.modules["backend_started"] = True          # sentinel
    threading.Thread(target=_start_backend, daemon=True).start()
    # Give the server a moment to bind before the first API call
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

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="LocalPulse",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── District-inspired Dark CSS ─────────────────────────────────────────────────

DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

* { font-family: 'Inter', sans-serif !important; }

/* Hide Streamlit defaults */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* Dark background everywhere */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: #0A0A0A !important;
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] {
    background-color: #111111 !important;
    border-right: 1px solid #2A2A2A !important;
}
.block-container { padding-top: 1rem !important; }

/* Input fields */
.stTextInput > div > div > input,
.stTextInput > div > div > input:focus,
.stSelectbox > div > div,
.stDateInput > div > div > input {
    background-color: #1A1A1A !important;
    border: 1px solid #2A2A2A !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
}
.stTextInput > div > div > input::placeholder { color: #666666 !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #E8456A, #C62A47) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.5rem 2rem !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #FF5580, #E8456A) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(232, 69, 106, 0.4) !important;
}

/* Cards */
.event-card {
    background: #161616;
    border: 1px solid #2A2A2A;
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    cursor: pointer;
    transition: all 0.2s ease;
}
.event-card:hover {
    border-color: #E8456A;
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(232, 69, 106, 0.15);
}

/* Category badge */
.category-badge {
    display: inline-block;
    background: rgba(232, 69, 106, 0.15);
    color: #E8456A;
    border: 1px solid rgba(232, 69, 106, 0.3);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Seats badge */
.seats-low { color: #FF4444 !important; font-weight: 700; }
.seats-ok { color: #44FF88 !important; font-weight: 600; }

/* Price */
.price-tag {
    color: #E8456A;
    font-size: 1.3rem;
    font-weight: 700;
}

/* Section headers */
.section-header {
    color: #FFFFFF;
    font-size: 1.5rem;
    font-weight: 800;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #E8456A;
}

/* Logo */
.logo-text {
    font-size: 1.8rem;
    font-weight: 900;
    color: #E8456A;
    letter-spacing: -1px;
}

/* Auth form container */
.auth-container {
    max-width: 420px;
    margin: 2rem auto;
    background: #161616;
    border: 1px solid #2A2A2A;
    border-radius: 16px;
    padding: 2.5rem;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background-color: #161616 !important;
    border-bottom: 1px solid #2A2A2A !important;
}
.stTabs [data-baseweb="tab"] {
    color: #A0A0A0 !important;
    font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
    color: #E8456A !important;
    border-bottom-color: #E8456A !important;
}

/* Divider */
hr { border-color: #2A2A2A !important; }

/* Selectbox dropdown */
[data-baseweb="select"] > div {
    background-color: #1A1A1A !important;
    border-color: #2A2A2A !important;
    color: #FFFFFF !important;
}
[data-baseweb="popover"] { background-color: #1A1A1A !important; }
[data-baseweb="menu"] { background-color: #1A1A1A !important; }
[data-baseweb="option"] { background-color: #1A1A1A !important; color: #FFFFFF !important; }
[data-baseweb="option"]:hover { background-color: #2A2A2A !important; }

/* Metric */
[data-testid="stMetric"] {
    background: #161616;
    border: 1px solid #2A2A2A;
    border-radius: 10px;
    padding: 1rem;
}
[data-testid="stMetricValue"] { color: #E8456A !important; }

/* Sidebar nav items */
.sidebar-nav-item {
    padding: 0.7rem 1rem;
    border-radius: 8px;
    cursor: pointer;
    color: #A0A0A0;
    font-weight: 500;
    transition: all 0.2s;
    margin-bottom: 0.3rem;
}
.sidebar-nav-item:hover, .sidebar-nav-item.active {
    background: rgba(232, 69, 106, 0.1);
    color: #E8456A;
}

/* Success/error messages */
.success-box {
    background: rgba(68, 255, 136, 0.1);
    border: 1px solid #44FF88;
    border-radius: 8px;
    padding: 1rem;
    color: #44FF88;
}
.error-box {
    background: rgba(255, 68, 68, 0.1);
    border: 1px solid #FF4444;
    border-radius: 8px;
    padding: 1rem;
    color: #FF4444;
}

/* QR code container */
.qr-container {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 1rem;
    display: inline-block;
    margin: 0 auto;
    text-align: center;
}

/* Ticket card */
.ticket-card {
    background: linear-gradient(135deg, #1A1A1A, #222222);
    border: 1px solid #E8456A;
    border-radius: 16px;
    padding: 2rem;
    position: relative;
    overflow: hidden;
}
.ticket-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #E8456A, #FF6B35);
}

/* Number input */
.stNumberInput > div > div > input {
    background-color: #1A1A1A !important;
    border: 1px solid #2A2A2A !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
}

/* Progress bar */
.stProgress > div > div > div > div {
    background-color: #E8456A !important;
}

/* Expander */
.streamlit-expanderHeader {
    background-color: #161616 !important;
    color: #FFFFFF !important;
    border: 1px solid #2A2A2A !important;
    border-radius: 8px !important;
}
.streamlit-expanderContent {
    background-color: #161616 !important;
    border: 1px solid #2A2A2A !important;
}
</style>
"""

st.markdown(DARK_CSS, unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────

def init_state():
    defaults = {
        "page": "home",
        "token": None,
        "user": None,
        "selected_event_id": None,
        "booking_id": None,
        "payment_id": None,
        "city_filter": "Bangalore",
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
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.page = "home"
    st.rerun()


# ── Auth page ─────────────────────────────────────────────────────────────────

def page_auth():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            '<div style="text-align:center; margin-bottom:0.5rem;">'
            '<span class="logo-text">LocalPulse</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p style="text-align:center; color:#A0A0A0; margin-bottom:2rem; font-size:1rem;">'
            'Find Your Pulse: Events, Anytime, Nearby'
            '</p>',
            unsafe_allow_html=True,
        )

        tab_login, tab_signup = st.tabs(["Sign In", "Create Account"])

        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            email = st.text_input("Email", key="login_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="login_password", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In", key="btn_login"):
                if not email or not password:
                    st.error("Please enter email and password.")
                else:
                    with st.spinner("Signing in..."):
                        try:
                            data, status = api_login(email, password)
                            if status == 200:
                                st.session_state.token = data["access_token"]
                                st.session_state.user = data["user"]
                                st.session_state.city_filter = data["user"]["city"]
                                st.rerun()
                            else:
                                st.error(data.get("detail", "Login failed"))
                        except Exception as e:
                            st.error(f"Cannot connect to backend: {e}")

        with tab_signup:
            st.markdown("<br>", unsafe_allow_html=True)
            s_name = st.text_input("Full Name", key="sig_name", placeholder="Arjun Kumar")
            s_email = st.text_input("Email", key="sig_email", placeholder="you@example.com")
            s_phone = st.text_input("Phone", key="sig_phone", placeholder="+91 98765 43210")
            s_password = st.text_input("Password", type="password", key="sig_password", placeholder="Min 6 characters")
            s_city = st.selectbox("City", ["Bangalore", "Chennai"], key="sig_city")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account", key="btn_signup"):
                if not all([s_name, s_email, s_phone, s_password]):
                    st.error("Please fill in all fields.")
                elif len(s_password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    with st.spinner("Creating account..."):
                        try:
                            data, status = api_signup(s_name, s_email, s_phone, s_password, s_city)
                            if status == 200:
                                st.session_state.token = data["access_token"]
                                st.session_state.user = data["user"]
                                st.session_state.city_filter = data["user"]["city"]
                                st.rerun()
                            else:
                                st.error(data.get("detail", "Signup failed"))
                        except Exception as e:
                            st.error(f"Cannot connect to backend: {e}")


# ── Sidebar ────────────────────────────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        st.markdown('<span class="logo-text">LocalPulse</span>', unsafe_allow_html=True)
        st.markdown(
            f'<p style="color:#A0A0A0; font-size:0.8rem; margin-top:0.2rem;">Hey, {st.session_state.user["name"].split()[0]} 👋</p>',
            unsafe_allow_html=True,
        )
        st.markdown("---")

        # Navigation
        if st.button("🏠  Discover Events", key="nav_home"):
            go("home")
        if st.button("🎟️  My Bookings", key="nav_bookings"):
            go("my_bookings")

        st.markdown("---")
        st.markdown('<p style="color:#A0A0A0; font-size:0.75rem; font-weight:600; text-transform:uppercase; letter-spacing:1px;">Filters</p>', unsafe_allow_html=True)

        city = st.selectbox(
            "City",
            ["Bangalore", "Chennai"],
            index=0 if st.session_state.city_filter == "Bangalore" else 1,
            key="sidebar_city",
        )
        st.session_state.city_filter = city

        # Category
        try:
            cats, _ = api_get_categories()
            cat_options = ["All"] + cats
        except Exception:
            cat_options = ["All"]
        category = st.selectbox("Category", cat_options, key="sidebar_cat")

        # Zone
        try:
            zones, _ = api_get_zones(city)
            zone_options = ["All"] + zones
        except Exception:
            zone_options = ["All"]
        zone = st.selectbox("Zone", zone_options, key="sidebar_zone")

        # Date range
        st.markdown('<p style="color:#A0A0A0; font-size:0.8rem; margin-bottom:0.2rem;">Date Range</p>', unsafe_allow_html=True)
        today = date.today()
        date_from = st.date_input("From", value=today, key="sidebar_date_from", label_visibility="collapsed")
        date_to = st.date_input("To", value=today + timedelta(days=30), key="sidebar_date_to", label_visibility="collapsed")

        # Price range
        price_range = st.slider("Price Range (₹)", 0, 2000, (0, 2000), step=50, key="sidebar_price")

        st.markdown("---")
        if st.button("🚪  Sign Out", key="btn_logout"):
            logout()

    return {
        "city": city,
        "category": None if category == "All" else category,
        "zone": None if zone == "All" else zone,
        "date_from": str(date_from),
        "date_to": str(date_to),
        "min_price": price_range[0] if price_range[0] > 0 else None,
        "max_price": price_range[1] if price_range[1] < 2000 else None,
    }


# ── Home / Discovery ──────────────────────────────────────────────────────────

def page_home(filters: dict):
    # Search bar
    search = st.text_input(
        "search_bar",
        placeholder="🔍  Search events, venues, artists...",
        label_visibility="collapsed",
        key="search_input",
    )

    st.markdown(
        f'<div class="section-header">Events in {filters["city"]}</div>',
        unsafe_allow_html=True,
    )

    with st.spinner("Loading events..."):
        try:
            params = {**filters}
            if search:
                params["search"] = search
            events, status = api_get_events(**params)
        except Exception as e:
            st.error(f"Cannot connect to backend. Please ensure the API server is running. ({e})")
            return

    if not events or (isinstance(events, dict) and "detail" in events):
        st.markdown(
            '<div style="text-align:center; color:#666; padding:3rem;">'
            '<div style="font-size:3rem;">🔍</div>'
            '<p>No events found matching your filters.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    # 2-column grid
    cols = st.columns(2)
    for i, event in enumerate(events):
        with cols[i % 2]:
            seats_cls = seats_color_class(event["available_seats"])
            seats_text = (
                f'<span class="{seats_cls}">{event["available_seats"]} seats left</span>'
                if event["available_seats"] > 0
                else '<span class="seats-low">SOLD OUT</span>'
            )

            card_html = f"""
<div class="event-card">
  <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.8rem;">
    <span style="font-size:2.5rem; line-height:1;">{event["image_emoji"]}</span>
    <span class="category-badge">{event["category"]}</span>
  </div>
  <h3 style="color:#FFFFFF; font-size:1rem; font-weight:700; margin:0 0 0.4rem 0; line-height:1.3;">{event["title"]}</h3>
  <p style="color:#A0A0A0; font-size:0.8rem; margin:0 0 0.3rem 0;">
    📍 {event["zone"]} · {event["venue"][:35]}{"..." if len(event["venue"]) > 35 else ""}
  </p>
  <p style="color:#A0A0A0; font-size:0.8rem; margin:0 0 0.6rem 0;">
    📅 {fmt_date(event["event_date"])} · ⏰ {event["event_time"]}
  </p>
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <span class="price-tag">{fmt_price(event["price"])}</span>
    {seats_text}
  </div>
</div>
"""
            st.markdown(card_html, unsafe_allow_html=True)
            if st.button("View Details →", key=f"event_btn_{event['id']}"):
                go("event_detail", selected_event_id=event["id"])


# ── Event Detail ──────────────────────────────────────────────────────────────

def page_event_detail():
    if st.button("← Back to Events", key="back_from_detail"):
        go("home")

    event_id = st.session_state.selected_event_id
    if not event_id:
        st.error("No event selected.")
        return

    with st.spinner("Loading event..."):
        try:
            event, status = api_get_event(event_id)
        except Exception as e:
            st.error(f"Error loading event: {e}")
            return

    if status != 200 or "detail" in event:
        st.error("Event not found.")
        return

    # Hero section
    col_emoji, col_info = st.columns([1, 3])
    with col_emoji:
        st.markdown(
            f'<div style="font-size:5rem; text-align:center; padding:1rem; background:#161616; border-radius:16px; border:1px solid #2A2A2A;">{event["image_emoji"]}</div>',
            unsafe_allow_html=True,
        )
    with col_info:
        st.markdown(f'<h1 style="color:#FFFFFF; font-weight:900; font-size:1.8rem; margin-bottom:0.5rem;">{event["title"]}</h1>', unsafe_allow_html=True)
        st.markdown(
            f'<span class="category-badge">{event["category"]}</span> '
            f'<span style="display:inline-block; background:rgba(255,255,255,0.05); color:#A0A0A0; border-radius:20px; padding:2px 10px; font-size:12px; margin-left:4px;">{event["city"]}</span> '
            f'<span style="display:inline-block; background:rgba(255,255,255,0.05); color:#A0A0A0; border-radius:20px; padding:2px 10px; font-size:12px; margin-left:4px;">{event["zone"]}</span>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<p style="color:#CCCCCC; font-size:0.9rem;">👤 Organized by <strong style="color:#FFFFFF">{event["organizer"]}</strong></p>', unsafe_allow_html=True)

    st.markdown("---")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown('<div class="section-header" style="font-size:1.1rem;">About this Event</div>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#CCCCCC; line-height:1.7; font-size:0.95rem;">{event["description"]}</p>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header" style="font-size:1.1rem;">Details</div>', unsafe_allow_html=True)

        details = [
            ("📍", "Venue", event["venue"]),
            ("🗺️", "Location", f"{event["zone"]}, {event["city"]}"),
            ("📅", "Date", fmt_date(event["event_date"])),
            ("⏰", "Time", event["event_time"]),
            ("👤", "Organizer", event["organizer"]),
        ]
        for icon, label, value in details:
            st.markdown(
                f'<div style="display:flex; gap:0.8rem; margin-bottom:0.5rem;">'
                f'<span style="color:#E8456A; min-width:1.2rem;">{icon}</span>'
                f'<div><span style="color:#666; font-size:0.75rem;">{label}</span>'
                f'<br><span style="color:#FFFFFF; font-size:0.9rem;">{value}</span></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    with col_right:
        # Pricing & seats card
        st.markdown(
            f"""
<div style="background:#161616; border:1px solid #2A2A2A; border-radius:16px; padding:1.5rem;">
  <div style="margin-bottom:1rem;">
    <p style="color:#A0A0A0; font-size:0.75rem; margin-bottom:0.2rem;">PRICE PER PERSON</p>
    <span class="price-tag" style="font-size:2rem;">{fmt_price(event["price"])}</span>
    <span style="color:#666; font-size:0.8rem;"> + 5% fee</span>
  </div>
  <hr style="border-color:#2A2A2A; margin:1rem 0;">
  <div style="margin-bottom:1rem;">
    <p style="color:#A0A0A0; font-size:0.75rem; margin-bottom:0.5rem;">SEAT AVAILABILITY</p>
    <p style="color:#FFFFFF; font-size:0.9rem; margin-bottom:0.3rem;">{event["available_seats"]} / {event["total_seats"]} available</p>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        # Seats progress bar
        avail = event["available_seats"]
        total = event["total_seats"]
        pct = avail / total if total > 0 else 0
        st.progress(pct)

        st.markdown("<br>", unsafe_allow_html=True)

        if avail > 0:
            if st.button("🎟️  Book Now", key="btn_book_now"):
                go("booking", selected_event_id=event_id)
        else:
            st.markdown(
                '<div class="error-box" style="text-align:center;">😔 Sold Out</div>',
                unsafe_allow_html=True,
            )


# ── Booking ───────────────────────────────────────────────────────────────────

def page_booking():
    if st.button("← Back to Event", key="back_from_booking"):
        go("event_detail")

    event_id = st.session_state.selected_event_id
    if not event_id:
        st.error("No event selected.")
        return

    with st.spinner("Loading event..."):
        try:
            event, status = api_get_event(event_id)
        except Exception as e:
            st.error(f"Error: {e}")
            return

    st.markdown(
        f'<div class="section-header">Book: {event["title"]}</div>',
        unsafe_allow_html=True,
    )

    col_form, col_summary = st.columns([3, 2])

    with col_form:
        # Event mini-card
        st.markdown(
            f"""
<div style="background:#161616; border:1px solid #2A2A2A; border-radius:12px; padding:1rem; margin-bottom:1.5rem; display:flex; gap:1rem; align-items:center;">
  <span style="font-size:2.5rem;">{event["image_emoji"]}</span>
  <div>
    <p style="color:#FFFFFF; font-weight:700; margin:0;">{event["title"]}</p>
    <p style="color:#A0A0A0; font-size:0.8rem; margin:0;">📅 {fmt_date(event["event_date"])} · {event["event_time"]}</p>
    <p style="color:#A0A0A0; font-size:0.8rem; margin:0;">📍 {event["venue"]}</p>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        seats = st.number_input(
            "Number of Seats",
            min_value=1,
            max_value=min(20, event["available_seats"]),
            value=1,
            key="booking_seats",
        )

        st.markdown(f'<p style="color:#A0A0A0; font-size:0.85rem; margin-bottom:0.5rem;">Attendee Names ({seats} required)</p>', unsafe_allow_html=True)
        attendee_names = []
        for i in range(int(seats)):
            name = st.text_input(
                f"Attendee {i+1}",
                key=f"attendee_{i}",
                placeholder=f"Full name of attendee {i+1}",
            )
            attendee_names.append(name)

    with col_summary:
        base_amount = seats * event["price"]
        fee = round(base_amount * 0.05, 2)
        total = round(base_amount + fee, 2)

        st.markdown(
            f"""
<div style="background:#161616; border:1px solid #2A2A2A; border-radius:16px; padding:1.5rem; position:sticky; top:1rem;">
  <p style="color:#FFFFFF; font-weight:700; font-size:1rem; margin-bottom:1rem;">Price Breakdown</p>
  <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
    <span style="color:#A0A0A0;">{seats} × {fmt_price(event["price"])}</span>
    <span style="color:#FFFFFF;">{fmt_price(base_amount)}</span>
  </div>
  <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
    <span style="color:#A0A0A0;">Convenience Fee (5%)</span>
    <span style="color:#FFFFFF;">{fmt_price(fee)}</span>
  </div>
  <hr style="border-color:#2A2A2A; margin:0.8rem 0;">
  <div style="display:flex; justify-content:space-between;">
    <span style="color:#FFFFFF; font-weight:700;">Total</span>
    <span class="price-tag">{fmt_price(total)}</span>
  </div>
  <p style="color:#666; font-size:0.75rem; margin-top:0.5rem;">{event["available_seats"]} seats available</p>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Proceed to Payment →", key="btn_proceed_payment"):
        if not all(attendee_names) or any(n.strip() == "" for n in attendee_names):
            st.error("Please enter all attendee names.")
        else:
            with st.spinner("Creating booking..."):
                try:
                    data, status = api_create_booking(
                        st.session_state.token,
                        event_id,
                        int(seats),
                        attendee_names,
                    )
                    if status == 200:
                        go("payment", booking_id=data["id"])
                    else:
                        st.error(data.get("detail", "Booking failed"))
                except Exception as e:
                    st.error(f"Error: {e}")


# ── Payment ───────────────────────────────────────────────────────────────────

def page_payment():
    if st.button("← Back to Booking", key="back_from_payment"):
        go("booking")

    booking_id = st.session_state.booking_id
    if not booking_id:
        st.error("No booking found.")
        return

    with st.spinner("Loading booking..."):
        try:
            booking, status = api_get_booking(st.session_state.token, booking_id)
        except Exception as e:
            st.error(f"Error: {e}")
            return

    if status != 200:
        st.error("Booking not found.")
        return

    # Load event info
    try:
        event, _ = api_get_event(booking["event_id"])
    except Exception:
        event = None

    st.markdown('<div class="section-header">Complete Your Payment</div>', unsafe_allow_html=True)

    col_payment, col_summary = st.columns([3, 2])

    with col_payment:
        tab_upi, tab_card, tab_wallet = st.tabs(["UPI", "Card", "Wallet"])

        with tab_upi:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<p style="color:#A0A0A0; font-size:0.9rem;">Scan the QR code with any UPI app (GPay, PhonePe, Paytm, etc.)</p>',
                unsafe_allow_html=True,
            )

            if st.button("Generate UPI QR Code", key="btn_gen_qr"):
                with st.spinner("Generating QR..."):
                    try:
                        pay_data, pay_status = api_initiate_payment(
                            st.session_state.token, booking_id, "UPI"
                        )
                        if pay_status == 200:
                            st.session_state.payment_id = pay_data["id"]
                            qr_bytes = generate_qr(pay_data["qr_data"])
                            st.image(qr_bytes, width=250, caption="Scan to pay")
                            st.markdown(
                                f'<p style="color:#A0A0A0; font-size:0.8rem; word-break:break-all;">{pay_data["qr_data"]}</p>',
                                unsafe_allow_html=True,
                            )
                        else:
                            st.error(pay_data.get("detail", "Failed to initiate payment"))
                    except Exception as e:
                        st.error(f"Error: {e}")

            if st.session_state.payment_id:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("✅  I have paid", key="btn_upi_paid"):
                    _confirm_and_redirect()

        with tab_card:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<p style="color:#A0A0A0; font-size:0.8rem;">Card number</p>', unsafe_allow_html=True)
            st.text_input("Card Number", value="", placeholder="4242 4242 4242 4242", key="card_number", label_visibility="collapsed")
            c1, c2 = st.columns(2)
            with c1:
                st.text_input("Expiry", placeholder="MM / YY", key="card_expiry", label_visibility="collapsed")
            with c2:
                st.text_input("CVV", placeholder="•••", type="password", key="card_cvv", label_visibility="collapsed")
            st.text_input("Name on Card", placeholder="ARJUN KUMAR", key="card_name", label_visibility="collapsed")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"Pay {fmt_price(booking['total_amount'])}", key="btn_card_pay"):
                with st.spinner("Processing payment..."):
                    try:
                        pay_data, pay_status = api_initiate_payment(
                            st.session_state.token, booking_id, "Card"
                        )
                        if pay_status == 200:
                            st.session_state.payment_id = pay_data["id"]
                            _confirm_and_redirect()
                        else:
                            st.error(pay_data.get("detail", "Payment failed"))
                    except Exception as e:
                        st.error(f"Error: {e}")

        with tab_wallet:
            st.markdown("<br>", unsafe_allow_html=True)
            wallet_choice = st.radio(
                "Select Wallet",
                ["📱 PhonePe", "🟢 Google Pay", "🔵 Paytm"],
                key="wallet_choice",
                label_visibility="collapsed",
            )
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"Pay {fmt_price(booking['total_amount'])} with {wallet_choice}", key="btn_wallet_pay"):
                with st.spinner("Processing payment..."):
                    try:
                        pay_data, pay_status = api_initiate_payment(
                            st.session_state.token, booking_id, "Wallet"
                        )
                        if pay_status == 200:
                            st.session_state.payment_id = pay_data["id"]
                            _confirm_and_redirect()
                        else:
                            st.error(pay_data.get("detail", "Payment failed"))
                    except Exception as e:
                        st.error(f"Error: {e}")

    with col_summary:
        event_title = event["title"] if event else "Event"
        event_date = fmt_date(event["event_date"]) if event else ""
        event_emoji = event["image_emoji"] if event else "🎫"

        st.markdown(
            f"""
<div style="background:#161616; border:1px solid #2A2A2A; border-radius:16px; padding:1.5rem;">
  <p style="color:#FFFFFF; font-weight:700; font-size:1rem; margin-bottom:1rem;">Order Summary</p>
  <div style="display:flex; gap:0.8rem; margin-bottom:1rem; padding-bottom:1rem; border-bottom:1px solid #2A2A2A;">
    <span style="font-size:1.8rem;">{event_emoji}</span>
    <div>
      <p style="color:#FFFFFF; font-weight:600; font-size:0.9rem; margin:0;">{event_title}</p>
      <p style="color:#A0A0A0; font-size:0.8rem; margin:0;">{event_date}</p>
    </div>
  </div>
  <div style="display:flex; justify-content:space-between; margin-bottom:0.4rem;">
    <span style="color:#A0A0A0; font-size:0.85rem;">Seats</span>
    <span style="color:#FFFFFF;">{booking["seats"]}</span>
  </div>
  <div style="display:flex; justify-content:space-between; margin-bottom:0.4rem;">
    <span style="color:#A0A0A0; font-size:0.85rem;">Booking Ref</span>
    <span style="color:#E8456A; font-weight:700; font-size:0.85rem;">{booking["booking_ref"]}</span>
  </div>
  <hr style="border-color:#2A2A2A; margin:0.8rem 0;">
  <div style="display:flex; justify-content:space-between;">
    <span style="color:#FFFFFF; font-weight:700;">Total Amount</span>
    <span class="price-tag">{fmt_price(booking["total_amount"])}</span>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )


def _confirm_and_redirect():
    payment_id = st.session_state.payment_id
    if not payment_id:
        st.error("No payment initiated.")
        return
    try:
        data, status = api_confirm_payment(st.session_state.token, payment_id)
        if status == 200:
            st.markdown(
                '<div class="success-box">🎉 Payment successful! Redirecting to your ticket...</div>',
                unsafe_allow_html=True,
            )
            go("ticket")
        else:
            st.error(data.get("detail", "Payment confirmation failed"))
    except Exception as e:
        st.error(f"Error: {e}")


# ── Ticket ────────────────────────────────────────────────────────────────────

def page_ticket():
    booking_id = st.session_state.booking_id
    if not booking_id:
        st.error("No booking found.")
        return

    try:
        booking, status = api_get_booking(st.session_state.token, booking_id)
    except Exception as e:
        st.error(f"Error: {e}")
        return

    try:
        event, _ = api_get_event(booking["event_id"])
    except Exception:
        event = None

    # Success header
    st.markdown(
        '<div style="text-align:center; padding:1.5rem 0;">'
        '<div style="font-size:3rem; margin-bottom:0.5rem;">🎉</div>'
        '<h1 style="color:#44FF88; font-weight:900; font-size:2rem; margin:0;">Booking Confirmed!</h1>'
        '<p style="color:#A0A0A0; margin-top:0.5rem;">Your tickets are ready. Have a great time!</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    col_ticket, col_qr = st.columns([3, 2])

    attendees = []
    try:
        attendees = json.loads(booking["attendee_names"])
    except Exception:
        pass

    with col_ticket:
        event_title = event["title"] if event else "Event"
        event_emoji = event["image_emoji"] if event else "🎫"
        event_date = fmt_date(event["event_date"]) if event else ""
        event_time = event["event_time"] if event else ""
        event_venue = event["venue"] if event else ""

        st.markdown(
            f"""
<div class="ticket-card">
  <div style="display:flex; gap:1rem; align-items:flex-start; margin-bottom:1.5rem;">
    <span style="font-size:3rem;">{event_emoji}</span>
    <div>
      <h2 style="color:#FFFFFF; font-weight:800; font-size:1.3rem; margin:0 0 0.3rem 0;">{event_title}</h2>
      <span class="category-badge">{event.get("category", "") if event else ""}</span>
    </div>
  </div>
  <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:1.5rem;">
    <div>
      <p style="color:#666; font-size:0.7rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:0.2rem;">Date</p>
      <p style="color:#FFFFFF; font-weight:600; font-size:0.9rem; margin:0;">{event_date}</p>
    </div>
    <div>
      <p style="color:#666; font-size:0.7rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:0.2rem;">Time</p>
      <p style="color:#FFFFFF; font-weight:600; font-size:0.9rem; margin:0;">{event_time}</p>
    </div>
    <div>
      <p style="color:#666; font-size:0.7rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:0.2rem;">Venue</p>
      <p style="color:#FFFFFF; font-weight:600; font-size:0.9rem; margin:0;">{event_venue}</p>
    </div>
    <div>
      <p style="color:#666; font-size:0.7rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:0.2rem;">Seats</p>
      <p style="color:#FFFFFF; font-weight:600; font-size:0.9rem; margin:0;">{booking["seats"]}</p>
    </div>
  </div>
  <div style="border-top:1px dashed #333; padding-top:1rem;">
    <p style="color:#666; font-size:0.7rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:0.2rem;">Booking Reference</p>
    <p style="color:#E8456A; font-weight:900; font-size:1.5rem; letter-spacing:3px; margin:0;">{booking["booking_ref"]}</p>
  </div>
  {"<div style='margin-top:1rem;'><p style='color:#666; font-size:0.7rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:0.3rem;'>Attendees</p>" + "".join(f"<p style='color:#CCCCCC; font-size:0.85rem; margin:0.1rem 0;'>• {n}</p>" for n in attendees) + "</div>" if attendees else ""}
</div>
""",
            unsafe_allow_html=True,
        )

    with col_qr:
        st.markdown(
            '<div style="display:flex; flex-direction:column; align-items:center; padding:1rem;">',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p style="color:#A0A0A0; text-align:center; font-size:0.85rem; margin-bottom:0.8rem;">Show this at the venue</p>',
            unsafe_allow_html=True,
        )
        qr_bytes = generate_qr(booking["booking_ref"])
        st.image(qr_bytes, width=200, caption=booking["booking_ref"])
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🎟️  View My Bookings", key="btn_goto_bookings"):
            go("my_bookings")
    with col_b:
        if st.button("🏠  Discover More Events", key="btn_goto_home"):
            go("home")


# ── My Bookings ───────────────────────────────────────────────────────────────

def page_my_bookings():
    st.markdown('<div class="section-header">My Bookings</div>', unsafe_allow_html=True)

    with st.spinner("Loading bookings..."):
        try:
            bookings, status = api_my_bookings(st.session_state.token)
        except Exception as e:
            st.error(f"Error: {e}")
            return

    if not bookings:
        st.markdown(
            '<div style="text-align:center; color:#666; padding:3rem;">'
            '<div style="font-size:3rem;">🎫</div>'
            '<p>No bookings yet. Explore events and book your first!</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button("Discover Events", key="btn_discover"):
            go("home")
        return

    for booking in bookings:
        # Load event for each booking
        try:
            event, _ = api_get_event(booking["event_id"])
            event_title = event["title"]
            event_emoji = event["image_emoji"]
            event_date = fmt_date(event["event_date"])
            event_venue = event["venue"]
        except Exception:
            event_title = f"Event #{booking['event_id']}"
            event_emoji = "🎫"
            event_date = ""
            event_venue = ""

        sc = status_color(booking["status"])
        status_label = booking["status"].upper()

        with st.expander(
            f'{event_emoji}  {event_title}  —  {event_date}  —  {status_label}',
            expanded=False,
        ):
            col_info, col_actions = st.columns([3, 1])

            attendees = []
            try:
                attendees = json.loads(booking["attendee_names"])
            except Exception:
                pass

            with col_info:
                st.markdown(
                    f"""
<div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:1rem;">
  <div>
    <p style="color:#666; font-size:0.75rem; text-transform:uppercase; margin-bottom:0.2rem;">Booking Ref</p>
    <p style="color:#E8456A; font-weight:700; letter-spacing:2px;">{booking["booking_ref"]}</p>
  </div>
  <div>
    <p style="color:#666; font-size:0.75rem; text-transform:uppercase; margin-bottom:0.2rem;">Status</p>
    <p style="color:{sc}; font-weight:700;">{status_label}</p>
  </div>
  <div>
    <p style="color:#666; font-size:0.75rem; text-transform:uppercase; margin-bottom:0.2rem;">Seats</p>
    <p style="color:#FFFFFF;">{booking["seats"]}</p>
  </div>
  <div>
    <p style="color:#666; font-size:0.75rem; text-transform:uppercase; margin-bottom:0.2rem;">Amount Paid</p>
    <p style="color:#FFFFFF;">{fmt_price(booking["total_amount"])}</p>
  </div>
  <div>
    <p style="color:#666; font-size:0.75rem; text-transform:uppercase; margin-bottom:0.2rem;">Venue</p>
    <p style="color:#CCCCCC; font-size:0.9rem;">{event_venue}</p>
  </div>
  <div>
    <p style="color:#666; font-size:0.75rem; text-transform:uppercase; margin-bottom:0.2rem;">Payment</p>
    <p style="color:#CCCCCC; font-size:0.9rem;">{booking["payment_status"].upper()}</p>
  </div>
</div>
""",
                    unsafe_allow_html=True,
                )

                if attendees:
                    st.markdown('<p style="color:#666; font-size:0.75rem; text-transform:uppercase; margin-bottom:0.3rem;">Attendees</p>', unsafe_allow_html=True)
                    for n in attendees:
                        st.markdown(f'<p style="color:#CCCCCC; font-size:0.85rem; margin:0.1rem 0;">• {n}</p>', unsafe_allow_html=True)

                # Show QR for confirmed bookings
                if booking["status"] == "confirmed":
                    st.markdown("<br>", unsafe_allow_html=True)
                    qr_bytes = generate_qr(booking["booking_ref"])
                    st.image(qr_bytes, width=150, caption="Entry QR")

            with col_actions:
                if booking["status"] not in ("cancelled",):
                    if st.button("View Ticket", key=f"view_ticket_{booking['id']}"):
                        st.session_state.booking_id = booking["id"]
                        go("ticket")

                if booking["status"] == "pending" and booking["payment_status"] == "pending":
                    if st.button("Complete Payment", key=f"pay_{booking['id']}"):
                        st.session_state.booking_id = booking["id"]
                        st.session_state.selected_event_id = booking["event_id"]
                        go("payment")

                if booking["status"] not in ("cancelled",):
                    if st.button("Cancel", key=f"cancel_{booking['id']}"):
                        with st.spinner("Cancelling..."):
                            try:
                                data, s = api_cancel_booking(st.session_state.token, booking["id"])
                                if s == 200:
                                    st.success("Booking cancelled.")
                                    st.rerun()
                                else:
                                    st.error(data.get("detail", "Cancel failed"))
                            except Exception as e:
                                st.error(f"Error: {e}")


# ── Router ─────────────────────────────────────────────────────────────────────

def main():
    if not st.session_state.token:
        page_auth()
        return

    filters = render_sidebar()
    page = st.session_state.page

    if page == "home":
        page_home(filters)
    elif page == "event_detail":
        page_event_detail()
    elif page == "booking":
        page_booking()
    elif page == "payment":
        page_payment()
    elif page == "ticket":
        page_ticket()
    elif page == "my_bookings":
        page_my_bookings()
    else:
        page_home(filters)


if __name__ == "__main__":
    main()
else:
    main()
