# 🏥 MELCO-Care: Autonomous Hospital Agentic System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red?style=for-the-badge&logo=streamlit)
![Firebase](https://img.shields.io/badge/Firebase-Firestore-orange?style=for-the-badge&logo=firebase)
![Ollama](https://img.shields.io/badge/Ollama-LLM-purple?style=for-the-badge)

**An AI-powered hospital management system with multiple intelligent agents for appointment scheduling, pharmacy management, emergency triage, and government scheme matching.**

[Features](#-features) • [Architecture](#-architecture) • [Installation](#-installation) • [Usage](#-usage) • [API Reference](#-api-reference)

</div>

---

## 🌟 Features

### 🤖 Intelligent Agents

| Agent | Description |
|-------|-------------|
| **🗓️ Appointment Scheduler** | Books doctor appointments based on symptoms, auto-routes to correct department |
| **💊 Pharmacy Agent** | Medicine search by illness, auto-reserve with 1-hour pickup window |
| **🚑 Triage Agent** | Emergency detection, ambulance dispatch, bed booking with 2-hour return timer |
| **📋 Scheme Matcher** | Matches patient disease history with government health schemes |
| **🎯 Orchestrator** | Central coordinator that routes requests to appropriate agents |

### 🎨 Modern Frontend

- **High Contrast Mode** - Accessibility toggle for vision-impaired users
- **Glass Card Design** - Frosted glass UI with smooth animations
- **Tabbed Dashboard** - Organized patient interface (Chat / Appointments / Pharmacy)
- **Real-time Updates** - Live appointment and reservation status

### 🔐 Security

- Firebase service account credentials excluded from git
- Environment variables for sensitive configuration
- Role-based access (Patient vs Doctor dashboards)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Streamlit)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │
│  │    Chat     │  │ Appointments│  │  Pharmacy   │               │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘               │
└─────────┼────────────────┼────────────────┼─────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    ORCHESTRATOR AGENT                     │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │   │
│  │  │ Intent      │ │ LLM Planner │ │ Response Formatter  │ │   │
│  │  │ Detection   │ │ (Ollama)    │ │                     │ │   │
│  │  └──────┬──────┘ └──────┬──────┘ └─────────────────────┘ │   │
│  └─────────┼───────────────┼────────────────────────────────┘   │
│            │               │                                     │
│  ┌─────────▼───────────────▼────────────────────────────────┐   │
│  │                    SPECIALIZED AGENTS                     │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ │   │
│  │  │Appointment│ │ Pharmacy  │ │  Triage   │ │  Scheme   │ │   │
│  │  │ Scheduler │ │   Agent   │ │   Agent   │ │  Matcher  │ │   │
│  │  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └─────┬─────┘ │   │
│  └────────┼─────────────┼─────────────┼─────────────┼───────┘   │
└───────────┼─────────────┼─────────────┼─────────────┼───────────┘
            │             │             │             │
            ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FIREBASE FIRESTORE                          │
│  ┌─────────┐ ┌─────────┐ ┌───────────────┐ ┌─────────────────┐  │
│  │  users  │ │hospitals│ │ appointments  │ │ medicine_       │  │
│  │         │ │         │ │               │ │ reservations    │  │
│  └─────────┘ └─────────┘ └───────────────┘ └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Melco Hospital Care/
├── backend/
│   ├── agents/
│   │   ├── orchestrator.py       # Central coordinator agent
│   │   ├── appointment_scheduler.py  # Appointment booking logic
│   │   ├── pharmacy_agent.py     # Medicine search & reservation
│   │   ├── triage_agent.py       # Emergency handling
│   │   ├── scheme_matcher.py     # Government scheme matching
│   │   └── tool_registry.py      # Agent registration utility
│   ├── db/
│   │   └── firebase_client.py    # Firebase connection handler
│   ├── models/
│   │   └── schemas.py            # Pydantic request/response models
│   ├── main.py                   # FastAPI application & endpoints
│   ├── config.py                 # Environment configuration
│   ├── .env                      # Environment variables (not in git)
│   └── serviceAccount.json       # Firebase credentials (not in git)
├── frontend/
│   ├── app.py                    # Streamlit application
│   ├── config.py                 # Frontend configuration
│   └── logo.png                  # MELCO-Care logo
├── requirements.txt              # Python dependencies
├── firestore_backup.json         # Sample database structure
└── README.md                     # This file
```

---

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher
- [Ollama](https://ollama.ai/) installed and running
- Firebase project with Firestore database
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/soumysuwas/Melco_hospital_care.git
cd Melco_hospital_care
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Ollama

Pull required models:

```bash
ollama pull gemma3:4b
# Optional: for vision capabilities
ollama pull qwen3-vl:4b
```

### Step 5: Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or use existing one
3. Enable Firestore Database
4. Go to Project Settings → Service Accounts → Generate New Private Key
5. Save the file as `backend/serviceAccount.json`

### Step 6: Configure Environment Variables

Create `backend/.env`:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:4b
FIREBASE_CREDENTIAL_PATH=serviceAccount.json
FIREBASE_DB_URL=https://YOUR-PROJECT-ID.firebaseio.com
```

### Step 7: Initialize Database

Import sample data to Firestore using `firestore_backup.json` or create your own collections:

**Required Collections:**
- `users` - Patient and doctor profiles
- `hospitals` - Hospital info with medicine inventory
- `appointments` - Booking records
- `schemes` - Government health schemes
- `medicine_reservations` - Pharmacy reservations
- `emergency_dispatches` - Ambulance dispatch records

---

## 💻 Usage

### Start the Backend Server

```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Start the Frontend

```bash
cd frontend
python -m streamlit run app.py
```

### Access the Application

- **Frontend:** http://localhost:8501
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### Demo Credentials

| Role | User ID | Location |
|------|---------|----------|
| Patient | p201 | Hyderabad |
| Patient | p202 | Delhi |
| Doctor | d101 | Hyderabad |
| Doctor | d102 | Delhi |

---

## 🔧 API Reference

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/login` | POST | User authentication |
| `/chat` | POST | Main chat interface (routes to agents) |

### Patient Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/patient/appointments/{id}` | GET | Get patient's appointments |

### Doctor Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/doctor/appointments/{id}` | GET | Get doctor's appointment queue |
| `/doctor/decision` | POST | Accept/reject appointment |
| `/doctor/assign-disease` | POST | Assign final diagnosis |

### Pharmacy Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/pharmacy/reserve` | POST | Reserve medicine |
| `/pharmacy/reservations/{id}` | GET | Get patient's reservations |
| `/pharmacy/cancel` | POST | Cancel reservation |
| `/pharmacy/pickup` | POST | Mark as picked up |

### Emergency Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/emergency/request` | POST | Dispatch ambulance + book bed |
| `/emergency/dispatches/{id}` | GET | Get dispatch history |

---

## 💬 Chat Commands

The AI assistant understands natural language. Here are some example commands:

### Appointment Booking
```
"I have a headache and fever, book me an appointment"
"Schedule a doctor visit for tomorrow at 3pm"
"I need to see a cardiologist"
```

### Pharmacy
```
"I need medicine for fever"
"I want paracetamol"
"Show me medicines for cold"
```

### Emergency
```
"Emergency! I'm having a heart attack"
"Urgent! Need an ambulance"
"My father is having chest pain"
```

### Government Schemes
```
"Find government schemes for my diseases"
"What schemes are available for cancer patients?"
"Show me health benefits I'm eligible for"
```

---

## 🗄️ Database Schema

### Users Collection
```json
{
  "name": "John Doe",
  "role": "patient",
  "location": "Hyderabad",
  "disease_history": ["Diabetes", "Hypertension"]
}
```

### Hospitals Collection
```json
{
  "hospital_name": "Apollo Hospital",
  "location": "Hyderabad",
  "departments": ["Cardiology", "General Medicine"],
  "doctors": [...],
  "medicine_inventory": [...],
  "total_beds": 220,
  "beds_available": 185,
  "ambulance_count": 8
}
```

### Medicine Inventory (in Hospitals)
```json
{
  "medicine_id": "med001",
  "medicine_name": "Paracetamol 500mg",
  "salt_composition": "Paracetamol",
  "manufacturer": "Cipla",
  "stock_count": 150,
  "treats": ["fever", "headache", "body pain"]
}
```

---

## 🔄 Auto-Expiry Systems

### Medicine Reservations
- **Window:** 1 hour from reservation
- **Action:** If not picked up, reservation expires and stock is restored
- **Check:** On-demand when patient views reservations

### Ambulance Dispatch
- **Window:** 2 hours from dispatch
- **Action:** Ambulance count restored to hospital
- **Check:** On-demand when emergency endpoint is called

---

## 🛠️ Troubleshooting

### Ollama Connection Error
```bash
# Check if Ollama is running
ollama list

# Start Ollama if not running
ollama serve
```

### Firebase Connection Error
- Verify `serviceAccount.json` exists in `/backend`
- Check `FIREBASE_DB_URL` in `.env`
- Ensure Firestore rules allow read/write

### Port Already in Use
```bash
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Kill process on port 8501
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

---

## 📄 License

This project is licensed under the MIT License.

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📞 Contact

**Author:** soumysuwas  
**Email:** soumy.suwas7@gmail.com  
**GitHub:** [@soumysuwas](https://github.com/soumysuwas)

---

<div align="center">

**Made with ❤️ for MELCO Healthcare**

</div>
