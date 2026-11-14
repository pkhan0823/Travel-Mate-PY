import os
import json
import datetime
import streamlit as st
from google import genai

# Page Configuration
st.set_page_config(
    page_title="Globetrotter Travel & Expense Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Key Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6J4K5NGcJ9ODbu08gJCkua1q4EknxZqcX5V_B9AiGRngg")
USD_TO_INR = 83.5

def get_ai_client():
    if GEMINI_API_KEY:
        try:
            return genai.Client(api_key=GEMINI_API_KEY)
        except Exception as e:
            st.sidebar.warning(f"AI Client note: {e}")
    return None

# --- Curated Indian Tourist Destinations ---
CURATED_SUGGESTIONS = [
    {
        "id": "sug-agra", "city": "Agra", "country": "India", "category": "Cultural",
        "tag": "UNESCO Wonder", "duration_days": 3, "flight_price": 45, "est_budget": 280, "daily_avg": 55,
        "attractions": [{"name": "Taj Mahal Entry", "ticket": 14}, {"name": "Agra Fort", "ticket": 7}, {"name": "Fatehpur Sikri", "ticket": 6}],
        "description": "Home to the world-renowned Taj Mahal, Agra Fort, and masterpieces of Mughal imperial architecture."
    },
    {
        "id": "sug-jaipur", "city": "Jaipur", "country": "India", "category": "Cultural",
        "tag": "Pink City", "duration_days": 4, "flight_price": 60, "est_budget": 320, "daily_avg": 50,
        "attractions": [{"name": "Amer Fort & Palace", "ticket": 6}, {"name": "Hawa Mahal", "ticket": 3}, {"name": "Jantar Mantar", "ticket": 3}],
        "description": "Rajasthan's royal Pink City featuring massive hilltop forts, pink sandstone palaces, and vibrant bazaars."
    },
    {
        "id": "sug-varanasi", "city": "Varanasi", "country": "India", "category": "Cultural",
        "tag": "Spiritual Hub", "duration_days": 3, "flight_price": 65, "est_budget": 260, "daily_avg": 45,
        "attractions": [{"name": "Ganga Aarti Boat Ride", "ticket": 10}, {"name": "Kashi Vishwanath Corridor", "ticket": 0}, {"name": "Sarnath Stupa", "ticket": 4}],
        "description": "Spiritual heart of India along the sacred Ganges, famous for ancient ghats, evening aartis, and temples."
    },
    {
        "id": "sug-alleppey", "city": "Alleppey", "country": "India", "category": "Beach & Nature",
        "tag": "Backwaters", "duration_days": 4, "flight_price": 85, "est_budget": 420, "daily_avg": 70,
        "attractions": [{"name": "Overnight Houseboat Cruise", "ticket": 80}, {"name": "Marari Beach Walk", "ticket": 0}, {"name": "Canal Kayaking", "ticket": 15}],
        "description": "Scenic network of palm-fringed backwater canals, tranquil lagoons, and traditional luxury houseboats."
    },
    {
        "id": "sug-goa", "city": "Goa", "country": "India", "category": "Beach & Nature",
        "tag": "Sun & Beaches", "duration_days": 5, "flight_price": 75, "est_budget": 380, "daily_avg": 60,
        "attractions": [{"name": "Fort Aguada", "ticket": 3}, {"name": "Baga Beach Watersports", "ticket": 25}, {"name": "Dudhsagar Waterfalls", "ticket": 20}],
        "description": "Tropical coastal getaway famous for golden beaches, seafood shacks, vibrant nightlife, and Portuguese heritage."
    },
    {
        "id": "sug-manali", "city": "Manali", "country": "India", "category": "Beach & Nature",
        "tag": "Snow & Peaks", "duration_days": 5, "flight_price": 70, "est_budget": 360, "daily_avg": 55,
        "attractions": [{"name": "Solang Valley Adventure", "ticket": 30}, {"name": "Rohtang Pass Permit", "ticket": 12}, {"name": "Hadimba Temple", "ticket": 1}],
        "description": "Himalayan hill station surrounded by snowy peaks, alpine forests, Solang Valley, and adventure sports."
    },
    {
        "id": "sug-kashmir", "city": "Kashmir Valley", "country": "India", "category": "Beach & Nature",
        "tag": "Paradise on Earth", "duration_days": 5, "flight_price": 95, "est_budget": 480, "daily_avg": 75,
        "attractions": [{"name": "Dal Lake Shikara Ride", "ticket": 8}, {"name": "Gulmarg Gondola Cable Car", "ticket": 22}, {"name": "Shalimar Mughal Garden", "ticket": 2}],
        "description": "Regarded as Paradise on Earth, featuring Dal Lake houseboats, Gulmarg ski slopes, and Mughal gardens."
    },
    {
        "id": "sug-munnar", "city": "Munnar", "country": "India", "category": "Beach & Nature",
        "tag": "Misty Hills", "duration_days": 4, "flight_price": 70, "est_budget": 310, "daily_avg": 50,
        "attractions": [{"name": "Eravikulam National Park", "ticket": 5}, {"name": "Tata Tea Museum", "ticket": 2}, {"name": "Mattupetty Speedboat", "ticket": 6}],
        "description": "Serene rolling hills blanketed with green tea plantations, misty viewpoints, and cool mountain air."
    },
    {
        "id": "sug-ranthambore", "city": "Ranthambore", "country": "India", "category": "Beach & Nature",
        "tag": "Tiger Reserve", "duration_days": 3, "flight_price": 55, "est_budget": 340, "daily_avg": 60,
        "attractions": [{"name": "Jeep Tiger Safari", "ticket": 25}, {"name": "Ranthambore Fort Entry", "ticket": 2}, {"name": "Padam Lake", "ticket": 0}],
        "description": "Premier wildlife sanctuary renowned for Bengal tiger sightings, jungle trails, and an ancient hilltop fort."
    },
    {
        "id": "sug-havelock", "city": "Havelock Island", "country": "India", "category": "Beach & Nature",
        "tag": "Scuba & Coral", "duration_days": 5, "flight_price": 130, "est_budget": 580, "daily_avg": 85,
        "attractions": [{"name": "Radhanagar Beach Walk", "ticket": 0}, {"name": "Scuba Diving & Coral Tour", "ticket": 45}, {"name": "Elephant Beach Ferry", "ticket": 12}],
        "description": "Pristine Andaman island paradise boasting turquoise seas, powder-white sand beaches, and coral reefs."
    },
    {
        "id": "sug-amritsar", "city": "Amritsar", "country": "India", "category": "Cultural",
        "tag": "Golden Temple", "duration_days": 3, "flight_price": 60, "est_budget": 240, "daily_avg": 40,
        "attractions": [{"name": "Golden Temple", "ticket": 0}, {"name": "Wagah Border Ceremony", "ticket": 0}, {"name": "Jallianwala Bagh", "ticket": 0}],
        "description": "Spiritual center of Sikhism housing the glistening Golden Temple and historic memorials."
    },
    {
        "id": "sug-udaipur", "city": "Udaipur", "country": "India", "category": "Cultural",
        "tag": "City of Lakes", "duration_days": 4, "flight_price": 65, "est_budget": 370, "daily_avg": 60,
        "attractions": [{"name": "City Palace Complex", "ticket": 5}, {"name": "Lake Pichola Boat Cruise", "ticket": 7}, {"name": "Saheliyon-ki-Bari", "ticket": 2}],
        "description": "Romantic City of Lakes surrounded by marble palaces, lakeside temples, and the Aravali hills."
    },
    {
        "id": "sug-darjeeling", "city": "Darjeeling", "country": "India", "category": "Beach & Nature",
        "tag": "Tea & Toy Train", "duration_days": 4, "flight_price": 80, "est_budget": 330, "daily_avg": 50,
        "attractions": [{"name": "Toy Train Steam Ride", "ticket": 18}, {"name": "Tiger Hill Sunrise", "ticket": 2}, {"name": "Happy Valley Tea Estate", "ticket": 3}],
        "description": "Iconic hill town in West Bengal renowned for tea gardens, UNESCO toy train, and Kanchenjunga views."
    },
    {
        "id": "sug-rishikesh", "city": "Rishikesh", "country": "India", "category": "Cultural",
        "tag": "Yoga & Rafting", "duration_days": 3, "flight_price": 50, "est_budget": 250, "daily_avg": 42,
        "attractions": [{"name": "River Rafting", "ticket": 12}, {"name": "Beatles Ashram", "ticket": 7}, {"name": "Triveni Ghat Evening Aarti", "ticket": 0}],
        "description": "World Yoga Capital along the Ganges, renowned for white water rafting, suspension bridges, and ashrams."
    },
    {
        "id": "sug-khajuraho", "city": "Khajuraho", "country": "India", "category": "Cultural",
        "tag": "UNESCO Heritage", "duration_days": 3, "flight_price": 65, "est_budget": 270, "daily_avg": 45,
        "attractions": [{"name": "Western Temples Complex", "ticket": 8}, {"name": "Light & Sound Show", "ticket": 4}, {"name": "Raneh Falls Canyon", "ticket": 3}],
        "description": "UNESCO World Heritage site celebrated for its intricately carved medieval temples and sculptures."
    },
    {
        "id": "sug-gangtok", "city": "Gangtok", "country": "India", "category": "Beach & Nature",
        "tag": "Sikkim Peaks", "duration_days": 5, "flight_price": 85, "est_budget": 410, "daily_avg": 60,
        "attractions": [{"name": "Tsomgo Glacial Lake Tour", "ticket": 15}, {"name": "Rumtek Monastery", "ticket": 1}, {"name": "Nathula Pass Permit", "ticket": 12}],
        "description": "Vibrant capital of Sikkim offering breathtaking Mt. Kanchenjunga panoramas and Buddhist monasteries."
    },
    {
        "id": "sug-mysore", "city": "Mysore", "country": "India", "category": "Cultural",
        "tag": "Heritage Palace", "duration_days": 3, "flight_price": 55, "est_budget": 260, "daily_avg": 45,
        "attractions": [{"name": "Mysore Grand Palace", "ticket": 2}, {"name": "Chamundi Hill Temple", "ticket": 0}, {"name": "Brindavan Gardens", "ticket": 1}],
        "description": "City of Palaces celebrated for opulent royal architecture, sandalwood crafts, and cultural festivals."
    },
    {
        "id": "sug-kaziranga", "city": "Kaziranga", "country": "India", "category": "Beach & Nature",
        "tag": "Rhino Wildlife", "duration_days": 4, "flight_price": 90, "est_budget": 390, "daily_avg": 65,
        "attractions": [{"name": "Elephant Safari Rhino Tour", "ticket": 22}, {"name": "Jeep Safari Central Range", "ticket": 18}, {"name": "Assam Orchid Park", "ticket": 2}],
        "description": "UNESCO World Heritage floodplains of Assam, home to the great one-horned rhinoceroses."
    },
    {
        "id": "sug-ajanta-ellora", "city": "Aurangabad", "country": "India", "category": "Cultural",
        "tag": "Ancient Caves", "duration_days": 3, "flight_price": 60, "est_budget": 280, "daily_avg": 45,
        "attractions": [{"name": "Ellora Kailasa Temple", "ticket": 7}, {"name": "Ajanta Buddhist Caves", "ticket": 7}, {"name": "Bibi Ka Maqbara", "ticket": 3}],
        "description": "Monumental rock-cut caves carved into cliffs, featuring ancient Buddhist murals, Hindu temples, and shrines."
    },
    {
        "id": "sug-kutch", "city": "Rann of Kutch", "country": "India", "category": "Beach & Nature",
        "tag": "White Desert", "duration_days": 4, "flight_price": 75, "est_budget": 390, "daily_avg": 65,
        "attractions": [{"name": "White Rann Desert Permit", "ticket": 2}, {"name": "Kalo Dungar (Black Hill)", "ticket": 1}, {"name": "Hodka Village Craft", "ticket": 0}],
        "description": "Vast white salt desert in Gujarat, world-famous for the vibrant Rann Utsav festival and moonlit sands."
    }
]

