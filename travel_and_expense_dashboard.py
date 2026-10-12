from flask import Flask, render_template_string, request, jsonify
import datetime

app = Flask(__name__)

# --- In-Memory Data Store ---
trips_db = {}

class Trip:
    def __init__(self, trip_id, name, start_date, end_date, description):
        self.trip_id = trip_id
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.description = description
        self.budget = 0.0
        self.destinations = []
        self.itinerary = []
        self.transportation = []
        self.accommodations = []
        self.activities = []
        self.expenses = []

    def to_dict(self):
        total_spent = self.calculate_total_expenses()
        pct = (total_spent / self.budget * 100) if self.budget > 0 else 0
        return {
            "trip_id": self.trip_id,
            "name": self.name,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "description": self.description,
            "budget": self.budget,
            "destinations": self.destinations,
            "itinerary": self.itinerary,
            "transportation": self.transportation,
            "accommodations": self.accommodations,
            "activities": self.activities,
            "expenses": self.expenses,
            "total_spent": total_spent,
            "budget_utilization": round(pct, 1),
            "remaining_budget": self.budget - total_spent
        }

    def calculate_total_expenses(self):
        transport_total = sum(t['cost'] for t in self.transportation)
        accom_total = sum(a['cost'] for a in self.accommodations)
        activity_total = sum(act['cost'] for act in self.activities)
        misc_total = sum(e['amount'] for e in self.expenses)
        return transport_total + accom_total + activity_total + misc_total


