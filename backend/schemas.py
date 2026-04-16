from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserSignup(BaseModel):
    name: str
    email: str
    phone: str
    password: str
    city: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    city: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


# ── Events ────────────────────────────────────────────────────────────────────

class EventOut(BaseModel):
    id: int
    title: str
    description: str
    category: str
    city: str
    zone: str
    venue: str
    event_date: date
    event_time: str
    price: float
    total_seats: int
    available_seats: int
    image_emoji: str
    organizer: str
    lat: float
    lng: float

    class Config:
        from_attributes = True


# ── Bookings ──────────────────────────────────────────────────────────────────

class BookingCreate(BaseModel):
    event_id: int
    seats: int
    attendee_names: List[str]


class BookingOut(BaseModel):
    id: int
    user_id: int
    event_id: int
    seats: int
    total_amount: float
    status: str
    payment_status: str
    booking_ref: str
    attendee_names: str
    created_at: datetime
    event: Optional[EventOut] = None

    class Config:
        from_attributes = True


# ── Payments ──────────────────────────────────────────────────────────────────

class PaymentInitiate(BaseModel):
    booking_id: int
    payment_method: str


class PaymentConfirm(BaseModel):
    payment_id: int


class PaymentOut(BaseModel):
    id: int
    booking_id: int
    amount: float
    payment_method: str
    transaction_id: str
    status: str
    qr_data: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
