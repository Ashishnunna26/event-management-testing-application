from datetime import date, timedelta
from backend.database import SessionLocal
from backend.models import Event

# Base date: 2026-04-16
BASE_DATE = date(2026, 4, 16)


def d(offset: int) -> date:
    return BASE_DATE + timedelta(days=offset)


EVENTS = [
    # ── Bangalore ────────────────────────────────────────────────────────────
    {
        "title": "Jazz Night at Toit",
        "description": (
            "An intimate evening of smooth jazz at Bangalore's iconic Toit Brewpub. "
            "Featuring live performances by local jazz legends, craft beers, and great food. "
            "Doors open at 7 PM. Smart casual dress code."
        ),
        "category": "Music",
        "city": "Bangalore",
        "zone": "Indiranagar",
        "venue": "Toit Brewpub, 298 100 Feet Rd",
        "event_date": d(2),
        "event_time": "19:30",
        "price": 800.0,
        "total_seats": 80,
        "available_seats": 12,
        "image_emoji": "🎷",
        "organizer": "Toit Brewpub Events",
        "lat": 12.9716,
        "lng": 77.6412,
    },
    {
        "title": "Comedy Night at The Humming Tree",
        "description": (
            "Catch Bangalore's funniest stand-up comedians back-to-back at The Humming Tree. "
            "An unforgettable night of laughter with 5 headlining acts, a full bar, and delicious bites. "
            "Show starts at 8 PM sharp."
        ),
        "category": "Comedy",
        "city": "Bangalore",
        "zone": "Indiranagar",
        "venue": "The Humming Tree, 12th Main, HAL 2nd Stage",
        "event_date": d(4),
        "event_time": "20:00",
        "price": 600.0,
        "total_seats": 120,
        "available_seats": 55,
        "image_emoji": "🎤",
        "organizer": "LOL Comedy Club",
        "lat": 12.9726,
        "lng": 77.6401,
    },
    {
        "title": "Bangalore Food Festival",
        "description": (
            "The biggest food festival in Bangalore returns to Forum Koramangala! "
            "50+ stalls featuring cuisines from across India and the world. "
            "Live cooking demos, food competitions, and celebrity chef appearances."
        ),
        "category": "Food",
        "city": "Bangalore",
        "zone": "Koramangala",
        "venue": "Forum Koramangala Mall, Hosur Rd",
        "event_date": d(5),
        "event_time": "12:00",
        "price": 500.0,
        "total_seats": 200,
        "available_seats": 130,
        "image_emoji": "🍔",
        "organizer": "Foodies of Bangalore",
        "lat": 12.9352,
        "lng": 77.6245,
    },
    {
        "title": "Electronic Music Rave",
        "description": (
            "Bangalore's most anticipated electronic music event at Hard Rock Cafe MG Road. "
            "International DJs spinning techno, house, and trance all night long. "
            "Laser show, LED walls, and open bar packages available."
        ),
        "category": "Nightlife",
        "city": "Bangalore",
        "zone": "MG Road",
        "venue": "Hard Rock Cafe, St. Mark's Rd",
        "event_date": d(7),
        "event_time": "22:00",
        "price": 1200.0,
        "total_seats": 150,
        "available_seats": 7,
        "image_emoji": "🎧",
        "organizer": "Bass Culture Events",
        "lat": 12.9747,
        "lng": 77.6076,
    },
    {
        "title": "Yoga & Wellness Workshop",
        "description": (
            "A full-day wellness experience at Cult.fit HSR Layout. "
            "Morning yoga session, meditation, breathwork, and nutrition workshop. "
            "Certified instructors, organic lunch included. Mats provided."
        ),
        "category": "Workshop",
        "city": "Bangalore",
        "zone": "HSR Layout",
        "venue": "Cult.fit HSR, 27th Main Rd",
        "event_date": d(8),
        "event_time": "07:00",
        "price": 400.0,
        "total_seats": 40,
        "available_seats": 18,
        "image_emoji": "🧘",
        "organizer": "Wellness Bangalore",
        "lat": 12.9116,
        "lng": 77.6413,
    },
    {
        "title": "Stand-Up Comedy Show",
        "description": (
            "A rip-roaring comedy night at Doodle Restaurant Koramangala. "
            "Featuring 3 acclaimed comedians from the national circuit. "
            "Dinner + show package available. Limited seating — book early!"
        ),
        "category": "Comedy",
        "city": "Bangalore",
        "zone": "Koramangala",
        "venue": "Doodle Restaurant, 6th Block Koramangala",
        "event_date": d(10),
        "event_time": "20:30",
        "price": 700.0,
        "total_seats": 90,
        "available_seats": 34,
        "image_emoji": "😂",
        "organizer": "Punchline Events",
        "lat": 12.9347,
        "lng": 77.6239,
    },
    {
        "title": "Indie Music Fest",
        "description": (
            "Three stages, twelve bands, one epic weekend at Phoenix Marketcity Whitefield. "
            "Celebrating the best of Indian indie music across genres — folk, rock, electronic, and pop. "
            "Food courts open. All ages welcome."
        ),
        "category": "Music",
        "city": "Bangalore",
        "zone": "Whitefield",
        "venue": "Phoenix Marketcity, Whitefield Main Rd",
        "event_date": d(12),
        "event_time": "16:00",
        "price": 999.0,
        "total_seats": 300,
        "available_seats": 185,
        "image_emoji": "🎸",
        "organizer": "Indie Nation",
        "lat": 12.9969,
        "lng": 77.6967,
    },
    {
        "title": "Food Truck Festival",
        "description": (
            "Jayanagar's favorite food truck festival is back at the iconic 4th Block! "
            "20+ food trucks, live music, craft beer garden, and games. "
            "Vegan and gluten-free options available. Bring the whole family."
        ),
        "category": "Food",
        "city": "Bangalore",
        "zone": "Jayanagar",
        "venue": "Jayanagar 4th Block Shopping Complex",
        "event_date": d(14),
        "event_time": "17:00",
        "price": 350.0,
        "total_seats": 250,
        "available_seats": 92,
        "image_emoji": "🌮",
        "organizer": "Street Eats Bangalore",
        "lat": 12.9261,
        "lng": 77.5825,
    },
    {
        "title": "Art Exhibition Opening",
        "description": (
            "Experience Bangalore's thriving contemporary art scene at Rangoli Metro Art Center. "
            "Featuring works by 30 emerging artists exploring themes of identity, nature, and technology. "
            "Opening night includes artist talks and complimentary refreshments."
        ),
        "category": "Arts",
        "city": "Bangalore",
        "zone": "MG Road",
        "venue": "Rangoli Metro Art Center, MG Road Station",
        "event_date": d(15),
        "event_time": "18:00",
        "price": 200.0,
        "total_seats": 60,
        "available_seats": 45,
        "image_emoji": "🎨",
        "organizer": "Bangalore Art Collective",
        "lat": 12.9743,
        "lng": 77.6077,
    },
    {
        "title": "IPL Watch Party",
        "description": (
            "Cheer for your team at the ultimate IPL watch party at Sheraton Grand Bangalore. "
            "Multiple giant screens, live commentary, bucket deals, and cricket-themed food. "
            "Lucky draw prizes for the best-dressed fans!"
        ),
        "category": "Sports",
        "city": "Bangalore",
        "zone": "Malleshwaram",
        "venue": "Sheraton Grand Bangalore, Palace Grounds",
        "event_date": d(3),
        "event_time": "19:00",
        "price": 500.0,
        "total_seats": 200,
        "available_seats": 76,
        "image_emoji": "🏏",
        "organizer": "Sports Fever Events",
        "lat": 13.0068,
        "lng": 77.5714,
    },
    {
        "title": "Photography Walk — Malleshwaram",
        "description": (
            "A guided photography walk through the heritage lanes of Malleshwaram. "
            "Capture the essence of old Bangalore — flower markets, temples, and street life. "
            "Led by award-winning photographer Ravi Shankar. All skill levels welcome."
        ),
        "category": "Workshop",
        "city": "Bangalore",
        "zone": "Malleshwaram",
        "venue": "Malleshwaram Circle (Meeting Point)",
        "event_date": d(9),
        "event_time": "06:30",
        "price": 299.0,
        "total_seats": 25,
        "available_seats": 9,
        "image_emoji": "📷",
        "organizer": "Lens & Light Photography Club",
        "lat": 13.0068,
        "lng": 77.5714,
    },
    {
        "title": "Tech Talk: AI & Future of Work",
        "description": (
            "A thought-provoking evening with industry leaders discussing AI's impact on the future of work. "
            "Panel discussions, networking sessions, and live demos. "
            "Hosted at Electronic City's thriving tech hub."
        ),
        "category": "Workshop",
        "city": "Bangalore",
        "zone": "Electronic City",
        "venue": "NASSCOM CoE, Electronic City Phase 1",
        "event_date": d(11),
        "event_time": "18:30",
        "price": 599.0,
        "total_seats": 150,
        "available_seats": 63,
        "image_emoji": "💻",
        "organizer": "TechBLR Community",
        "lat": 12.8463,
        "lng": 77.6636,
    },
    {
        "title": "Bollywood Retro Night",
        "description": (
            "Dance to the golden hits of Bollywood from the 70s, 80s and 90s! "
            "Live DJ, themed photobooth, retro costumes encouraged. "
            "At the iconic Ulsoor Lake Club."
        ),
        "category": "Nightlife",
        "city": "Bangalore",
        "zone": "Ulsoor",
        "venue": "Ulsoor Lake Club, Halasuru",
        "event_date": d(16),
        "event_time": "21:00",
        "price": 850.0,
        "total_seats": 120,
        "available_seats": 44,
        "image_emoji": "💃",
        "organizer": "Retro Night Productions",
        "lat": 12.9775,
        "lng": 77.6237,
    },
    {
        "title": "Marathahalli Street Food Crawl",
        "description": (
            "Join us on a guided street food tour through the vibrant lanes of Marathahalli. "
            "Taste the best chaats, biryanis, dosas, and desserts. "
            "Walking tour with a food expert guide. Ends at a local chai spot."
        ),
        "category": "Food",
        "city": "Bangalore",
        "zone": "Marathahalli",
        "venue": "Marathahalli Bridge (Meeting Point)",
        "event_date": d(18),
        "event_time": "18:00",
        "price": 450.0,
        "total_seats": 30,
        "available_seats": 5,
        "image_emoji": "🍜",
        "organizer": "Eat Like a Local Tours",
        "lat": 12.9591,
        "lng": 77.6972,
    },
    {
        "title": "Theatre Showcase: New Voices",
        "description": (
            "An evening of experimental theatre featuring six short plays by debut playwrights. "
            "Exploring themes of love, loss, and identity in contemporary India. "
            "Post-show Q&A with the cast and directors."
        ),
        "category": "Theatre",
        "city": "Bangalore",
        "zone": "Indiranagar",
        "venue": "Ranga Shankara, JP Nagar",
        "event_date": d(20),
        "event_time": "19:00",
        "price": 350.0,
        "total_seats": 80,
        "available_seats": 31,
        "image_emoji": "🎭",
        "organizer": "Stage and Script Collective",
        "lat": 12.9116,
        "lng": 77.5834,
    },

    # ── Chennai ───────────────────────────────────────────────────────────────
    {
        "title": "Carnatic Music Concert",
        "description": (
            "A sublime evening of classical Carnatic music at the prestigious Music Academy. "
            "Featuring Vidwan T.M. Krishna and accompanying artists. "
            "One of Chennai's most celebrated concert experiences."
        ),
        "category": "Music",
        "city": "Chennai",
        "zone": "Mylapore",
        "venue": "Music Academy, TTK Road",
        "event_date": d(1),
        "event_time": "18:30",
        "price": 600.0,
        "total_seats": 500,
        "available_seats": 220,
        "image_emoji": "🎵",
        "organizer": "Music Academy Chennai",
        "lat": 13.0343,
        "lng": 80.2705,
    },
    {
        "title": "Chennai Comedy Club",
        "description": (
            "Chennai's premier comedy club comes to The Leela Palace Nungambakkam. "
            "An evening of sharp wit and hilarious observations from Chennai's top comedians. "
            "Cocktails and dinner available. Must be 21+."
        ),
        "category": "Comedy",
        "city": "Chennai",
        "zone": "Nungambakkam",
        "venue": "The Leela Palace, Adyar Seaface",
        "event_date": d(3),
        "event_time": "20:00",
        "price": 800.0,
        "total_seats": 100,
        "available_seats": 38,
        "image_emoji": "🎤",
        "organizer": "Madras Comedy Factory",
        "lat": 13.0569,
        "lng": 80.2425,
    },
    {
        "title": "Marina Beach Food Fest",
        "description": (
            "The biggest outdoor food festival in South India returns to Elliot's Beach. "
            "100+ stalls serving everything from filter coffee to craft cocktails. "
            "Live music, beach games, and sunset vibes. "
            "Free entry for children under 12."
        ),
        "category": "Food",
        "city": "Chennai",
        "zone": "Besant Nagar",
        "venue": "Elliot's Beach, Besant Nagar",
        "event_date": d(6),
        "event_time": "16:00",
        "price": 300.0,
        "total_seats": 400,
        "available_seats": 210,
        "image_emoji": "🦀",
        "organizer": "Chennai Food Council",
        "lat": 12.9987,
        "lng": 80.2707,
    },
    {
        "title": "Classical Dance Recital",
        "description": (
            "An exquisite Bharatanatyam recital at the legendary Kalakshetra Foundation. "
            "Featuring solo performances by Kalakshetra's finest dancers. "
            "Traditional costumes, live orchestra. A must-see cultural experience."
        ),
        "category": "Arts",
        "city": "Chennai",
        "zone": "Mylapore",
        "venue": "Kalakshetra Foundation, Thiruvanmiyur",
        "event_date": d(7),
        "event_time": "18:00",
        "price": 400.0,
        "total_seats": 200,
        "available_seats": 87,
        "image_emoji": "💃",
        "organizer": "Kalakshetra Foundation",
        "lat": 12.9986,
        "lng": 80.2586,
    },
    {
        "title": "Tech & Startup Workshop",
        "description": (
            "A full-day intensive workshop for entrepreneurs and tech enthusiasts at TIDEL Park OMR. "
            "Covers startup fundamentals, pitching, product development, and fundraising. "
            "Mentors from top VC firms and successful founders in attendance."
        ),
        "category": "Workshop",
        "city": "Chennai",
        "zone": "OMR",
        "venue": "TIDEL Park, Taramani, OMR",
        "event_date": d(9),
        "event_time": "09:00",
        "price": 999.0,
        "total_seats": 80,
        "available_seats": 22,
        "image_emoji": "🚀",
        "organizer": "StartupTN",
        "lat": 12.9717,
        "lng": 80.2448,
    },
    {
        "title": "Retro Bollywood Night",
        "description": (
            "Relive the golden age of Bollywood at VGP Golden Beach Anna Nagar. "
            "DJ spinning 70s and 80s classics, themed decorations, dance floor, and retro snacks. "
            "Costume contest with prizes. Open to all ages."
        ),
        "category": "Nightlife",
        "city": "Chennai",
        "zone": "Anna Nagar",
        "venue": "VGP Golden Beach, ECR",
        "event_date": d(11),
        "event_time": "20:00",
        "price": 700.0,
        "total_seats": 300,
        "available_seats": 145,
        "image_emoji": "🕺",
        "organizer": "Retro Chennai",
        "lat": 13.0827,
        "lng": 80.2707,
    },
    {
        "title": "Tamil Film Screening",
        "description": (
            "A special curated screening of a classic Tamil cinema masterpiece at Sathyam Cinemas. "
            "Followed by a panel discussion with film critics and cinema historians. "
            "Includes complimentary popcorn and beverage."
        ),
        "category": "Arts",
        "city": "Chennai",
        "zone": "T. Nagar",
        "venue": "Sathyam Cinemas, Royapettah High Rd",
        "event_date": d(13),
        "event_time": "19:00",
        "price": 250.0,
        "total_seats": 150,
        "available_seats": 4,
        "image_emoji": "🎬",
        "organizer": "Cinema Heritage Foundation",
        "lat": 13.0600,
        "lng": 80.2437,
    },
    {
        "title": "Yoga by the Beach",
        "description": (
            "Start your morning with a transformative yoga session on Chennai's beautiful Elliot's Beach. "
            "Led by certified yoga instructor Priya Nair. "
            "Suitable for all levels. Mats provided. Followed by a healthy smoothie breakfast."
        ),
        "category": "Workshop",
        "city": "Chennai",
        "zone": "Besant Nagar",
        "venue": "Elliot's Beach, Besant Nagar",
        "event_date": d(10),
        "event_time": "06:00",
        "price": 300.0,
        "total_seats": 50,
        "available_seats": 8,
        "image_emoji": "🧘",
        "organizer": "Chennai Wellness Collective",
        "lat": 12.9987,
        "lng": 80.2707,
    },
    {
        "title": "Rock Night at Hard Rock",
        "description": (
            "Chennai's rock community comes alive at Hard Rock Cafe Nungambakkam. "
            "Five local rock bands battle it out for the title of Chennai's best band. "
            "Prizes worth ₹1 lakh for the winner. Loud, proud, and epic."
        ),
        "category": "Music",
        "city": "Chennai",
        "zone": "Nungambakkam",
        "venue": "Hard Rock Cafe Chennai, Nungambakkam High Rd",
        "event_date": d(14),
        "event_time": "20:30",
        "price": 900.0,
        "total_seats": 180,
        "available_seats": 62,
        "image_emoji": "🎸",
        "organizer": "Rock Chennai Events",
        "lat": 13.0569,
        "lng": 80.2424,
    },
    {
        "title": "IPL Super Final Watch",
        "description": (
            "The biggest IPL Watch Party in Chennai — live on massive screens at Forum Vijaya Mall. "
            "Multiple zones for different team fans, cricket trivia, lucky draws. "
            "Food and beverage packages available. Come early to get the best seats!"
        ),
        "category": "Sports",
        "city": "Chennai",
        "zone": "Velachery",
        "venue": "Forum Vijaya Mall, Vadapalani",
        "event_date": d(5),
        "event_time": "19:30",
        "price": 450.0,
        "total_seats": 350,
        "available_seats": 178,
        "image_emoji": "🏏",
        "organizer": "Sports Entertainment Chennai",
        "lat": 13.0012,
        "lng": 80.2102,
    },
    {
        "title": "Chennai Heritage Walk",
        "description": (
            "Discover the rich history of Chennai's oldest neighborhoods on this guided heritage walk. "
            "Explore colonial architecture, ancient temples, and vibrant bazaars of Mylapore and Egmore. "
            "Ends with a traditional South Indian breakfast at a local restaurant."
        ),
        "category": "Workshop",
        "city": "Chennai",
        "zone": "Egmore",
        "venue": "Egmore Museum Gate (Meeting Point)",
        "event_date": d(8),
        "event_time": "07:00",
        "price": 350.0,
        "total_seats": 30,
        "available_seats": 14,
        "image_emoji": "🏛️",
        "organizer": "Chennai Heritage Trust",
        "lat": 13.0785,
        "lng": 80.2619,
    },
    {
        "title": "Adyar Fusion Food Night",
        "description": (
            "A spectacular evening of Indo-fusion cuisine in the heart of Adyar. "
            "Top Chennai chefs compete in a live cook-off featuring fusion dishes. "
            "Tasting tokens included in ticket price. Vegetarian-friendly."
        ),
        "category": "Food",
        "city": "Chennai",
        "zone": "Adyar",
        "venue": "Adyar Depot Grounds",
        "event_date": d(17),
        "event_time": "17:30",
        "price": 550.0,
        "total_seats": 120,
        "available_seats": 53,
        "image_emoji": "🍽️",
        "organizer": "Gastronomy Chennai",
        "lat": 13.0012,
        "lng": 80.2565,
    },
    {
        "title": "Guindy Photography Exhibition",
        "description": (
            "Forty powerful photographs documenting Chennai's transformation over the last 50 years. "
            "Featuring work by 15 celebrated photographers. "
            "Free guided tours at 11 AM and 4 PM. Photography workshop on Day 2."
        ),
        "category": "Arts",
        "city": "Chennai",
        "zone": "Guindy",
        "venue": "Guindy National Park, Exhibition Pavilion",
        "event_date": d(19),
        "event_time": "10:00",
        "price": 150.0,
        "total_seats": 200,
        "available_seats": 112,
        "image_emoji": "🖼️",
        "organizer": "Chennai Photography Society",
        "lat": 13.0067,
        "lng": 80.2206,
    },
    {
        "title": "T. Nagar Fashion & Style Night",
        "description": (
            "Chennai's most glamorous fashion event returns to T. Nagar. "
            "Runway shows featuring upcoming designers, live styling sessions, and pop-up boutiques. "
            "Hosted at the iconic Sathyam venue. Dress to impress."
        ),
        "category": "Arts",
        "city": "Chennai",
        "zone": "T. Nagar",
        "venue": "GN Chetty Rd, T. Nagar",
        "event_date": d(21),
        "event_time": "19:30",
        "price": 650.0,
        "total_seats": 100,
        "available_seats": 29,
        "image_emoji": "👗",
        "organizer": "Chennai Fashion Week",
        "lat": 13.0418,
        "lng": 80.2341,
    },
    {
        "title": "Anna Nagar Sunday Night Market",
        "description": (
            "The vibrant Sunday Night Market in Anna Nagar comes alive with 100+ vendors, "
            "live street music, artisanal crafts, gourmet street food, and a lively atmosphere. "
            "Great for the whole family. Free entry, ticketed food zones."
        ),
        "category": "Food",
        "city": "Chennai",
        "zone": "Anna Nagar",
        "venue": "Anna Nagar Tower Park",
        "event_date": d(22),
        "event_time": "18:00",
        "price": 200.0,
        "total_seats": 500,
        "available_seats": 320,
        "image_emoji": "🏮",
        "organizer": "Nagar Bazaar Events",
        "lat": 13.0850,
        "lng": 80.2100,
    },
]


def seed_events(db):
    count = db.query(Event).count()
    if count > 0:
        return  # Already seeded

    for ev in EVENTS:
        event = Event(**ev)
        db.add(event)
    db.commit()
    print(f"Seeded {len(EVENTS)} events.")


def run_seed():
    db = SessionLocal()
    try:
        seed_events(db)
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
