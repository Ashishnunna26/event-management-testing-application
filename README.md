# LocalPulse — Local Event Discovery & Booking Platform

> Find Your Pulse: Events, Anytime, Nearby

A full-stack event discovery and booking platform for **Bangalore** and **Chennai**, built as a functional prototype from the LocalPulse PRD.

![Dark Mode UI](https://img.shields.io/badge/UI-District%20Dark%20Mode-E8456A?style=flat-square)
![Backend](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square)
![Frontend](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=flat-square)
![Database](https://img.shields.io/badge/Database-SQLite-003B57?style=flat-square)

---

## Features

- **Event Discovery** — Browse 30 pre-seeded events across Bangalore & Chennai with real Google Maps coordinates
- **Advanced Filtering** — Filter by city, category (Music/Comedy/Food/Sports/Workshop/Arts/Nightlife/Theatre), zone, date range, and price
- **User Auth** — Sign up / sign in with bcrypt password hashing and JWT tokens
- **Seat Booking** — Individual or group bookings (up to 20 seats), real-time seat decrement on payment
- **QR Payment** — UPI QR code generation, Card, and Wallet fake payment flows; seats only decrement after confirmed payment
- **Digital Tickets** — QR-coded ticket with booking reference after successful payment
- **My Bookings** — View all bookings, ticket QR, and cancel pending bookings
- **District-inspired Dark Mode** — Black background, coral-red accents, card-based layout

---

## Tech Stack

| Layer    | Technology                        |
|----------|-----------------------------------|
| Backend  | Python FastAPI + Uvicorn          |
| Frontend | Python Streamlit                  |
| Database | SQLite (via SQLAlchemy ORM)       |
| Auth     | JWT (HS256) + bcrypt passwords    |
| QR Codes | `qrcode` + `Pillow`               |

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the backend (Terminal 1)

```bash
python start_backend.py
# API runs at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### 3. Start the frontend (Terminal 2)

```bash
python start_frontend.py
# App runs at http://localhost:8501
```

### 4. Open the app

Go to **http://localhost:8501** in your browser.

---

## Project Structure

```
localpulse/
├── backend/
│   ├── main.py           # FastAPI app entry point
│   ├── database.py       # SQLite engine & session
│   ├── models.py         # SQLAlchemy ORM models
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── seed_data.py      # 30 pre-seeded events (BLR + CHN)
│   └── routers/
│       ├── auth.py       # /api/auth/* endpoints
│       ├── events.py     # /api/events/* endpoints
│       ├── bookings.py   # /api/bookings/* endpoints
│       └── payments.py   # /api/payments/* endpoints
├── frontend/
│   ├── app.py            # Streamlit single-file app (7 pages)
│   └── utils.py          # API helpers, QR generator, formatters
├── requirements.txt
├── start_backend.py
├── start_frontend.py
└── README.md
```

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register new user |
| POST | `/api/auth/login` | Login, returns JWT token |
| GET  | `/api/auth/me` | Get current user |

### Events
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/events` | List events (filterable) |
| GET | `/api/events/{id}` | Event detail |
| GET | `/api/events/categories` | All categories |
| GET | `/api/events/zones/{city}` | Zones for a city |

### Bookings
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/bookings` | Create booking |
| GET  | `/api/bookings/my` | My bookings |
| GET  | `/api/bookings/{id}` | Booking detail |
| PATCH | `/api/bookings/{id}/cancel` | Cancel booking |

### Payments
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/payments/initiate` | Start payment, returns UPI QR |
| POST | `/api/payments/confirm` | Confirm payment, decrements seats |
| GET  | `/api/payments/{booking_id}` | Get payment status |

---

## Seeded Events

### Bangalore (15 events)
Zones: Indiranagar, Koramangala, MG Road, Whitefield, Jayanagar, HSR Layout, Marathahalli, Malleshwaram, Ulsoor, Electronic City

### Chennai (15 events)
Zones: Anna Nagar, T. Nagar, Adyar, Nungambakkam, Egmore, Velachery, Mylapore, Besant Nagar, OMR, Guindy

---

## Payment Flow

1. Create a booking — booking status: `pending`
2. Initiate payment — generates UPI QR code (or Card/Wallet UI)
3. Confirm payment (click "I have paid" / "Pay") — atomically:
   - Sets payment status: `success`
   - Sets booking status: `confirmed`
   - Decrements `event.available_seats` by seats booked
4. Ticket with QR code displayed immediately

---

## Database

SQLite database stored at `localpulse.db` in the project root. Auto-created and seeded on first backend startup. No external database required.
