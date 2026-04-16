import json
import random
import string
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Booking, Event, User
from backend.schemas import BookingCreate, BookingOut
from backend.routers.auth import get_current_user

router = APIRouter(prefix="/api/bookings", tags=["bookings"])
security = HTTPBearer()


def require_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    return get_current_user(credentials.credentials, db)


def gen_booking_ref() -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


@router.post("", response_model=BookingOut)
def create_booking(
    data: BookingCreate,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    event = db.query(Event).filter(Event.id == data.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.available_seats < data.seats:
        raise HTTPException(status_code=400, detail="Not enough seats available")
    if len(data.attendee_names) != data.seats:
        raise HTTPException(status_code=400, detail="Attendee names count must match seats")

    total = round(data.seats * event.price * 1.05, 2)  # 5% convenience fee
    ref = gen_booking_ref()

    booking = Booking(
        user_id=user.id,
        event_id=data.event_id,
        seats=data.seats,
        total_amount=total,
        status="pending",
        payment_status="pending",
        booking_ref=ref,
        attendee_names=json.dumps(data.attendee_names),
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/my", response_model=list[BookingOut])
def my_bookings(
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    bookings = (
        db.query(Booking)
        .filter(Booking.user_id == user.id)
        .order_by(Booking.created_at.desc())
        .all()
    )
    return bookings


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(
    booking_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return booking


@router.patch("/{booking_id}/cancel", response_model=BookingOut)
def cancel_booking(
    booking_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    if booking.status == "cancelled":
        raise HTTPException(status_code=400, detail="Already cancelled")

    # Restore seats if booking was confirmed
    if booking.status == "confirmed":
        event = db.query(Event).filter(Event.id == booking.event_id).first()
        if event:
            event.available_seats += booking.seats

    booking.status = "cancelled"
    db.commit()
    db.refresh(booking)
    return booking