# --- HTML Frontend Template ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Travel & Expense Management Dashboard</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Alpine.js -->
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class="bg-slate-50 text-slate-800 min-h-screen flex flex-col" x-data="travelApp()">

    <!-- Header Navigation -->
    <header class="bg-indigo-600 text-white shadow-md">
        <div class="max-w-7xl mx-auto px-4 py-4 flex flex-col md:flex-row justify-between items-center gap-4">
            <div class="flex items-center space-x-3">
                <div class="bg-white/10 p-2.5 rounded-xl backdrop-blur-sm">
                    <i class="fa-solid fa-earth-americas text-2xl text-indigo-100"></i>
                </div>
                <div>
                    <h1 class="text-xl font-bold tracking-tight">Globetrotter Dashboard</h1>
                    <p class="text-xs text-indigo-200">Trip Planning & Expense Intelligence</p>
                </div>
            </div>
            <nav class="flex flex-wrap gap-2">
                <button @click="activeTab = 'dashboard'" :class="activeTab === 'dashboard' ? 'bg-indigo-700 shadow-inner' : 'hover:bg-indigo-500'" class="px-4 py-2 rounded-lg text-sm font-medium transition flex items-center gap-2">
                    <i class="fa-solid fa-chart-pie"></i> Dashboard
                </button>
                <button @click="activeTab = 'trips'" :class="activeTab === 'trips' ? 'bg-indigo-700 shadow-inner' : 'hover:bg-indigo-500'" class="px-4 py-2 rounded-lg text-sm font-medium transition flex items-center gap-2">
                    <i class="fa-solid fa-suitcase-rolling"></i> Trips & Details
                </button>
                <button @click="activeTab = 'reports'" :class="activeTab === 'reports' ? 'bg-indigo-700 shadow-inner' : 'hover:bg-indigo-500'" class="px-4 py-2 rounded-lg text-sm font-medium transition flex items-center gap-2">
                    <i class="fa-solid fa-file-invoice-dollar"></i> Reports & AI
                </button>
            </nav>
        </div>
    </header>

    <!-- Main Content Area -->
    <main class="flex-grow max-w-7xl w-full mx-auto px-4 py-6">

        <!-- Toast Notifications -->
        <div x-show="toast.show" x-transition class="fixed bottom-5 right-5 z-50 px-4 py-3 rounded-xl shadow-lg text-white text-sm font-medium flex items-center gap-2" :class="toast.success ? 'bg-emerald-600' : 'bg-rose-600'">
            <i :class="toast.success ? 'fa-solid fa-circle-check' : 'fa-solid fa-circle-exclamation'"></i>
            <span x-text="toast.message"></span>
        </div>

        <!-- TAB 1: DASHBOARD OVERVIEW -->
        <div x-show="activeTab === 'dashboard'" class="space-y-6">
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
                        <h3 class="text-2xl font-bold text-slate-800 mt-1" x-text="'$' + totalBudget.toFixed(2)">$0.00</h3>
                    </div>
                    <div class="w-12 h-12 bg-emerald-50 text-emerald-600 rounded-xl flex items-center justify-center text-xl">
                        <i class="fa-solid fa-wallet"></i>
                    </div>
                </div>
                <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 flex items-center justify-between">
                    <div>
                        <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Expenses</p>
                        <h3 class="text-2xl font-bold text-slate-800 mt-1" x-text="'$' + totalSpent.toFixed(2)">$0.00</h3>
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

            <!-- Create Trip Quick Form & Summary Cards -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <!-- Quick Create Card -->
                <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                    <h2 class="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                        <i class="fa-solid fa-plus-circle text-indigo-600"></i> Create New Trip
                    </h2>
                    <form @submit.prevent="createTrip" class="space-y-4">
                        <div>
                            <label class="block text-xs font-semibold text-slate-600 mb-1">Trip ID</label>
                            <input type="text" x-model="newTrip.trip_id" placeholder="e.g. NYC2026" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-slate-600 mb-1">Trip Name</label>
                            <input type="text" x-model="newTrip.name" placeholder="e.g. New York Getaway" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
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
                        <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 rounded-lg text-sm transition shadow-sm">
                            Create Trip
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
                            <div class="p-4 border border-slate-100 rounded-xl hover:bg-slate-50/80 transition flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
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
                                        <p class="text-sm font-semibold text-slate-800"><span x-text="'$' + trip.total_spent.toFixed(2)"></span> / <span x-text="'$' + trip.budget.toFixed(2)"></span></p>
                                        <div class="w-24 bg-slate-100 h-2 rounded-full overflow-hidden mt-1">
                                            <div class="h-full rounded-full" :class="trip.budget_utilization > 100 ? 'bg-rose-500' : 'bg-emerald-500'" :style="'width: ' + Math.min(trip.budget_utilization, 100) + '%'"></div>
                                        </div>
                                    </div>
                                    <button @click="selectedTripId = trip.trip_id; activeTab = 'trips'" class="px-3 py-1.5 bg-slate-100 hover:bg-indigo-600 hover:text-white text-slate-700 rounded-lg text-xs font-medium transition">
                                        Manage <i class="fa-solid fa-arrow-right ml-1"></i>
                                    </button>
                                </div>
                            </div>
                        </template>
                        <div x-show="trips.length === 0" class="text-center py-12 text-slate-400 text-sm">
                            <i class="fa-solid fa-folder-open text-3xl mb-2"></i>
                            <p>No trips created yet. Use the form to add your first trip!</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 2: TRIPS & DETAILS MANAGER -->
        <div x-show="activeTab === 'trips'" class="space-y-6">
            <!-- Trip Selector Bar -->
            <div class="bg-white p-4 rounded-2xl shadow-sm border border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4">
                <div class="flex items-center gap-3 w-full sm:w-auto">
                    <label class="text-xs font-bold text-slate-600 uppercase tracking-wider">Select Trip:</label>
                    <select x-model="selectedTripId" @change="fetchTripDetails()" class="px-3 py-2 border border-slate-200 rounded-lg text-sm font-medium bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 w-full sm:w-64">
                        <option value="">-- Choose a Trip --</option>
                        <template x-for="t in trips" :key="t.trip_id">
                            <option :value="t.trip_id" x-text="t.name + ' (' + t.trip_id + ')'"></option>
                        </template>
                    </select>
                </div>
                <div class="text-sm font-medium text-slate-600" x-show="currentTrip">
                    Active Budget: <span class="font-bold text-slate-800" x-text="'$' + currentTrip.budget.toFixed(2)"></span> | 
                    Total Spent: <span class="font-bold text-slate-800" x-text="'$' + currentTrip.total_spent.toFixed(2)"></span>
                </div>
            </div>

            <!-- If Trip Selected -->
            <div x-show="currentTrip" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

                <!-- 1. Budget Setting -->
                <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-100">
                    <h3 class="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
                        <i class="fa-solid fa-wallet text-indigo-600"></i> Set Trip Budget
                    </h3>
                    <form @submit.prevent="addBudget" class="space-y-3">
                        <input type="number" step="0.01" x-model="budgetForm.amount" placeholder="Amount ($)" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        <button type="submit" class="w-full bg-slate-800 hover:bg-slate-900 text-white font-medium py-2 rounded-lg text-xs transition">Update Budget</button>
                    </form>
                </div>

                <!-- 2. Add Destination -->
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

                <!-- 3. Create Itinerary -->
                <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-100">
                    <h3 class="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
                        <i class="fa-solid fa-calendar-days text-indigo-600"></i> Add Itinerary
                    </h3>
                    <form @submit.prevent="addItinerary" class="space-y-3">
                        <div class="grid grid-cols-2 gap-2">
                            <input type="number" x-model="itinForm.day_num" placeholder="Day # (e.g. 1)" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                            <input type="date" x-model="itinForm.date_str" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        </div>
                        <input type="text" x-model="itinForm.details" placeholder="Activities details..." required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 rounded-lg text-xs transition">Add Itinerary Day</button>
                    </form>
                </div>

                <!-- 4. Transportation Details -->
                <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-100">
                    <h3 class="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
                        <i class="fa-solid fa-plane text-indigo-600"></i> Add Transportation
                    </h3>
                    <form @submit.prevent="addTransportation" class="space-y-3">
                        <select x-model="transForm.type" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                            <option value="Flight">Flight</option>
                            <option value="Train">Train</option>
                            <option value="Car Rental">Car Rental</option>
                            <option value="Bus / Taxi">Bus / Taxi</option>
                        </select>
                        <input type="text" x-model="transForm.details" placeholder="Details (e.g. JFK to LHR)" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        <input type="number" step="0.01" x-model="transForm.cost" placeholder="Cost ($)" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 rounded-lg text-xs transition">Log Transport</button>
                    </form>
                </div>

                <!-- 5. Accommodation Details -->
                <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-100">
                    <h3 class="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
                        <i class="fa-solid fa-hotel text-indigo-600"></i> Add Accommodation
                    </h3>
                    <form @submit.prevent="addAccommodation" class="space-y-3">
                        <input type="text" x-model="accomForm.name" placeholder="Hotel / Property Name" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        <div class="grid grid-cols-2 gap-2">
                            <input type="date" x-model="accomForm.check_in" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                            <input type="date" x-model="accomForm.check_out" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        </div>
                        <input type="number" step="0.01" x-model="accomForm.cost" placeholder="Total Cost ($)" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 rounded-lg text-xs transition">Log Accommodation</button>
                    </form>
                </div>

                <!-- 6. Activities & Expenses -->
                <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 flex flex-col justify-between">
                    <div>
                        <h3 class="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
                            <i class="fa-solid fa-ticket text-indigo-600"></i> Record Activity / Expense
                        </h3>
                        <!-- Tabs inside card -->
                        <div class="flex border-b border-slate-100 mb-3 text-xs">
                            <button type="button" @click="expTab = 'activity'" :class="expTab === 'activity' ? 'border-b-2 border-indigo-600 font-bold text-indigo-600' : 'text-slate-500'" class="pb-1 mr-4">Activity</button>
                            <button type="button" @click="expTab = 'expense'" :class="expTab === 'expense' ? 'border-b-2 border-indigo-600 font-bold text-indigo-600' : 'text-slate-500'" class="pb-1">General Expense</button>
                        </div>
                    </div>

                    <!-- Activity Form -->
                    <form x-show="expTab === 'activity'" @submit.prevent="addActivity" class="space-y-3">
                        <input type="text" x-model="actForm.name" placeholder="Activity Name (e.g. Museum Tour)" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        <div class="grid grid-cols-2 gap-2">
                            <input type="date" x-model="actForm.date_str" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                            <input type="number" step="0.01" x-model="actForm.cost" placeholder="Cost ($)" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        </div>
                        <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 rounded-lg text-xs transition">Record Activity</button>
                    </form>

                    <!-- General Expense Form -->
                    <form x-show="expTab === 'expense'" @submit.prevent="addExpense" class="space-y-3">
                        <select x-model="genExpForm.category" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                            <option value="Food & Dining">Food & Dining</option>
                            <option value="Shopping">Shopping</option>
                            <option value="Emergency">Emergency</option>
                            <option value="Miscellaneous">Miscellaneous</option>
                        </select>
                        <div class="grid grid-cols-2 gap-2">
                            <input type="date" x-model="genExpForm.date" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                            <input type="number" step="0.01" x-model="genExpForm.amount" placeholder="Amount ($)" required class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        </div>
                        <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 rounded-lg text-xs transition">Record Expense</button>
                    </form>
                </div>

            </div>

            <!-- Empty State for Trip Details -->
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
                    <template x-if="reportTripId">
                        <div class="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-3 text-sm">
                            <template x-let="rpt = trips.find(t => t.trip_id === reportTripId)">
                                <div>
                                    <div class="flex justify-between font-bold text-slate-800 text-base border-b pb-2">
                                        <span x-text="rpt.name"></span>
                                        <span x-text="'$' + rpt.total_spent.toFixed(2)"></span>
                                    </div>
                                    <div class="grid grid-cols-2 gap-2 mt-3 text-xs text-slate-600">
                                        <p>Budget: <span class="font-bold text-slate-800" x-text="'$' + rpt.budget.toFixed(2)"></span></p>
                                        <p>Remaining: <span class="font-bold text-slate-800" x-text="'$' + rpt.remaining_budget.toFixed(2)"></span></p>
                                        <p>Utilization: <span class="font-bold" :class="rpt.budget_utilization > 100 ? 'text-rose-600' : 'text-emerald-600'" x-text="rpt.budget_utilization + '%'"></span></p>
                                    </div>
                                    <div class="mt-4 space-y-2">
                                        <p class="text-xs font-bold text-slate-700 uppercase tracking-wider">Breakdown</p>
                                        <div class="flex justify-between text-xs bg-white p-2 rounded border">
                                            <span>Transportation:</span>
                                            <span class="font-semibold" x-text="'$' + rpt.transportation.reduce((a,b)=>a+b.cost, 0).toFixed(2)"></span>
                                        </div>
                                        <div class="flex justify-between text-xs bg-white p-2 rounded border">
                                            <span>Accommodation:</span>
                                            <span class="font-semibold" x-text="'$' + rpt.accommodations.reduce((a,b)=>a+b.cost, 0).toFixed(2)"></span>
                                        </div>
                                        <div class="flex justify-between text-xs bg-white p-2 rounded border">
                                            <span>Activities:</span>
                                            <span class="font-semibold" x-text="'$' + rpt.activities.reduce((a,b)=>a+b.cost, 0).toFixed(2)"></span>
                                        </div>
                                        <div class="flex justify-between text-xs bg-white p-2 rounded border">
                                            <span>Miscellaneous:</span>
                                            <span class="font-semibold" x-text="'$' + rpt.expenses.reduce((a,b)=>a+b.amount, 0).toFixed(2)"></span>
                                        </div>
                                    </div>
                                </div>
                            </template>
                        </div>
                    </template>
                </div>

                <!-- Monthly Travel Reports -->
                <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                    <h2 class="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                        <i class="fa-solid fa-calendar-alt text-indigo-600"></i> Monthly Travel Reports
                    </h2>
                    <div class="mb-4">
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Select Year-Month</label>
                        <div class="flex gap-2">
                            <input type="month" x-model="monthlyReportYM" class="flex-grow px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                            <button @click="fetchMonthlyReport" class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-xs font-medium transition">Generate</button>
                        </div>
                    </div>
                    <div class="bg-slate-50 p-4 rounded-xl border border-slate-200 min-h-[160px] flex flex-col justify-center">
                        <template x-if="monthlyReportData">
                            <div class="space-y-2 text-sm">
                                <p class="font-bold text-slate-800">Report for <span x-text="monthlyReportData.year_month"></span></p>
                                <p class="text-xs text-slate-600">Active Trips: <span class="font-bold text-slate-800" x-text="monthlyReportData.trips_count"></span></p>
                                <p class="text-xs text-slate-600">Total Expenditure: <span class="font-bold text-emerald-600 text-base" x-text="'$' + monthlyReportData.total_spent.toFixed(2)"></span></p>
                            </div>
                        </template>
                        <template x-if="!monthlyReportData">
                            <p class="text-xs text-slate-400 text-center">Select month and click generate to view aggregated monthly statistics.</p>
                        </template>
                    </div>
                </div>
            </div>

            <!-- AI Travel / Expense Query Assistant -->
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <h2 class="text-lg font-bold text-slate-800 mb-2 flex items-center gap-2">
                    <i class="fa-solid fa-wand-magic-sparkles text-indigo-600"></i> AI Travel & Expense Assistant
                </h2>
                <p class="text-xs text-slate-500 mb-4">Ask natural language questions regarding your trips, spending totals, budgets, or destinations.</p>
                <div class="space-y-4">
                    <div class="flex gap-2">
                        <input type="text" x-model="aiQueryText" @keydown.enter="askAI" placeholder="e.g. What is my total spent? or Show budget status" class="flex-grow px-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        <button @click="askAI" class="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-xl text-sm font-medium transition shadow-sm">Ask AI</button>
                    </div>
                    <div class="bg-indigo-50/50 p-4 rounded-xl border border-indigo-100 min-h-[80px]" x-show="aiResponse">
                        <p class="text-xs font-bold text-indigo-900 mb-1"><i class="fa-solid fa-robot mr-1"></i> AI Assistant Reply:</p>
                        <p class="text-sm text-indigo-950 whitespace-pre-line" x-text="aiResponse"></p>
                    </div>
                </div>
            </div>
        </div>

    </main>

    <!-- Footer -->
    <footer class="bg-white border-t border-slate-100 py-4 mt-auto">
        <div class="max-w-7xl mx-auto px-4 text-center text-xs text-slate-400">
            Travel Planning & Expense Management Dashboard &bull; Powered by Python Flask & Tailwind CSS
        </div>
    </footer>

    <!-- JavaScript Application Logic -->
    <script>
        function travelApp() {
            return {
                activeTab: 'dashboard',
                trips: [],
                selectedTripId: '',
                currentTrip: null,
                reportTripId: '',
                monthlyReportYM: '',
                monthlyReportData: null,
                aiQueryText: '',
                aiResponse: '',
                expTab: 'activity',
                toast: { show: false, message: '', success: true },

                newTrip: { trip_id: '', name: '', start_date: '', end_date: '', description: '' },
                budgetForm: { amount: '' },
                destForm: { city: '', country: '', dates: '' },
                itinForm: { day_num: '', date_str: '', details: '' },
                transForm: { type: 'Flight', details: '', cost: '' },
                accomForm: { name: '', check_in: '', check_out: '', cost: '' },
                actForm: { name: '', date_str: '', cost: '' },
                genExpForm: { category: 'Food & Dining', date: '', amount: '' },

                get totalBudget() {
                    return this.trips.reduce((acc, t) => acc + t.budget, 0);
                },
                get totalSpent() {
                    return this.trips.reduce((acc, t) => acc + t.total_spent, 0);
                },
                get overallUtilization() {
                    if (this.totalBudget === 0) return 0;
                    return ((this.totalSpent / this.totalBudget) * 100).toFixed(1);
                },

                showToast(message, success = true) {
                    this.toast.message = message;
                    this.toast.success = success;
                    this.toast.show = true;
                    setTimeout(() => { this.toast.show = false; }, 3000);
                },

                async init() {
                    await this.fetchTrips();
                },

                async fetchTrips() {
                    try {
                        let res = await fetch('/api/trips');
                        let data = await res.json();
                        this.trips = data.trips;
                        if (this.selectedTripId) {
                            this.currentTrip = this.trips.find(t => t.trip_id === this.selectedTripId) || null;
                        }
                    } catch (e) {
                        this.showToast('Failed to fetch trips', false);
                    }
                },

                async fetchTripDetails() {
                    if (!this.selectedTripId) {
                        this.currentTrip = null;
                        return;
                    }
                    await this.fetchTrips();
                    this.currentTrip = this.trips.find(t => t.trip_id === this.selectedTripId) || null;
                },

                async createTrip() {
                    try {
                        let res = await fetch('/api/trips', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(this.newTrip)
                        });
                        let data = await res.json();
                        if (res.ok) {
                            this.showToast(data.message);
                            this.newTrip = { trip_id: '', name: '', start_date: '', end_date: '', description: '' };
                            await this.fetchTrips();
                        } else {
                            this.showToast(data.error, false);
                        }
                    } catch (e) {
                        this.showToast('Error creating trip', false);
                    }
                },

                async addBudget() {
                    await this.postData(`/api/trips/${this.selectedTripId}/budget`, this.budgetForm, 'Budget updated successfully!');
                    this.budgetForm.amount = '';
                },
                async addDestination() {
                    await this.postData(`/api/trips/${this.selectedTripId}/destinations`, this.destForm, 'Destination added successfully!');
                    this.destForm = { city: '', country: '', dates: '' };
                },
                async addItinerary() {
                    await this.postData(`/api/trips/${this.selectedTripId}/itinerary`, this.itinForm, 'Itinerary day added successfully!');
                    this.itinForm = { day_num: '', date_str: '', details: '' };
                },
                async addTransportation() {
                    await this.postData(`/api/trips/${this.selectedTripId}/transportation`, this.transForm, 'Transportation recorded successfully!');
                    this.transForm = { type: 'Flight', details: '', cost: '' };
                },
                async addAccommodation() {
                    await this.postData(`/api/trips/${this.selectedTripId}/accommodations`, this.accomForm, 'Accommodation recorded successfully!');
                    this.accomForm = { name: '', check_in: '', check_out: '', cost: '' };
                },
                async addActivity() {
                    await this.postData(`/api/trips/${this.selectedTripId}/activities`, this.actForm, 'Activity recorded successfully!');
                    this.actForm = { name: '', date_str: '', cost: '' };
                },
                async addExpense() {
                    await this.postData(`/api/trips/${this.selectedTripId}/expenses`, this.genExpForm, 'Expense recorded successfully!');
                    this.genExpForm = { category: 'Food & Dining', date: '', amount: '' };
                },

                async postData(url, payload, successMsg) {
                    try {
                        let res = await fetch(url, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(payload)
                        });
                        let data = await res.json();
                        if (res.ok) {
                            this.showToast(successMsg);
                            await this.fetchTripDetails();
                        } else {
                            this.showToast(data.error, false);
                        }
                    } catch (e) {
                        this.showToast('Server communication error', false);
                    }
                },

                async fetchMonthlyReport() {
                    if (!this.monthlyReportYM) {
                        this.showToast('Please select year and month', false);
                        return;
                    }
                    try {
                        let res = await fetch(`/api/reports/monthly?ym=${this.monthlyReportYM}`);
                        let data = await res.json();
                        this.monthlyReportData = data;
                    } catch (e) {
                        this.showToast('Failed to generate monthly report', false);
                    }
                },

                async askAI() {
                    if (!this.aiQueryText.trim()) return;
                    try {
                        let res = await fetch('/api/ai/query', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ query: this.aiQueryText })
                        });
                        let data = await res.json();
                        this.aiResponse = data.response;
                    } catch (e) {
                        this.aiResponse = 'AI Assistant is currently unavailable.';
                    }
                }
            }
        }
    </script>