# --- Session State Initialization ---
if "trips" not in st.session_state:
    st.session_state.trips = {}
if "selected_trip_id" not in st.session_state:
    st.session_state.selected_trip_id = None
if "currency_mode" not in st.session_state:
    st.session_state.currency_mode = "Both ($ / ₹)"
if "ai_dashboard_message" not in st.session_state:
    st.session_state.ai_dashboard_message = "✨ Pro Tip: Traveling to Jaipur or Varanasi? Train passes and local guided tours save up to 40% ($50 / ₹4,100) compared to last-minute flights."

# --- Helper: Currency Formatter ---
def fmt_money(usd_amt):
    usd = float(usd_amt or 0)
    inr = int(round(usd * USD_TO_INR))
    mode = st.session_state.currency_mode
    if mode == "Both ($ / ₹)":
        return f"${usd:,.2f} / ₹{inr:,}"
    elif mode == "INR (₹)":
        return f"₹{inr:,}"
    else:
        return f"${usd:,.2f}"

def calculate_trip_total(trip):
    t_cost = sum(t['cost'] for t in trip.get('transportation', []))
    a_cost = sum(a['cost'] for a in trip.get('accommodations', []))
    act_cost = sum(act['cost'] for act in trip.get('activities', []))
    m_cost = sum(e['amount'] for e in trip.get('expenses', []))
    return t_cost + a_cost + act_cost + m_cost

# --- Sidebar Controls ---
st.sidebar.title("✈️ Globetrotter")
st.sidebar.caption("AI Travel & Expense Dashboard")

# Currency Toggle
st.session_state.currency_mode = st.sidebar.radio(
    "💱 Display Currency",
    ["Both ($ / ₹)", "USD ($)", "INR (₹)"],
    index=0
)
st.sidebar.info(f"Conversion Benchmark: 1 USD ≈ {USD_TO_INR} INR")

# Navigation
page = st.sidebar.selectbox(
    "Navigation Menu",
    ["📊 Dashboard & Suggestions", "🧳 Trip Manager", "📈 Reports & Analytics", "🤖 AI Travel Assistant"]
)

# --- PAGE 1: DASHBOARD & SUGGESTIONS ---
if page == "📊 Dashboard & Suggestions":
    st.title("Travel Dashboard & Live Ticket Benchmarks")

    # AI Banner
    with st.container():
        col_banner, col_btn = st.columns([5, 1])
        with col_banner:
            st.info(f"💡 **AI Smart Travel Advisor:** {st.session_state.ai_dashboard_message}")
        with col_btn:
            if st.button("🔄 Refresh Tip"):
                client = get_ai_client()
                if client:
                    try:
                        resp = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents="Give a short 2-sentence travel advice tip for Indian destinations with ticket price benchmarks in USD ($) and INR (₹)."
                        )
                        st.session_state.ai_dashboard_message = resp.text.strip()
                        st.rerun()
                    except Exception as e:
                        st.warning(f"AI: {e}")

    # Top KPI Metrics
    total_trips = len(st.session_state.trips)
    total_budget = sum(t.get('budget', 0) for t in st.session_state.trips.values())
    total_spent = sum(calculate_trip_total(t) for t in st.session_state.trips.values())
    utilization = (total_spent / total_budget * 100) if total_budget > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Trips Registered", total_trips)
    m2.metric("Total Budget Allocated", fmt_money(total_budget))
    m3.metric("Total Actual Spending", fmt_money(total_spent))
    m4.metric("Budget Utilization", f"{utilization:.1f}%")

    st.markdown("---")

    # Destination Suggestions
    st.subheader("🌟 Top Tourist Destinations & Live Ticket Benchmarks")
    cat_filter = st.radio("Category Filter:", ["All", "Cultural", "Beach & Nature", "Budget (< ₹30,000 / $360)"], horizontal=True)

    filtered = CURATED_SUGGESTIONS
    if cat_filter == "Cultural":
        filtered = [s for s in CURATED_SUGGESTIONS if s['category'] == "Cultural"]
    elif cat_filter == "Beach & Nature":
        filtered = [s for s in CURATED_SUGGESTIONS if s['category'] == "Beach & Nature"]
    elif cat_filter == "Budget (< ₹30,000 / $360)":
        filtered = [s for s in CURATED_SUGGESTIONS if s['est_budget'] <= 360]

    # Grid of Suggestions Cards (3 columns)
    cols = st.columns(3)
    for idx, item in enumerate(filtered):
        with cols[idx % 3]:
            with st.container(border=True):
                st.markdown(f"### {item['city']}, {item['country']}")
                st.caption(f"🏷️ {item['tag']} • ⏱️ {item['duration_days']} Days / {item['duration_days']-1} Nights")
                st.write(item['description'])
                st.markdown(f"**✈️ Flight/Travel Ticket:** `{fmt_money(item['flight_price'])}`")
                st.markdown(f"**💰 Est. Total Budget:** `{fmt_money(item['est_budget'])}`")
                
                with st.expander("🎫 Sightseeing Tickets"):
                    for att in item['attractions']:
                        fee_str = "Free" if att['ticket'] == 0 else fmt_money(att['ticket'])
                        st.write(f"- **{att['name']}:** {fee_str}")

                if st.button(f"⚡ Plan Trip to {item['city']}", key=f"btn_{item['id']}"):
                    tid = f"{item['city'][:3].upper()}2026"
                    today = datetime.date.today()
                    st.session_state.trips[tid] = {
                        "trip_id": tid,
                        "name": f"{item['city']} Tour",
                        "start_date": str(today + datetime.timedelta(days=14)),
                        "end_date": str(today + datetime.timedelta(days=14 + item['duration_days'])),
                        "description": item['description'],
                        "budget": float(item['est_budget']),
                        "destinations": [{"city": item['city'], "country": item['country'], "dates": "Day 1-4"}],
                        "itinerary": [],
                        "transportation": [{"type": "Flight", "details": f"Travel to {item['city']}", "cost": float(item['flight_price'])}],
                        "accommodations": [],
                        "activities": [],
                        "expenses": []
                    }
                    st.session_state.selected_trip_id = tid
                    st.success(f"Trip '{item['city']} Tour' created successfully! Visit 'Trip Manager' tab to customize.")

