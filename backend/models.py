from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    city = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    bookings = relationship("Booking", back_populates="user")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    category = Column(String, nullable=False)
    city = Column(String, nullable=False)
    zone = Column(String, nullable=False)
    venue = Column(String, nullable=False)
    event_date = Column(Date, nullable=False)
    event_time = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    total_seats = Column(Integer, nullable=False)
    available_seats = Column(Integer, nullable=False)
    image_emoji = Column(String, nullable=False)
    organizer = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)

    bookings = relationship("Booking", back_populates="event")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    seats = Column(Integer, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String, default="pending")
    payment_status = Column(String, default="pending")
    booking_ref = Column(String, unique=True, nullable=False)
    attendee_names = Column(String, nullable=False)  # JSON list as string
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bookings")
    event = relationship("Event", back_populates="bookings")
    payments = relationship("Payment", back_populates="booking")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)
    transaction_id = Column(String, nullable=False)
    status = Column(String, default="pending")
    qr_data = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    booking = relationship("Booking", back_populates="payments")