</body>
</html>
"""

# --- Flask Routes & REST Endpoints ---
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/trips', methods=['GET', 'POST'])
def handle_trips():
    if request.method == 'POST':
        data = request.json
        tid = data.get('trip_id')
        name = data.get('name')
        start = data.get('start_date')
        end = data.get('end_date')
        desc = data.get('description', '')

        if not tid or not name or not start or not end:
            return jsonify({"error": "Missing required fields"}), 400
        if tid in trips_db:
            return jsonify({"error": "Trip ID already exists"}), 400

        trips_db[tid] = Trip(tid, name, start, end, desc)
        return jsonify({"message": f"Trip '{name}' created successfully!"})
    
    return jsonify({"trips": [t.to_dict() for t in trips_db.values()]})

@app.route('/api/trips/<trip_id>/budget', methods=['POST'])
def set_budget(trip_id):
    trip = trips_db.get(trip_id)
    if not trip: return jsonify({"error": "Trip not found"}), 404
    trip.set_budget(request.json.get('amount', 0))
    return jsonify({"message": "Budget updated"})

@app.route('/api/trips/<trip_id>/destinations', methods=['POST'])
def add_destination(trip_id):
    trip = trips_db.get(trip_id)
    if not trip: return jsonify({"error": "Trip not found"}), 404
    d = request.json
    trip.destinations.append({'city': d.get('city'), 'country': d.get('country'), 'dates': d.get('dates')})
    return jsonify({"message": "Destination added"})

@app.route('/api/trips/<trip_id>/itinerary', methods=['POST'])
def add_itinerary(trip_id):
    trip = trips_db.get(trip_id)
    if not trip: return jsonify({"error": "Trip not found"}), 404
    i = request.json
    trip.itinerary.append({'day': int(i.get('day_num', 1)), 'date': i.get('date_str'), 'details': i.get('details')})
    return jsonify({"message": "Itinerary added"})

@app.route('/api/trips/<trip_id>/transportation', methods=['POST'])
def add_transportation(trip_id):
    trip = trips_db.get(trip_id)
    if not trip: return jsonify({"error": "Trip not found"}), 404
    t = request.json
    trip.transportation.append({'type': t.get('type'), 'details': t.get('details'), 'cost': float(t.get('cost', 0))})
    return jsonify({"message": "Transportation logged"})

@app.route('/api/trips/<trip_id>/accommodations', methods=['POST'])
def add_accommodation(trip_id):
    trip = trips_db.get(trip_id)
    if not trip: return jsonify({"error": "Trip not found"}), 404
    a = request.json
    trip.accommodations.append({'name': a.get('name'), 'check_in': a.get('check_in'), 'check_out': a.get('check_out'), 'cost': float(a.get('cost', 0))})
    return jsonify({"message": "Accommodation logged"})

@app.route('/api/trips/<trip_id>/activities', methods=['POST'])
def add_activity(trip_id):
    trip = trips_db.get(trip_id)
    if not trip: return jsonify({"error": "Trip not found"}), 404
    act = request.json
    trip.activities.append({'name': act.get('name'), 'date': act.get('date_str'), 'cost': float(act.get('cost', 0))})
    return jsonify({"message": "Activity recorded"})

@app.route('/api/trips/<trip_id>/expenses', methods=['POST'])
def add_expense(trip_id):
    trip = trips_db.get(trip_id)
    if not trip: return jsonify({"error": "Trip not found"}), 404
    e = request.json
    trip.expenses.append({'category': e.get('category'), 'amount': float(e.get('amount', 0)), 'date': e.get('date')})
    return jsonify({"message": "Expense recorded"})

@app.route('/api/reports/monthly', methods=['GET'])
def monthly_report():
    ym = request.args.get('ym', '')
    total_spent = 0.0
    trips_matched = 0
    for trip in trips_db.values():
        if trip.start_date.startswith(ym) or trip.end_date.startswith(ym):
            total_spent += trip.calculate_total_expenses()
            trips_matched += 1
    return jsonify({"year_month": ym, "trips_count": trips_matched, "total_spent": total_spent})

@app.route('/api/ai/query', methods=['POST'])
def ai_query():
    q = request.json.get('query', '').lower()
    if "total spent" in q or "how much did i spend" in q:
        total_all = sum(t.calculate_total_expenses() for t in trips_db.values())
        return jsonify({"response": f"You have spent a total of ${total_all:.2f} across all registered trips."})
    elif "budget" in q:
        responses = []
        for t in trips_db.values():
            spent = t.calculate_total_expenses()
            pct = (spent / t.budget * 100) if t.budget > 0 else 0
            responses.append(f"• {t.name}: Spent ${spent:.2f} of ${t.budget:.2f} ({pct:.1f}% used)")
        return jsonify({"response": "Budget Status:\n" + ("\n".join(responses) if responses else "No trips found.")})
    elif "destination" in q:
        dest_list = []
        for t in trips_db.values():
            for d in t.destinations:
                dest_list.append(f"• {d['city']}, {d['country']} (Trip: {t.name})")
        return jsonify({"response": "Destinations:\n" + ("\n".join(dest_list) if dest_list else "No destinations added.")})
    else:
        return jsonify({"response": "I can answer queries about your total spending, budget utilization, or destinations. Try asking 'What is my total spent?' or 'Show budget status'."})

if __name__ == '__main__':
    app.run(debug=True, port=5000)