# --- PAGE 2: TRIP MANAGER ---
elif page == "🧳 Trip Manager":
    st.title("Trip & Expense Manager")

    # Trip Creation Section
    with st.expander("➕ Create a New Custom Trip", expanded=len(st.session_state.trips) == 0):
        with st.form("create_trip_form"):
            c1, c2 = st.columns(2)
            new_tid = c1.text_input("Trip ID (e.g. DEL2026)")
            new_name = c2.text_input("Trip Name (e.g. Golden Triangle Tour)")
            d1, d2, d3 = st.columns(3)
            start_d = d1.date_input("Start Date")
            end_d = d2.date_input("End Date")
            init_budget = d3.number_input("Budget in USD ($)", min_value=0.0, step=50.0)
            desc = st.text_area("Trip Description")
            submit_trip = st.form_submit_button("Create Trip")

            if submit_trip:
                if not new_tid or not new_name:
                    st.error("Please fill in Trip ID and Trip Name.")
                elif new_tid in st.session_state.trips:
                    st.error("Trip ID already exists!")
                else:
                    st.session_state.trips[new_tid] = {
                        "trip_id": new_tid, "name": new_name,
                        "start_date": str(start_d), "end_date": str(end_d),
                        "description": desc, "budget": float(init_budget),
                        "destinations": [], "itinerary": [],
                        "transportation": [], "accommodations": [],
                        "activities": [], "expenses": []
                    }
                    st.session_state.selected_trip_id = new_tid
                    st.success(f"Trip '{new_name}' created!")
                    st.rerun()

    # Active Trip Selector
    if st.session_state.trips:
        trip_ids = list(st.session_state.trips.keys())
        current_id = st.selectbox(
            "Select Trip to Manage:",
            trip_ids,
            index=trip_ids.index(st.session_state.selected_trip_id) if st.session_state.selected_trip_id in trip_ids else 0
        )
        st.session_state.selected_trip_id = current_id
        trip = st.session_state.trips[current_id]

        spent = calculate_trip_total(trip)
        rem = trip['budget'] - spent
        col_t1, col_t2, col_t3 = st.columns(3)
        col_t1.metric("Trip Budget", fmt_money(trip['budget']))
        col_t2.metric("Total Spent", fmt_money(spent))
        col_t3.metric("Remaining Balance", fmt_money(rem))

        # Sub-Forms Tabs
        t1, t2, t3, t4, t5 = st.tabs(["✈️ Transport & Tickets", "🏨 Accommodation", "🎟️ Activities", "💵 General Expenses", "🗺️ Destinations & Itinerary"])

        # 1. Transport & Tickets
        with t1:
            st.subheader("Log Transportation & Ticket Costs")
            with st.form("trans_form"):
                tt1, tt2, tt3 = st.columns(3)
                t_type = tt1.selectbox("Type", ["Flight", "Train", "Bus/Ferry", "Car Rental"])
                t_details = tt2.text_input("Details (e.g. Delhi to Jaipur Express)")
                t_cost = tt3.number_input("Cost in USD ($)", min_value=0.0, step=10.0)
                if st.form_submit_button("Add Transportation Ticket"):
                    trip['transportation'].append({"type": t_type, "details": t_details, "cost": float(t_cost)})
                    st.success("Ticket logged!")
                    st.rerun()

            if trip['transportation']:
                st.table([{"Type": t['type'], "Details": t['details'], "Price": fmt_money(t['cost'])} for t in trip['transportation']])

        # 2. Accommodations
        with t2:
            st.subheader("Log Stays & Hotels")
            with st.form("accom_form"):
                ac1, ac2 = st.columns(2)
                h_name = ac1.text_input("Hotel / Property Name")
                h_cost = ac2.number_input("Total Stay Cost in USD ($)", min_value=0.0, step=20.0)
                if st.form_submit_button("Log Accommodation"):
                    trip['accommodations'].append({"name": h_name, "cost": float(h_cost)})
                    st.success("Stay logged!")
                    st.rerun()

            if trip['accommodations']:
                st.table([{"Property": a['name'], "Cost": fmt_money(a['cost'])} for a in trip['accommodations']])

        # 3. Activities
        with t3:
            st.subheader("Attractions, Tours & Entry Passes")
            with st.form("act_form"):
                act1, act2 = st.columns(2)
                act_name = act1.text_input("Activity (e.g. Scuba Dive, Taj Mahal Ticket)")
                act_cost = act2.number_input("Cost in USD ($)", min_value=0.0, step=5.0)
                if st.form_submit_button("Record Activity Ticket"):
                    trip['activities'].append({"name": act_name, "cost": float(act_cost)})
                    st.success("Activity recorded!")
                    st.rerun()

            if trip['activities']:
                st.table([{"Activity": a['name'], "Cost": fmt_money(a['cost'])} for a in trip['activities']])

        # 4. General Expenses
        with t4:
            st.subheader("Daily Meals, Shopping & Miscellaneous")
            with st.form("exp_form"):
                ex1, ex2 = st.columns(2)
                cat = ex1.selectbox("Category", ["Food & Dining", "Shopping", "Local Transport", "Emergency"])
                amt = ex2.number_input("Amount in USD ($)", min_value=0.0, step=5.0)
                if st.form_submit_button("Record Expense"):
                    trip['expenses'].append({"category": cat, "amount": float(amt)})
                    st.success("Expense logged!")
                    st.rerun()

            if trip['expenses']:
                st.table([{"Category": e['category'], "Amount": fmt_money(e['amount'])} for e in trip['expenses']])

        # 5. Destinations & Itinerary
        with t5:
            st.subheader("Trip Cities & Itinerary")
            with st.form("dest_form"):
                d_c1, d_c2 = st.columns(2)
                d_city = d_c1.text_input("City")
                d_country = d_c2.text_input("Country", value="India")
                if st.form_submit_button("Add Destination"):
                    trip['destinations'].append({"city": d_city, "country": d_country})
                    st.success("Destination saved!")
                    st.rerun()

            for d in trip['destinations']:
                st.write(f"📍 **{d['city']}, {d['country']}**")
    else:
        st.info("No trips created yet. Use the expander above or pick from suggestions on the Dashboard.")

# --- PAGE 3: REPORTS & ANALYTICS ---
elif page == "📈 Reports & Analytics":
    st.title("Expense Reports & Visual Breakdown")
    if not st.session_state.trips:
        st.info("Register a trip and add expenses to view analytics.")
    else:
        for tid, trip in st.session_state.trips.items():
            with st.expander(f"📊 Report: {trip['name']} ({trip['trip_id']})", expanded=True):
                spent = calculate_trip_total(trip)
                st.write(f"**Allocated Budget:** {fmt_money(trip['budget'])} | **Total Spent:** {fmt_money(spent)}")
                
                trans_sum = sum(t['cost'] for t in trip['transportation'])
                accom_sum = sum(a['cost'] for a in trip['accommodations'])
                act_sum = sum(act['cost'] for act in trip['activities'])
                misc_sum = sum(e['amount'] for e in trip['expenses'])

                chart_data = {
                    "Transport & Tickets": trans_sum,
                    "Accommodation": accom_sum,
                    "Sightseeing & Passes": act_sum,
                    "Meals & Misc": misc_sum
                }
                st.bar_chart(chart_data)

# --- PAGE 4: AI TRAVEL ASSISTANT ---
elif page == "🤖 AI Travel Assistant":
    st.title("🤖 AI Travel & Expense Intelligence")
    st.caption("Ask natural language questions about your travel itinerary, conversion between $ and ₹, or budget checks.")

    user_query = st.text_input("Ask AI a question:", placeholder="e.g. Can I afford a ₹10,000 hotel in Jaipur with my remaining budget? or Suggest free things in Goa")

    if st.button("Ask Gemini AI") and user_query:
        client = get_ai_client()
        if not client:
            st.error("Gemini API key is not configured.")
        else:
            with st.spinner("Analyzing travel plans with Gemini AI..."):
                try:
                    all_trips_snapshot = json.dumps(st.session_state.trips, indent=2)
                    prompt = (
                        "You are an AI Travel & Budget Assistant for the Globetrotter App.\n"
                        f"Current User Trips Database:\n{all_trips_snapshot}\n\n"
                        "Instructions:\n"
                        "- Always mention amounts in both USD ($) and Indian Rupees (₹) using 1 USD = 83.5 INR.\n"
                        "- Give concise, structured answers with bullet points.\n"
                        f"User Query: {user_query}"
                    )
                    resp = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt
                    )
                    st.markdown("### 💬 AI Response:")
                    st.write(resp.text)
                except Exception as e:
                    st.error(f"AI Error: {e}")
