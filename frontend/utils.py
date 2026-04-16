import qrcode
import requests
from io import BytesIO
from PIL import Image

BACKEND_URL = "http://localhost:8000"


# ── QR Code ───────────────────────────────────────────────────────────────────

def generate_qr(data: str) -> bytes:
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ── API helpers ───────────────────────────────────────────────────────────────

def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def api_signup(name, email, phone, password, city):
    r = requests.post(
        f"{BACKEND_URL}/api/auth/signup",
        json={"name": name, "email": email, "phone": phone, "password": password, "city": city},
        timeout=10,
    )
    return r.json(), r.status_code


def api_login(email, password):
    r = requests.post(
        f"{BACKEND_URL}/api/auth/login",
        json={"email": email, "password": password},
        timeout=10,
    )
    return r.json(), r.status_code


def api_get_events(token=None, **params):
    clean = {k: v for k, v in params.items() if v is not None and v != "" and v != "All"}
    r = requests.get(f"{BACKEND_URL}/api/events", params=clean, timeout=10)
    return r.json(), r.status_code


def api_get_event(event_id: int):
    r = requests.get(f"{BACKEND_URL}/api/events/{event_id}", timeout=10)
    return r.json(), r.status_code


def api_get_categories():
    r = requests.get(f"{BACKEND_URL}/api/events/categories", timeout=10)
    return r.json(), r.status_code


def api_get_zones(city: str):
    r = requests.get(f"{BACKEND_URL}/api/events/zones/{city}", timeout=10)
    return r.json(), r.status_code


def api_create_booking(token, event_id, seats, attendee_names):
    r = requests.post(
        f"{BACKEND_URL}/api/bookings",
        json={"event_id": event_id, "seats": seats, "attendee_names": attendee_names},
        headers=auth_headers(token),
        timeout=10,
    )
    return r.json(), r.status_code


def api_my_bookings(token):
    r = requests.get(
        f"{BACKEND_URL}/api/bookings/my",
        headers=auth_headers(token),
        timeout=10,
    )
    return r.json(), r.status_code


def api_get_booking(token, booking_id):
    r = requests.get(
        f"{BACKEND_URL}/api/bookings/{booking_id}",
        headers=auth_headers(token),
        timeout=10,
    )
    return r.json(), r.status_code


def api_cancel_booking(token, booking_id):
    r = requests.patch(
        f"{BACKEND_URL}/api/bookings/{booking_id}/cancel",
        headers=auth_headers(token),
        timeout=10,
    )
    return r.json(), r.status_code


def api_initiate_payment(token, booking_id, payment_method):
    r = requests.post(
        f"{BACKEND_URL}/api/payments/initiate",
        json={"booking_id": booking_id, "payment_method": payment_method},
        headers=auth_headers(token),
        timeout=10,
    )
    return r.json(), r.status_code


def api_confirm_payment(token, payment_id):
    r = requests.post(
        f"{BACKEND_URL}/api/payments/confirm",
        json={"payment_id": payment_id},
        headers=auth_headers(token),
        timeout=10,
    )
    return r.json(), r.status_code


def api_get_payment(token, booking_id):
    r = requests.get(
        f"{BACKEND_URL}/api/payments/{booking_id}",
        headers=auth_headers(token),
        timeout=10,
    )
    return r.json(), r.status_code


# ── Formatting helpers ────────────────────────────────────────────────────────

def fmt_price(amount: float) -> str:
    return f"₹{amount:,.0f}"


def fmt_date(d: str) -> str:
    from datetime import datetime
    try:
        dt = datetime.strptime(d, "%Y-%m-%d")
        return dt.strftime("%a, %d %b %Y")
    except Exception:
        return d


def seats_color_class(available: int) -> str:
    if available < 10:
        return "seats-low"
    return "seats-ok"


def status_color(status: str) -> str:
    mapping = {
        "confirmed": "#44FF88",
        "pending": "#FFB84D",
        "cancelled": "#888888",
    }
    return mapping.get(status, "#FFFFFF")
