from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import engine, Base, SessionLocal
from backend.routers import auth, events, bookings, payments

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LocalPulse API", version="1.0.0")

# CORS — allow Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(bookings.router)
app.include_router(payments.router)


@app.on_event("startup")
def on_startup():
    from backend.seed_data import seed_events
    db = SessionLocal()
    try:
        seed_events(db)
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "LocalPulse API is running", "docs": "/docs"}
