from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date

from backend.database import get_db
from backend.models import Event
from backend.schemas import EventOut

router = APIRouter(prefix="/api/events", tags=["events"])

CATEGORIES = ["Music", "Food", "Comedy", "Sports", "Workshop", "Arts", "Nightlife", "Theatre"]

ZONES = {
    "Bangalore": [
        "Indiranagar", "Koramangala", "MG Road", "Whitefield", "Jayanagar",
        "HSR Layout", "Marathahalli", "Malleshwaram", "Ulsoor", "Electronic City"
    ],
    "Chennai": [
        "Anna Nagar", "T. Nagar", "Adyar", "Nungambakkam", "Egmore",
        "Velachery", "Mylapore", "Besant Nagar", "OMR", "Guindy"
    ]
}


@router.get("/categories", response_model=List[str])
def get_categories():
    return CATEGORIES


@router.get("/zones/{city}", response_model=List[str])
def get_zones(city: str):
    zones = ZONES.get(city)
    if zones is None:
        raise HTTPException(status_code=404, detail="City not found")
    return zones


@router.get("", response_model=List[EventOut])
def list_events(
    city: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    zone: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    search: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Event)
    if city:
        q = q.filter(Event.city == city)
    if category:
        q = q.filter(Event.category == category)
    if zone:
        q = q.filter(Event.zone == zone)
    if date_from:
        q = q.filter(Event.event_date >= date_from)
    if date_to:
        q = q.filter(Event.event_date <= date_to)
    if search:
        term = f"%{search}%"
        q = q.filter(
            Event.title.ilike(term) |
            Event.description.ilike(term) |
            Event.venue.ilike(term)
        )
    if min_price is not None:
        q = q.filter(Event.price >= min_price)
    if max_price is not None:
        q = q.filter(Event.price <= max_price)

    return q.order_by(Event.event_date).all()


@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
