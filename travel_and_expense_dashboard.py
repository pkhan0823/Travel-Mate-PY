import os
import json
import streamlit as st
import streamlit.components.v1 as components

# Page Configuration
st.set_page_config(
    page_title="Travel_Mate - AI Travel & Expense Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit's default headers/padding so your Tailwind dashboard fills the entire screen
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }
    iframe {
        border: none !important;
        width: 100% !important;
        height: 100vh !important;
    }
</style>
""", unsafe_allow_html=True)

# API Key Resolution
def get_api_key():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6J4K5NGcJ9ODbu08gJCkua1q4EknxZqcX5V_B9AiGRngg")

API_KEY = get_api_key()

# Complete 20 Curated Indian Tourist Destinations
CURATED_SUGGESTIONS = [
    {
        "id": "sug-agra", "city": "Agra", "country": "India", "category": "Cultural",
        "tag": "UNESCO Wonder", "tag_color": "bg-rose-50 text-rose-600", "icon": "fa-monument",
        "duration_days": 3, "flight_price": 45, "est_budget": 280, "daily_avg": 55,
        "attractions": [{"name": "Taj Mahal Entry", "ticket": 14}, {"name": "Agra Fort", "ticket": 7}, {"name": "Fatehpur Sikri", "ticket": 6}],
        "description": "Home to the world-renowned Taj Mahal, Agra Fort, and masterpieces of Mughal imperial architecture."
    },
    {
        "id": "sug-jaipur", "city": "Jaipur", "country": "India", "category": "Cultural",
        "tag": "Pink City", "tag_color": "bg-rose-50 text-rose-600", "icon": "fa-landmark",
        "duration_days": 4, "flight_price": 60, "est_budget": 320, "daily_avg": 50,
        "attractions": [{"name": "Amer Fort & Palace", "ticket": 6}, {"name": "Hawa Mahal", "ticket": 3}, {"name": "Jantar Mantar", "ticket": 3}],
        "description": "Rajasthan's royal Pink City featuring massive hilltop forts, pink sandstone palaces, and vibrant bazaars."
    },
    {
        "id": "sug-varanasi", "city": "Varanasi", "country": "India", "category": "Cultural",
        "tag": "Spiritual Hub", "tag_color": "bg-amber-50 text-amber-700", "icon": "fa-om",
        "duration_days": 3, "flight_price": 65, "est_budget": 260, "daily_avg": 45,
        "attractions": [{"name": "Ganga Aarti Boat Ride", "ticket": 10}, {"name": "Kashi Vishwanath Corridor", "ticket": 0}, {"name": "Sarnath Stupa", "ticket": 4}],
        "description": "Spiritual heart of India along the sacred Ganges, famous for ancient ghats, evening aartis, and temples."
    },
    {
        "id": "sug-alleppey", "city": "Alleppey", "country": "India", "category": "Beach & Nature",
        "tag": "Backwaters", "tag_color": "bg-emerald-50 text-emerald-600", "icon": "fa-ship",
        "duration_days": 4, "flight_price": 85, "est_budget": 420, "daily_avg": 70,
        "attractions": [{"name": "Overnight Houseboat Cruise", "ticket": 80}, {"name": "Marari Beach Walk", "ticket": 0}, {"name": "Canal Kayaking", "ticket": 15}],
        "description": "Scenic network of palm-fringed backwater canals, tranquil lagoons, and traditional luxury houseboats."
    },
    {
        "id": "sug-goa", "city": "Goa", "country": "India", "category": "Beach & Nature",
        "tag": "Sun & Beaches", "tag_color": "bg-teal-50 text-teal-700", "icon": "fa-umbrella-beach",
        "duration_days": 5, "flight_price": 75, "est_budget": 380, "daily_avg": 60,
        "attractions": [{"name": "Fort Aguada", "ticket": 3}, {"name": "Baga Beach Watersports", "ticket": 25}, {"name": "Dudhsagar Waterfalls", "ticket": 20}],
        "description": "Tropical coastal haven famous for golden beaches, seafood shacks, vibrant nightlife, and Portuguese heritage."
    },
    {
        "id": "sug-manali", "city": "Manali", "country": "India", "category": "Beach & Nature",
        "tag": "Snow & Peaks", "tag_color": "bg-indigo-50 text-indigo-600", "icon": "fa-mountain",
        "duration_days": 5, "flight_price": 70, "est_budget": 360, "daily_avg": 55,
        "attractions": [{"name": "Solang Valley Adventure", "ticket": 30}, {"name": "Rohtang Pass Permit", "ticket": 12}, {"name": "Hadimba Temple", "ticket": 1}],
        "description": "Himalayan hill station surrounded by snowy mountain peaks, alpine forests, Solang Valley, and adventure sports."
    },
    {
        "id": "sug-kashmir", "city": "Kashmir Valley", "country": "India", "category": "Beach & Nature",
        "tag": "Paradise on Earth", "tag_color": "bg-cyan-50 text-cyan-700", "icon": "fa-snowflake",
        "duration_days": 5, "flight_price": 95, "est_budget": 480, "daily_avg": 75,
        "attractions": [{"name": "Dal Lake Shikara Ride", "ticket": 8}, {"name": "Gulmarg Gondola Cable Car", "ticket": 22}, {"name": "Shalimar Mughal Garden", "ticket": 2}],
        "description": "Regarded as Paradise on Earth, featuring Dal Lake houseboats, Gulmarg ski slopes, and Mughal gardens."
    },
    {
        "id": "sug-munnar", "city": "Munnar", "country": "India", "category": "Beach & Nature",
        "tag": "Misty Hills", "tag_color": "bg-emerald-50 text-emerald-600", "icon": "fa-leaf",
        "duration_days": 4, "flight_price": 70, "est_budget": 310, "daily_avg": 50,
        "attractions": [{"name": "Eravikulam National Park", "ticket": 5}, {"name": "Tata Tea Museum", "ticket": 2}, {"name": "Mattupetty Speedboat", "ticket": 6}],
        "description": "Serene rolling hills blanketed with green tea plantations, misty viewpoints, and cool mountain air."
    },
    {
        "id": "sug-ranthambore", "city": "Ranthambore", "country": "India", "category": "Beach & Nature",
        "tag": "Tiger Reserve", "tag_color": "bg-amber-50 text-amber-700", "icon": "fa-paw",
        "duration_days": 3, "flight_price": 55, "est_budget": 340, "daily_avg": 60,
        "attractions": [{"name": "Jeep Tiger Safari", "ticket": 25}, {"name": "Ranthambore Fort Entry", "ticket": 2}, {"name": "Padam Lake", "ticket": 0}],
        "description": "Premier wildlife sanctuary renowned for Bengal tiger sightings, jungle trails, and an ancient hilltop fort."
    },
    {
        "id": "sug-havelock", "city": "Havelock Island", "country": "India", "category": "Beach & Nature",
        "tag": "Scuba & Coral", "tag_color": "bg-blue-50 text-blue-700", "icon": "fa-water",
        "duration_days": 5, "flight_price": 130, "est_budget": 580, "daily_avg": 85,
        "attractions": [{"name": "Radhanagar Beach Walk", "ticket": 0}, {"name": "Scuba Diving & Coral Tour", "ticket": 45}, {"name": "Elephant Beach Ferry", "ticket": 12}],
        "description": "Pristine Andaman island paradise boasting turquoise seas, powder-white sand beaches, and coral reefs."
    },
    {
        "id": "sug-amritsar", "city": "Amritsar", "country": "India", "category": "Cultural",
        "tag": "Golden Temple", "tag_color": "bg-yellow-50 text-yellow-700", "icon": "fa-hands-praying",
        "duration_days": 3, "flight_price": 60, "est_budget": 240, "daily_avg": 40,
        "attractions": [{"name": "Golden Temple", "ticket": 0}, {"name": "Wagah Border Ceremony", "ticket": 0}, {"name": "Jallianwala Bagh", "ticket": 0}],
        "description": "Spiritual center of Sikhism housing the glistening Golden Temple and historic memorials."
    },
    {
        "id": "sug-udaipur", "city": "Udaipur", "country": "India", "category": "Cultural",
        "tag": "City of Lakes", "tag_color": "bg-purple-50 text-purple-700", "icon": "fa-crown",
        "duration_days": 4, "flight_price": 65, "est_budget": 370, "daily_avg": 60,
        "attractions": [{"name": "City Palace Complex", "ticket": 5}, {"name": "Lake Pichola Boat Cruise", "ticket": 7}, {"name": "Saheliyon-ki-Bari", "ticket": 2}],
        "description": "Romantic City of Lakes surrounded by marble palaces, lakeside temples, and the Aravali hills."
    },
    {
        "id": "sug-darjeeling", "city": "Darjeeling", "country": "India", "category": "Beach & Nature",
        "tag": "Tea & Toy Train", "tag_color": "bg-emerald-50 text-emerald-600", "icon": "fa-train",
        "duration_days": 4, "flight_price": 80, "est_budget": 330, "daily_avg": 50,
        "attractions": [{"name": "Toy Train Steam Ride", "ticket": 18}, {"name": "Tiger Hill Sunrise", "ticket": 2}, {"name": "Happy Valley Tea Estate", "ticket": 3}],
        "description": "Iconic hill town in West Bengal renowned for tea gardens, UNESCO toy train, and Kanchenjunga views."
    },
    {
        "id": "sug-rishikesh", "city": "Rishikesh", "country": "India", "category": "Cultural",
        "tag": "Yoga & Rafting", "tag_color": "bg-teal-50 text-teal-700", "icon": "fa-person-hiking",
        "duration_days": 3, "flight_price": 50, "est_budget": 250, "daily_avg": 42,
        "attractions": [{"name": "River Rafting", "ticket": 12}, {"name": "Beatles Ashram", "ticket": 7}, {"name": "Triveni Ghat Evening Aarti", "ticket": 0}],
        "description": "World Yoga Capital along the Ganges, renowned for white water rafting, suspension bridges, and ashrams."
    },
    {
        "id": "sug-khajuraho", "city": "Khajuraho", "country": "India", "category": "Cultural",
        "tag": "UNESCO Heritage", "tag_color": "bg-amber-50 text-amber-700", "icon": "fa-monument",
        "duration_days": 3, "flight_price": 65, "est_budget": 270, "daily_avg": 45,
        "attractions": [{"name": "Western Temples Complex", "ticket": 8}, {"name": "Light & Sound Show", "ticket": 4}, {"name": "Raneh Falls Canyon", "ticket": 3}],
        "description": "UNESCO World Heritage site celebrated for its intricately carved medieval temples and sculptures."
    },
    {
        "id": "sug-gangtok", "city": "Gangtok", "country": "India", "category": "Beach & Nature",
        "tag": "Sikkim Peaks", "tag_color": "bg-indigo-50 text-indigo-600", "icon": "fa-mountain-sun",
        "duration_days": 5, "flight_price": 85, "est_budget": 410, "daily_avg": 60,
        "attractions": [{"name": "Tsomgo Glacial Lake Tour", "ticket": 15}, {"name": "Rumtek Monastery", "ticket": 1}, {"name": "Nathula Pass Permit", "ticket": 12}],
        "description": "Vibrant capital of Sikkim offering breathtaking Mt. Kanchenjunga panoramas and Buddhist monasteries."
    },
    {
        "id": "sug-mysore", "city": "Mysore", "country": "India", "category": "Cultural",
        "tag": "Heritage Palace", "tag_color": "bg-yellow-50 text-yellow-700", "icon": "fa-chess-rook",
        "duration_days": 3, "flight_price": 55, "est_budget": 260, "daily_avg": 45,
        "attractions": [{"name": "Mysore Grand Palace", "ticket": 2}, {"name": "Chamundi Hill Temple", "ticket": 0}, {"name": "Brindavan Gardens", "ticket": 1}],
        "description": "City of Palaces celebrated for opulent royal architecture, sandalwood crafts, and cultural festivals."
    },
    {
        "id": "sug-kaziranga", "city": "Kaziranga", "country": "India", "category": "Beach & Nature",
        "tag": "Rhino Wildlife", "tag_color": "bg-emerald-50 text-emerald-600", "icon": "fa-shield-halved",
        "duration_days": 4, "flight_price": 90, "est_budget": 390, "daily_avg": 65,
        "attractions": [{"name": "Elephant Safari Rhino Tour", "ticket": 22}, {"name": "Jeep Safari Central Range", "ticket": 18}, {"name": "Assam Orchid Park", "ticket": 2}],
        "description": "UNESCO World Heritage floodplains of Assam, home to the great one-horned rhinoceroses."
    },
    {
        "id": "sug-ajanta-ellora", "city": "Aurangabad", "country": "India", "category": "Cultural",
        "tag": "Ancient Caves", "tag_color": "bg-purple-50 text-purple-700", "icon": "fa-gem",
        "duration_days": 3, "flight_price": 60, "est_budget": 280, "daily_avg": 45,
        "attractions": [{"name": "Ellora Kailasa Temple", "ticket": 7}, {"name": "Ajanta Buddhist Caves", "ticket": 7}, {"name": "Bibi Ka Maqbara", "ticket": 3}],
        "description": "Monumental rock-cut caves carved into cliffs, featuring ancient Buddhist murals, Hindu temples, and shrines."
    },
    {
        "id": "sug-kutch", "city": "Rann of Kutch", "country": "India", "category": "Beach & Nature",
        "tag": "White Desert", "tag_color": "bg-slate-50 text-slate-700", "icon": "fa-sun",
        "duration_days": 4, "flight_price": 75, "est_budget": 390, "daily_avg": 65,
        "attractions": [{"name": "White Rann Desert Permit", "ticket": 2}, {"name": "Kalo Dungar (Black Hill)", "ticket": 1}, {"name": "Hodka Village Craft", "ticket": 0}],
        "description": "Vast white salt desert in Gujarat, world-famous for the vibrant Rann Utsav festival and moonlit sands."
    }
]

# Serialized Data for JavaScript Injection
SUGGESTIONS_JSON = json.dumps(CURATED_SUGGESTIONS)

HTML_CODE = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Travel_Mate Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
        body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
    </style>
</head>
<body class="bg-slate-50 text-slate-800 min-h-screen flex flex-col" x-data="travelApp()">

    <!-- Header Navigation -->
    <header class="bg-indigo-600 text-white shadow-md sticky top-0 z-40">
        <div class="max-w-7xl mx-auto px-4 py-3 flex flex-col md:flex-row justify-between items-center gap-3">
            <div class="flex items-center space-x-3">
                <div class="bg-white/10 p-2.5 rounded-xl backdrop-blur-sm">
                    <i class="fa-solid fa-earth-asia text-2xl text-indigo-100"></i>
                </div>
                <div>
                    <h1 class="text-xl font-bold tracking-tight">Travel_Mate Dashboard</h1>
                    <p class="text-xs text-indigo-200">AI Travel Insights & Dual-Currency Expense Tracker</p>
                </div>
            </div>

            <div class="flex flex-wrap items-center gap-3">
                <!-- Currency Switcher Pill -->
                <div class="bg-indigo-800/80 p-1 rounded-xl flex items-center text-xs font-semibold shadow-inner border border-indigo-400/30">
                    <span class="px-2 text-indigo-200 text-[11px]"><i class="fa-solid fa-coins mr-1"></i> Currency:</span>
                    <button @click="currencyMode = 'both'" :class="currencyMode === 'both' ? 'bg-white text-indigo-700 shadow-sm' : 'text-indigo-200 hover:text-white'" class="px-2.5 py-1 rounded-lg transition">Both ($ / ₹)</button>
                    <button @click="currencyMode = 'USD'" :class="currencyMode === 'USD' ? 'bg-white text-indigo-700 shadow-sm' : 'text-indigo-200 hover:text-white'" class="px-2.5 py-1 rounded-lg transition">$ USD</button>
                    <button @click="currencyMode = 'INR'" :class="currencyMode === 'INR' ? 'bg-white text-indigo-700 shadow-sm' : 'text-indigo-200 hover:text-white'" class="px-2.5 py-1 rounded-lg transition">₹ INR</button>
                </div>

                <!-- Nav Tabs -->
                <nav class="flex gap-1.5">
                    <button @click="activeTab = 'dashboard'" :class="activeTab === 'dashboard' ? 'bg-indigo-700 shadow-inner' : 'hover:bg-indigo-500'" class="px-3.5 py-2 rounded-lg text-xs font-semibold transition flex items-center gap-1.5">
                        <i class="fa-solid fa-chart-pie"></i> Dashboard
                    </button>
                    <button @click="activeTab = 'trips'" :class="activeTab === 'trips' ? 'bg-indigo-700 shadow-inner' : 'hover:bg-indigo-500'" class="px-3.5 py-2 rounded-lg text-xs font-semibold transition flex items-center gap-1.5">
                        <i class="fa-solid fa-suitcase-rolling"></i> Trips & Details
                    </button>
                    <button @click="activeTab = 'reports'" :class="activeTab === 'reports' ? 'bg-indigo-700 shadow-inner' : 'hover:bg-indigo-500'" class="px-3.5 py-2 rounded-lg text-xs font-semibold transition flex items-center gap-1.5">
                        <i class="fa-solid fa-file-invoice-dollar"></i> Reports & AI
                    </button>
                </nav>
            </div>
        </div>
    </header>

    <!-- Main Content Area -->
    <main class="flex-grow max-w-7xl w-full mx-auto px-4 py-6 space-y-6">

        <!-- Toast Notifications -->
        <div x-show="toast.show" x-transition class="fixed bottom-5 right-5 z-50 px-4 py-3 rounded-xl shadow-lg text-white text-sm font-medium flex items-center gap-2" :class="toast.success ? 'bg-emerald-600' : 'bg-rose-600'">
            <i :class="toast.success ? 'fa-solid fa-circle-check' : 'fa-solid fa-circle-exclamation'"></i>
            <span x-text="toast.message"></span>
        </div>

        <!-- TAB 1: DASHBOARD OVERVIEW -->
        <div x-show="activeTab === 'dashboard'" class="space-y-6">

            <!-- AI RECOMMENDATION BANNER -->
            <div class="bg-gradient-to-r from-indigo-900 via-indigo-800 to-purple-900 text-white p-5 rounded-2xl shadow-md border border-indigo-700/50 relative overflow-hidden">
                <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                    <div class="flex items-start space-x-3.5">
                        <div class="p-3 bg-white/10 rounded-xl text-yellow-300 text-xl backdrop-blur-md shrink-0">
                            <i class="fa-solid fa-wand-magic-sparkles"></i>
                        </div>
                        <div>
                            <div class="flex items-center gap-2">
                                <span class="bg-yellow-400 text-indigo-950 font-bold text-[10px] uppercase px-2 py-0.5 rounded-full tracking-wider">Live AI Advisor</span>
                                <span class="text-xs text-indigo-200">Powered by Gemini AI</span>
                            </div>
                            <h2 class="text-base font-bold text-white mt-0.5">Smart AI Travel Recommendation</h2>
                            <p class="text-xs text-indigo-100/90 mt-1 whitespace-pre-line leading-relaxed max-w-4xl" x-text="aiDashboardMessage"></p>
                        </div>
                    </div>
                    <button @click="generateDailyTip" :disabled="aiTipLoading" class="shrink-0 px-3.5 py-2 bg-white/10 hover:bg-white/20 disabled:opacity-50 text-white rounded-xl text-xs font-semibold backdrop-blur-sm transition flex items-center gap-1.5 border border-white/15">
                        <i :class="aiTipLoading ? 'fa-solid fa-spinner fa-spin' : 'fa-solid fa-rotate'"></i>
                        <span>New Suggestion</span>
                    </button>
                </div>
            </div>

            <!-- Stats Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 flex items-center justify-between">
                    <div>
                        <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Trips</p>
                        <h3 class="text-2xl font-bold text-slate-800 mt-1" x-text="trips.length">0</h3>
                    </div>
                    <div class="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-xl flex items-center justify-center text-xl">
                        <i class="fa-solid fa-map-location-dot"></i>
                    </div>
                </div>
                <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 flex items-center justify-between">
                    <div>
                        <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Budget</p>
                        <h3 class="text-lg font-bold text-slate-800 mt-1" x-text="formatMoney(totalBudget)">$0 / ₹0</h3>
                    </div>
                    <div class="w-12 h-12 bg-emerald-50 text-emerald-600 rounded-xl flex items-center justify-center text-xl">
                        <i class="fa-solid fa-wallet"></i>
                    </div>
                </div>
                <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 flex items-center justify-between">
                    <div>
                        <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Expenses</p>
                        <h3 class="text-lg font-bold text-slate-800 mt-1" x-text="formatMoney(totalSpent)">$0 / ₹0</h3>
                    </div>
                    <div class="w-12 h-12 bg-amber-50 text-amber-600 rounded-xl flex items-center justify-center text-xl">
                        <i class="fa-solid fa-receipt"></i>
                    </div>
                </div>
                <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 flex items-center justify-between">
                    <div>
                        <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Overall Utilization</p>
                        <h3 class="text-2xl font-bold text-slate-800 mt-1" x-text="overallUtilization + '%'">0%</h3>
                    </div>
                    <div class="w-12 h-12 bg-purple-50 text-purple-600 rounded-xl flex items-center justify-center text-xl">
                        <i class="fa-solid fa-chart-line"></i>
                    </div>
                </div>
            </div>

            <!-- SUGGESTIONS & TICKET PRICES SHOWCASE CARD -->
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 space-y-5">
                <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-100 pb-4">
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
                            <h2 class="text-lg font-bold text-slate-800 flex items-center gap-2">
                                <i class="fa-solid fa-compass text-indigo-600"></i> Destinations, Flight Tickets & Budget Suggestions
                            </h2>
                        </div>
                        <p class="text-xs text-slate-500 mt-0.5">Explore 20 Indian destinations with flight benchmarks and attraction ticket fees.</p>
                    </div>

                    <!-- Filter Categories -->
                    <div class="flex flex-wrap gap-1.5 text-xs">
                        <button @click="sugFilter = 'All'" :class="sugFilter === 'All' ? 'bg-indigo-600 text-white font-medium' : 'bg-slate-100 hover:bg-slate-200 text-slate-600'" class="px-3 py-1.5 rounded-lg transition">All (20)</button>
                        <button @click="sugFilter = 'Under $1,000'" :class="sugFilter === 'Under $1,000' ? 'bg-indigo-600 text-white font-medium' : 'bg-slate-100 hover:bg-slate-200 text-slate-600'" class="px-3 py-1.5 rounded-lg transition"><i class="fa-solid fa-tag mr-1"></i> Budget (< ₹30,000 / $360)</button>
                        <button @click="sugFilter = 'Beach & Nature'" :class="sugFilter === 'Beach & Nature' ? 'bg-indigo-600 text-white font-medium' : 'bg-slate-100 hover:bg-slate-200 text-slate-600'" class="px-3 py-1.5 rounded-lg transition">Beach & Nature</button>
                        <button @click="sugFilter = 'Cultural'" :class="sugFilter === 'Cultural' ? 'bg-indigo-600 text-white font-medium' : 'bg-slate-100 hover:bg-slate-200 text-slate-600'" class="px-3 py-1.5 rounded-lg transition">Cultural</button>
                    </div>
                </div>

                <!-- Custom AI Suggestion Prompt Bar -->
                <div class="bg-gradient-to-r from-indigo-50 via-purple-50 to-slate-50 p-4 rounded-xl border border-indigo-100 flex flex-col sm:flex-row gap-3 items-center">
                    <div class="text-indigo-600 text-xl hidden sm:block">
                        <i class="fa-solid fa-sparkles"></i>
                    </div>
                    <div class="flex-grow w-full">
                        <input type="text" x-model="aiPromptSuggest" @keydown.enter="generateCustomAISuggestions" placeholder="Ask AI for custom destinations (e.g. 'Beach vacation under ₹50,000' or '4-day mountain trek')..." class="w-full px-3.5 py-2 rounded-lg border border-indigo-200 bg-white text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-sm">
                    </div>
                    <button @click="generateCustomAISuggestions" :disabled="aiSugLoading" class="w-full sm:w-auto px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-400 text-white text-xs font-semibold rounded-lg transition shadow-sm whitespace-nowrap flex items-center justify-center gap-2">
                        <span x-show="!aiSugLoading"><i class="fa-solid fa-wand-magic-sparkles mr-1"></i> Get AI Suggestions</span>
                        <span x-show="aiSugLoading"><i class="fa-solid fa-spinner fa-spin"></i> Generating...</span>
                    </button>
                </div>

                <!-- Cards Grid -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                    <template x-for="item in filteredSuggestions" :key="item.id">
                        <div class="border border-slate-200 rounded-2xl p-4 bg-white hover:shadow-md hover:border-indigo-300 transition-all flex flex-col justify-between group">
                            <div>
                                <div class="flex justify-between items-start gap-2 mb-2">
                                    <div class="flex items-center gap-2.5">
                                        <div class="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center text-lg group-hover:bg-indigo-600 group-hover:text-white transition">
                                            <i :class="'fa-solid ' + (item.icon || 'fa-location-dot')"></i>
                                        </div>
                                        <div>
                                            <h3 class="font-bold text-slate-800 text-base" x-text="item.city"></h3>
                                            <p class="text-xs text-slate-500" x-text="item.country"></p>
                                        </div>
                                    </div>
                                    <span class="text-[11px] font-semibold px-2 py-0.5 rounded-md" :class="item.tag_color || 'bg-indigo-50 text-indigo-700'" x-text="item.tag"></span>
                                </div>

                                <p class="text-xs text-slate-600 line-clamp-2 my-2.5" x-text="item.description"></p>

                                <div class="grid grid-cols-2 gap-2 my-3 bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                                    <div>
                                        <p class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Flight Ticket</p>
                                        <p class="text-xs font-bold text-blue-600 mt-0.5" x-text="formatMoney(item.flight_price)"></p>
                                    </div>
                                    <div>
                                        <p class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Est. Budget</p>
                                        <p class="text-xs font-bold text-emerald-600 mt-0.5" x-text="formatMoney(item.est_budget)"></p>
                                    </div>
                                </div>

                                <div class="space-y-1.5 mb-4">
                                    <p class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Sightseeing Ticket Fees</p>
                                    <div class="space-y-1">
                                        <template x-for="att in item.attractions" :key="att.name">
                                            <div class="flex justify-between items-center text-xs text-slate-600 bg-white px-2 py-1 rounded border border-slate-100">
                                                <span class="truncate pr-2" x-text="att.name"></span>
                                                <span class="font-semibold text-slate-800 shrink-0" x-text="att.ticket === 0 ? 'Free' : formatMoney(att.ticket)"></span>
                                            </div>
                                        </template>
                                    </div>
                                </div>
                            </div>

                            <div class="pt-2 border-t border-slate-100 flex items-center justify-between">
                                <span class="text-[11px] text-slate-400"><i class="fa-regular fa-clock mr-1"></i> <span x-text="item.duration_days + ' Days'"></span></span>
                                <button @click="applySuggestionToForm(item)" class="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition shadow-sm flex items-center gap-1.5">
                                    <i class="fa-solid fa-plus-circle text-xs"></i> Plan This Trip
                                </button>
                            </div>
                        </div>
                    </template>
                </div>
            </div>

            <!-- Create Trip Form & Registered Trips List -->
            <div id="create-trip-section" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <!-- Create Trip Card -->
                <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                    <h2 class="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                        <i class="fa-solid fa-plus-circle text-indigo-600"></i> Create New Trip
                    </h2>
                    <form @submit.prevent="createTrip" class="space-y-4">
                        <div>
                            <label class="block text-xs font-semibold text-slate-600 mb-1">Trip ID</label>
                            <input type="text" x-model="newTrip.trip_id" placeholder="e.g. JAI2026" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-slate-600 mb-1">Trip Name</label>
                            <input type="text" x-model="newTrip.name" placeholder="e.g. Jaipur Royal Tour" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        </div>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="block text-xs font-semibold text-slate-600 mb-1">Start Date</label>
                                <input type="date" x-model="newTrip.start_date" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-slate-600 mb-1">End Date</label>
                                <input type="date" x-model="newTrip.end_date" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                            </div>
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-slate-600 mb-1">Description</label>
                            <textarea x-model="newTrip.description" placeholder="Brief summary..." rows="2" class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"></textarea>
                        </div>
                        <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 rounded-lg text-sm transition shadow-sm flex items-center justify-center gap-2">
                            <i class="fa-solid fa-check"></i> Create Trip
                        </button>
                    </form>
                </div>

                <!-- Active Trips Overview List -->
                <div class="lg:col-span-2 bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col">
                    <h2 class="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                        <i class="fa-solid fa-list-check text-indigo-600"></i> Your Registered Trips
                    </h2>
                    <div class="overflow-y-auto max-h-[420px] space-y-3 pr-1">
                        <template x-for="trip in trips" :key="trip.trip_id">
                            <div class="p-4 border border-slate-100 rounded-xl hover:bg-slate-50 transition flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                                <div>
                                    <div class="flex items-center gap-2">
                                        <span class="text-xs font-bold px-2 py-0.5 bg-indigo-50 text-indigo-700 rounded" x-text="trip.trip_id"></span>
                                        <h3 class="font-semibold text-slate-800" x-text="trip.name"></h3>
                                    </div>
                                    <p class="text-xs text-slate-500 mt-1"><i class="fa-regular fa-calendar"></i> <span x-text="trip.start_date + ' to ' + trip.end_date"></span></p>
                                    <p class="text-xs text-slate-600 mt-1" x-text="trip.description"></p>
                                </div>
                                <div class="flex items-center gap-4 w-full sm:w-auto justify-between sm:justify-end">
                                    <div class="text-right">
                                        <p class="text-xs text-slate-400">Spent / Budget</p>
                                        <p class="text-xs font-semibold text-slate-800">
                                            <span x-text="formatMoney(calculateTripTotal(trip))"></span> / <span x-text="formatMoney(trip.budget)"></span>
                                        </p>
                                    </div>
                                    <button @click="selectedTripId = trip.trip_id; activeTab = 'trips'" class="px-3 py-1.5 bg-slate-100 hover:bg-indigo-600 hover:text-white text-slate-700 rounded-lg text-xs font-medium transition">
                                        Manage <i class="fa-solid fa-arrow-right ml-1"></i>
                                    </button>
                                </div>
                            </div>
                        </template>
                        <div x-show="trips.length === 0" class="text-center py-12 text-slate-400 text-sm">
                            <i class="fa-solid fa-folder-open text-3xl mb-2"></i>
                            <p>No trips registered yet. Click "Plan This Trip" from suggestions above!</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 2: TRIPS & DETAILS MANAGER -->
        <div x-show="activeTab === 'trips'" class="space-y-6">
            <div class="bg-white p-4 rounded-2xl shadow-sm border border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4">
                <div class="flex items-center gap-3 w-full sm:w-auto">
                    <label class="text-xs font-bold text-slate-600 uppercase tracking-wider">Select Trip:</label>
                    <select x-model="selectedTripId" class="px-3 py-2 border border-slate-200 rounded-lg text-sm font-medium bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 w-full sm:w-64">
                        <option value="">-- Choose a Trip --</option>
                        <template x-for="t in trips" :key="t.trip_id">
                            <option :value="t.trip_id" x-text="t.name + ' (' + t.trip_id + ')'"></option>
                        </template>
                    </select>
                </div>
                <div class="text-xs font-medium text-slate-600" x-show="currentTrip">
                    Active Budget: <span class="font-bold text-slate-800" x-text="formatMoney(currentTrip ? currentTrip.budget : 0)"></span> | 
                    Total Spent: <span class="font-bold text-slate-800" x-text="formatMoney(currentTrip ? calculateTripTotal(currentTrip) : 0)"></span>
                </div>
            </div>

            <div x-show="currentTrip" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <!-- 1. Budget -->
                <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-100">
                    <h3 class="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
                        <i class="fa-solid fa-wallet text-indigo-600"></i> Set Trip Budget ($ USD)
                    </h3>
                    <form @submit.prevent="updateBudget" class="space-y-3">
                        <input type="number" step="0.01" x-model="budgetForm.amount" placeholder="Amount in USD ($)" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        <button type="submit" class="w-full bg-slate-800 hover:bg-slate-900 text-white font-medium py-2 rounded-lg text-xs transition">Update Budget</button>
                    </form>
                </div>

                <!-- 2. Destination -->
                <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-100">
                    <h3 class="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
                        <i class="fa-solid fa-map-pin text-indigo-600"></i> Add Destination
                    </h3>
                    <form @submit.prevent="addDestination" class="space-y-3">
                        <input type="text" x-model="destForm.city" placeholder="City" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        <input type="text" x-model="destForm.country" placeholder="Country" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        <input type="text" x-model="destForm.dates" placeholder="Dates (e.g., Oct 10-15)" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 rounded-lg text-xs transition">Add Destination</button>
                    </form>
                </div>

                <!-- 3. Itinerary -->
                <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-100">
                    <h3 class="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
                        <i class="fa-solid fa-calendar-days text-indigo-600"></i> Add Itinerary Day
                    </h3>
                    <form @submit.prevent="addItinerary" class="space-y-3">
                        <div class="grid grid-cols-2 gap-2">
                            <input type="number" x-model="itinForm.day_num" placeholder="Day #" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                            <input type="date" x-model="itinForm.date_str" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        </div>
                        <input type="text" x-model="itinForm.details" placeholder="Activities details..." required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 rounded-lg text-xs transition">Add Day Plan</button>
                    </form>
                </div>

                <!-- 4. Transportation -->
                <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-100">
                    <h3 class="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
                        <i class="fa-solid fa-plane text-indigo-600"></i> Log Transportation & Ticket
                    </h3>
                    <form @submit.prevent="addTransportation" class="space-y-3">
                        <select x-model="transForm.type" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                            <option value="Flight">Flight Ticket</option>
                            <option value="Train">Train Ticket</option>
                            <option value="Car Rental">Car Rental</option>
                            <option value="Bus / Ferry">Bus / Ferry Ticket</option>
                        </select>
                        <input type="text" x-model="transForm.details" placeholder="Route (e.g. DEL to JAI Express)" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        <input type="number" step="0.01" x-model="transForm.cost" placeholder="Cost ($ USD)" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 rounded-lg text-xs transition">Log Ticket</button>
                    </form>
                </div>

                <!-- 5. Accommodation -->
                <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-100">
                    <h3 class="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
                        <i class="fa-solid fa-hotel text-indigo-600"></i> Add Accommodation
                    </h3>
                    <form @submit.prevent="addAccommodation" class="space-y-3">
                        <input type="text" x-model="accomForm.name" placeholder="Hotel / Resort Name" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        <div class="grid grid-cols-2 gap-2">
                            <input type="date" x-model="accomForm.check_in" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                            <input type="date" x-model="accomForm.check_out" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        </div>
                        <input type="number" step="0.01" x-model="accomForm.cost" placeholder="Total Cost ($ USD)" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 rounded-lg text-xs transition">Log Stay</button>
                    </form>
                </div>

                <!-- 6. Activities & Expenses -->
                <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 flex flex-col justify-between">
                    <div>
                        <h3 class="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
                            <i class="fa-solid fa-ticket text-indigo-600"></i> Activity Pass or Expense
                        </h3>
                        <div class="flex border-b border-slate-100 mb-3 text-xs">
                            <button type="button" @click="expTab = 'activity'" :class="expTab === 'activity' ? 'border-b-2 border-indigo-600 font-bold text-indigo-600' : 'text-slate-500'" class="pb-1 mr-4">Attraction Pass</button>
                            <button type="button" @click="expTab = 'expense'" :class="expTab === 'expense' ? 'border-b-2 border-indigo-600 font-bold text-indigo-600' : 'text-slate-500'" class="pb-1">General Expense</button>
                        </div>
                    </div>

                    <form x-show="expTab === 'activity'" @submit.prevent="addActivity" class="space-y-3">
                        <input type="text" x-model="actForm.name" placeholder="Pass / Activity (e.g. Amer Fort Pass)" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        <div class="grid grid-cols-2 gap-2">
                            <input type="date" x-model="actForm.date_str" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                            <input type="number" step="0.01" x-model="actForm.cost" placeholder="Cost ($ USD)" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        </div>
                        <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 rounded-lg text-xs transition">Record Activity</button>
                    </form>

                    <form x-show="expTab === 'expense'" @submit.prevent="addExpense" class="space-y-3">
                        <select x-model="genExpForm.category" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                            <option value="Food & Dining">Food & Dining</option>
                            <option value="Shopping">Shopping</option>
                            <option value="Emergency">Emergency</option>
                            <option value="Miscellaneous">Miscellaneous</option>
                        </select>
                        <div class="grid grid-cols-2 gap-2">
                            <input type="date" x-model="genExpForm.date" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                            <input type="number" step="0.01" x-model="genExpForm.amount" placeholder="Amount ($ USD)" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        </div>
                        <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 rounded-lg text-xs transition">Record Expense</button>
                    </form>
                </div>
            </div>

            <div x-show="!currentTrip" class="bg-white p-12 rounded-2xl shadow-sm border border-slate-100 text-center text-slate-400">
                <i class="fa-solid fa-hand-pointer text-4xl mb-3"></i>
                <p class="text-base font-medium">Please select a trip above to view and manage its details.</p>
            </div>
        </div>

        <!-- TAB 3: REPORTS & AI ASSISTANT -->
        <div x-show="activeTab === 'reports'" class="space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Trip Report Viewer -->
                <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                    <h2 class="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                        <i class="fa-solid fa-file-invoice text-indigo-600"></i> Trip-wise Expense Report
                    </h2>
                    <div class="mb-4">
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Select Trip</label>
                        <select x-model="reportTripId" class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                            <option value="">-- Choose Trip --</option>
                            <template x-for="t in trips" :key="t.trip_id">
                                <option :value="t.trip_id" x-text="t.name"></option>
                            </template>
                        </select>
                    </div>
                    <template x-if="reportTrip">
                        <div class="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-3 text-sm">
                            <div class="flex justify-between font-bold text-slate-800 text-base border-b pb-2">
                                <span x-text="reportTrip.name"></span>
                                <span x-text="formatMoney(calculateTripTotal(reportTrip))"></span>
                            </div>
                            <div class="grid grid-cols-2 gap-2 mt-3 text-xs text-slate-600">
                                <p>Budget: <span class="font-bold text-slate-800" x-text="formatMoney(reportTrip.budget)"></span></p>
                                <p>Remaining: <span class="font-bold text-slate-800" x-text="formatMoney(reportTrip.budget - calculateTripTotal(reportTrip))"></span></p>
                            </div>
                        </div>
                    </template>
                </div>

                <!-- AI Query Box -->
                <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                    <h2 class="text-lg font-bold text-slate-800 mb-2 flex items-center gap-2">
                        <i class="fa-solid fa-wand-magic-sparkles text-indigo-600"></i> AI Travel & Expense Assistant
                    </h2>
                    <p class="text-xs text-slate-500 mb-4">Ask natural language questions about your travel budget, conversions, or Indian destinations.</p>
                    <div class="space-y-4">
                        <div class="flex gap-2">
                            <input type="text" x-model="aiQueryText" @keydown.enter="askAI" placeholder="e.g. Can I afford a ₹10,000 hotel in Jaipur with my remaining budget?" class="flex-grow px-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                            <button @click="askAI" :disabled="aiLoading" class="bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-400 text-white px-6 py-2.5 rounded-xl text-sm font-medium transition shadow-sm flex items-center gap-2">
                                <span x-show="!aiLoading">Ask AI</span>
                                <span x-show="aiLoading"><i class="fa-solid fa-spinner fa-spin"></i> Thinking...</span>
                            </button>
                        </div>
                        <div class="bg-indigo-50/50 p-4 rounded-xl border border-indigo-100 min-h-[80px]" x-show="aiResponse">
                            <p class="text-xs font-bold text-indigo-900 mb-1"><i class="fa-solid fa-robot mr-1"></i> AI Assistant Reply:</p>
                            <p class="text-sm text-indigo-950 whitespace-pre-line" x-text="aiResponse"></p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

    </main>

    <!-- Footer -->
    <footer class="bg-white border-t border-slate-100 py-4 mt-auto">
        <div class="max-w-7xl mx-auto px-4 text-center text-xs text-slate-400">
            Globetrotter Travel Dashboard &bull; Live Ticket Benchmarks &bull; 1 USD ≈ 83.5 INR
        </div>
    </footer>

    <script>
        const GEMINI_API_KEY = "{API_KEY}";
        const INITIAL_SUGGESTIONS = {SUGGESTIONS_JSON};

        function travelApp() {{
            return {{
                activeTab: 'dashboard',
                currencyMode: 'both',
                usdToInrRate: 83.5,
                trips: [],
                selectedTripId: '',
                reportTripId: '',
                aiQueryText: '',
                aiResponse: '',
                aiLoading: false,
                aiSugLoading: false,
                aiTipLoading: false,
                aiPromptSuggest: '',
                aiDashboardMessage: "✨ Pro Tip: Traveling to Jaipur or Varanasi? Train passes and local guided tours save up to 40% ($50 / ₹4,100) compared to last-minute flights.",
                sugFilter: 'All',
                suggestions: INITIAL_SUGGESTIONS,
                expTab: 'activity',
                toast: {{ show: false, message: '', success: true }},

                newTrip: {{ trip_id: '', name: '', start_date: '', end_date: '', description: '' }},
                budgetForm: {{ amount: '' }},
                destForm: {{ city: '', country: 'India', dates: '' }},
                itinForm: {{ day_num: '', date_str: '', details: '' }},
                transForm: {{ type: 'Flight', details: '', cost: '' }},
                accomForm: {{ name: '', check_in: '', check_out: '', cost: '' }},
                actForm: {{ name: '', date_str: '', cost: '' }},
                genExpForm: {{ category: 'Food & Dining', date: '', amount: '' }},

                get currentTrip() {{
                    return this.trips.find(t => t.trip_id === this.selectedTripId) || null;
                }},
                get reportTrip() {{
                    return this.trips.find(t => t.trip_id === this.reportTripId) || null;
                }},
                get totalBudget() {{
                    return this.trips.reduce((acc, t) => acc + (parseFloat(t.budget) || 0), 0);
                }},
                get totalSpent() {{
                    return this.trips.reduce((acc, t) => acc + this.calculateTripTotal(t), 0);
                }},
                get overallUtilization() {{
                    if (this.totalBudget === 0) return 0;
                    return ((this.totalSpent / this.totalBudget) * 100).toFixed(1);
                }},
                get filteredSuggestions() {{
                    if (this.sugFilter === 'All') return this.suggestions;
                    if (this.sugFilter === 'Under $1,000') return this.suggestions.filter(s => s.est_budget <= 360);
                    return this.suggestions.filter(s => s.category === this.sugFilter);
                }},

                formatMoney(amount) {{
                    let usd = parseFloat(amount) || 0;
                    let inr = Math.round(usd * this.usdToInrRate);
                    let usdFmt = '$' + usd.toLocaleString('en-US', {{ minimumFractionDigits: 0, maximumFractionDigits: 2 }});
                    let inrFmt = '₹' + inr.toLocaleString('en-IN');
                    if (this.currencyMode === 'both') return `${{usdFmt}} / ${{inrFmt}}`;
                    if (this.currencyMode === 'INR') return inrFmt;
                    return usdFmt;
                }},

                calculateTripTotal(t) {{
                    if (!t) return 0;
                    let tc = (t.transportation || []).reduce((a, b) => a + (parseFloat(b.cost) || 0), 0);
                    let ac = (t.accommodations || []).reduce((a, b) => a + (parseFloat(b.cost) || 0), 0);
                    let act = (t.activities || []).reduce((a, b) => a + (parseFloat(b.cost) || 0), 0);
                    let mc = (t.expenses || []).reduce((a, b) => a + (parseFloat(b.amount) || 0), 0);
                    return tc + ac + act + mc;
                }},

                showToast(message, success = true) {{
                    this.toast.message = message;
                    this.toast.success = success;
                    this.toast.show = true;
                    setTimeout(() => {{ this.toast.show = false; }}, 3500);
                }},

                init() {{
                    const saved = localStorage.getItem('globetrotter_trips');
                    if (saved) {{
                        try {{ this.trips = JSON.parse(saved); }} catch(e) {{}}
                    }}
                }},

                saveTrips() {{
                    localStorage.setItem('globetrotter_trips', JSON.stringify(this.trips));
                }},

                createTrip() {{
                    if (this.trips.find(t => t.trip_id === this.newTrip.trip_id)) {{
                        this.showToast('Trip ID already exists!', false);
                        return;
                    }}
                    const tripObj = {{
                        ...this.newTrip,
                        budget: 0,
                        destinations: [],
                        itinerary: [],
                        transportation: [],
                        accommodations: [],
                        activities: [],
                        expenses: []
                    }};
                    this.trips.push(tripObj);
                    this.saveTrips();
                    this.showToast(`Trip '${{this.newTrip.name}}' created!`);
                    this.newTrip = {{ trip_id: '', name: '', start_date: '', end_date: '', description: '' }};
                }},

                applySuggestionToForm(item) {{
                    const today = new Date();
                    const start = new Date(today.getTime() + 14 * 86400000).toISOString().split('T')[0];
                    const end = new Date(today.getTime() + (14 + item.duration_days) * 86400000).toISOString().split('T')[0];
                    const tid = (item.city.substring(0, 3) + Math.floor(100 + Math.random() * 900)).toUpperCase();

                    const newT = {{
                        trip_id: tid,
                        name: `${{item.city}} Tour`,
                        start_date: start,
                        end_date: end,
                        description: item.description,
                        budget: item.est_budget,
                        destinations: [{{ city: item.city, country: item.country, dates: 'Full Trip' }}],
                        itinerary: [],
                        transportation: [{{ type: 'Flight', details: `Travel to ${{item.city}}`, cost: item.flight_price }}],
                        accommodations: [],
                        activities: [],
                        expenses: []
                    }};
                    this.trips.push(newT);
                    this.saveTrips();
                    this.selectedTripId = tid;
                    this.showToast(`'${{item.city}} Tour' added to your trips!`);
                }},

                updateBudget() {{
                    if (!this.currentTrip) return;
                    this.currentTrip.budget = parseFloat(this.budgetForm.amount) || 0;
                    this.saveTrips();
                    this.showToast('Budget updated!');
                    this.budgetForm.amount = '';
                }},
                addDestination() {{
                    if (!this.currentTrip) return;
                    this.currentTrip.destinations.push({{ ...this.destForm }});
                    this.saveTrips();
                    this.showToast('Destination added!');
                    this.destForm = {{ city: '', country: 'India', dates: '' }};
                }},
                addItinerary() {{
                    if (!this.currentTrip) return;
                    this.currentTrip.itinerary.push({{ ...this.itinForm }});
                    this.saveTrips();
                    this.showToast('Day plan added!');
                    this.itinForm = {{ day_num: '', date_str: '', details: '' }};
                }},
                addTransportation() {{
                    if (!this.currentTrip) return;
                    this.currentTrip.transportation.push({{ ...this.transForm, cost: parseFloat(this.transForm.cost) || 0 }});
                    this.saveTrips();
                    this.showToast('Transport ticket logged!');
                    this.transForm = {{ type: 'Flight', details: '', cost: '' }};
                }},
                addAccommodation() {{
                    if (!this.currentTrip) return;
                    this.currentTrip.accommodations.push({{ ...this.accomForm, cost: parseFloat(this.accomForm.cost) || 0 }});
                    this.saveTrips();
                    this.showToast('Accommodation logged!');
                    this.accomForm = {{ name: '', check_in: '', check_out: '', cost: '' }};
                }},
                addActivity() {{
                    if (!this.currentTrip) return;
                    this.currentTrip.activities.push({{ ...this.actForm, cost: parseFloat(this.actForm.cost) || 0 }});
                    this.saveTrips();
                    this.showToast('Activity pass recorded!');
                    this.actForm = {{ name: '', date_str: '', cost: '' }};
                }},
                addExpense() {{
                    if (!this.currentTrip) return;
                    this.currentTrip.expenses.push({{ ...this.genExpForm, amount: parseFloat(this.genExpForm.amount) || 0 }});
                    this.saveTrips();
                    this.showToast('Expense recorded!');
                    this.genExpForm = {{ category: 'Food & Dining', date: '', amount: '' }};
                }},

                async callGemini(promptText) {{
                    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${{GEMINI_API_KEY}}`;
                    const res = await fetch(url, {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ contents: [{{ parts: [{{ text: promptText }}] }}] }})
                    }});
                    const data = await res.json();
                    if (data.candidates && data.candidates[0].content.parts[0].text) {{
                        return data.candidates[0].content.parts[0].text;
                    }}
                    throw new Error(data.error ? data.error.message : 'AI error');
                }},

                async generateDailyTip() {{
                    this.aiTipLoading = true;
                    try {{
                        const reply = await this.callGemini("Give a short 2-sentence travel advice tip for Indian destinations with ticket price benchmarks in USD ($) and INR (₹).");
                        this.aiDashboardMessage = reply.trim();
                    }} catch(e) {{
                        this.aiDashboardMessage = "💡 Pro Tip: Book Rajasthan and Kerala train passes 3 weeks in advance to save up to 40% on travel!";
                    }} finally {{
                        this.aiTipLoading = false;
                    }}
                }},

                async askAI() {{
                    if (!this.aiQueryText.trim() || this.aiLoading) return;
                    this.aiLoading = true;
                    this.aiResponse = '';
                    try {{
                        const context = JSON.stringify(this.trips);
                        const prompt = `You are a travel advisor. Context: ${{context}}. Answer the question in dual currency (USD $ and INR ₹ with 1 USD = 83.5 INR): ${{this.aiQueryText}}`;
                        this.aiResponse = await this.callGemini(prompt);
                    }} catch(e) {{
                        this.aiResponse = "AI is currently unavailable. Please verify the Gemini API key.";
                    }} finally {{
                        this.aiLoading = false;
                    }}
                }},

                async generateCustomAISuggestions() {{
                    if (!this.aiPromptSuggest.trim() || this.aiSugLoading) return;
                    this.aiSugLoading = true;
                    try {{
                        const reply = await this.callGemini(`Recommend 1 destination for '${{this.aiPromptSuggest}}' with estimated flight ticket and budget in both $ and ₹.`);
                        this.aiDashboardMessage = reply.trim();
                        this.showToast('AI recommendation generated!');
                    }} catch(e) {{
                        this.showToast('AI suggestion failed.', false);
                    }} finally {{
                        this.aiSugLoading = false;
                    }}
                }}
            }}
        }}
    </script>
</body>
</html>
"""

# Render the exact Tailwind dashboard directly into Streamlit Cloud
components.html(HTML_CODE, height=1350, scrolling=True)
