import time
import random
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Payment, Booking, Event, User
from backend.schemas import PaymentInitiate, PaymentConfirm, PaymentOut
from backend.routers.auth import get_current_user

router = APIRouter(prefix="/api/payments", tags=["payments"])
security = HTTPBearer()


def require_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    return get_current_user(credentials.credentials, db)


def gen_transaction_id() -> str:
    suffix = str(random.randint(1000, 9999))
    return f"TX{int(time.time())}{suffix}"


@router.post("/initiate", response_model=PaymentOut)
def initiate_payment(
    data: PaymentInitiate,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    booking = db.query(Booking).filter(Booking.id == data.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    if booking.status == "confirmed":
        raise HTTPException(status_code=400, detail="Booking already confirmed")

    # Build UPI QR data
    qr_data = (
        f"upi://pay?pa=localpulse@upi&pn=LocalPulse"
        f"&am={booking.total_amount}&cu=INR&tn=Booking{booking.booking_ref}"
    )

    payment = Payment(
        booking_id=booking.id,
        amount=booking.total_amount,
        payment_method=data.payment_method,
        transaction_id=gen_transaction_id(),
        status="pending",
        qr_data=qr_data,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


@router.post("/confirm", response_model=PaymentOut)
def confirm_payment(
    data: PaymentConfirm,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    payment = db.query(Payment).filter(Payment.id == data.payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Atomically update everything
    event = db.query(Event).filter(Event.id == booking.event_id).first()
    if event:
        if event.available_seats < booking.seats:
            raise HTTPException(status_code=400, detail="Not enough seats available")
        event.available_seats -= booking.seats

    payment.status = "success"
    booking.status = "confirmed"
    booking.payment_status = "paid"

    db.commit()
    db.refresh(payment)
    return payment


@router.get("/{booking_id}", response_model=PaymentOut)
def get_payment(
    booking_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    payment = (
        db.query(Payment)
        .filter(Payment.booking_id == booking_id)
        .order_by(Payment.id.desc())
        .first()
    )
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment
