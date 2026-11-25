# Medicall — AI-Powered Voice Clinic Receptionist

Medicall is an AI-powered voice receptionist that helps patients interact with a clinic through natural voice conversations. Patients can check doctor availability, book appointments, and cancel existing appointments without navigating complicated forms.

The project combines real-time voice AI with a clinic management dashboard, allowing staff to monitor doctors, availability, and appointments.

## Features

- **AI Voice Receptionist:** Natural two-way voice conversations through the browser.
- **Doctor Availability:** Retrieves doctors and available appointment slots from the database.
- **Appointment Booking:** Books appointments after collecting patient details and obtaining explicit confirmation.
- **Appointment Cancellation:** Identifies existing appointments and cancels them after confirmation.
- **Clinic Dashboard:** Overview of appointments, doctors, and availability.
- **Live Updates:** Dashboard data reflects booking and cancellation changes.
- **Voice Pipeline:** Speech recognition, LLM processing, and speech generation using Pipecat, ElevenLabs, and Google Gemini.

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, Vite, Tailwind CSS |
| Backend | Python, FastAPI |
| Voice orchestration | Pipecat |
| Speech-to-text | ElevenLabs |
| Language model | Google Gemini |
| Text-to-speech | ElevenLabs |
| Database | SQLite, SQLAlchemy |
| Browser communication | WebRTC, Pipecat Small WebRTC |
| HTTP client | Axios |

## Architecture

1. Patient starts a browser-based voice session.
2. Audio is transmitted to the Pipecat voice pipeline using WebRTC.
3. ElevenLabs processes speech into text.
4. Google Gemini interprets the request and determines the appropriate action.
5. Pipecat invokes the relevant appointment-management function when required.
6. FastAPI and SQLAlchemy interact with the SQLite database.
7. ElevenLabs generates the spoken response.
8. The frontend dashboard retrieves and displays the updated clinic data.

## Project Structure

```text
Medicall/
├── backend/
│   ├── app/
│   │   ├── database/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── schemas/
│   │   └── voice/
│   ├── bot.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   └── services/
│   ├── package.json
│   └── vite.config.js
├── .env.example
├── .gitignore
└── README.md
```

## Prerequisites

- Python 3.11 or later (Python 3.13.3 was used during development)
- Node.js and npm
- Gemini API key
- ElevenLabs API key and voice ID

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Medicall.git
cd Medicall
```

### 2. Configure environment variables

Create a `.env` file in the backend directory using `.env.example` as a reference.

Configure the following variables:

```env
GEMINI_API_KEY=your_gemini_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=your_elevenlabs_voice_id

APP_ENV=development
```

Never commit API keys or secret credentials.

### 3. Set up the backend

```bash
cd backend

python -m venv venv
```

Activate the environment:

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

Backend API: `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

### 4. Start the voice agent

Open another terminal:

```bash
cd backend
```

Activate the virtual environment and run:

```bash
python bot.py -t webrtc
```

The voice agent uses the Pipecat Small WebRTC transport.

### 5. Set up the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local Vite URL shown in your terminal.

Allow microphone access when prompted by the browser.

## Environment Configuration

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API credential |
| `ELEVENLABS_API_KEY` | ElevenLabs API credential |
| `ELEVENLABS_VOICE_ID` | ElevenLabs voice used for speech generation |
| `APP_ENV` | Application environment |
| `CORS_ALLOWED_ORIGINS` | Optional backend CORS origin configuration |
| `VITE_API_BASE_URL` | Optional frontend API base URL |
| `VITE_PIPECAT_CONNECTION_URL` | Optional Pipecat connection URL, if supported by the frontend configuration |

The backend and frontend must be configured to use matching local service addresses.

## API Overview

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/doctors` | Retrieve doctors |
| GET | `/api/doctors/{doctor_id}` | Retrieve doctor details |
| GET | `/api/specialties` | Retrieve specialties |
| GET | `/api/availability` | Retrieve available slots |
| POST | `/api/appointments/book` | Book an appointment |
| POST | `/api/appointments/cancel` | Cancel an appointment |
| GET | `/api/appointments` | Retrieve appointments |
| GET | `/api/dashboard/stats` | Retrieve dashboard statistics |

Interactive API documentation is available at `/docs`.

## Project Scope

Medicall is a demonstration application using mock clinic data and a local SQLite database. Browser-based WebRTC provides the voice interaction experience; it does not represent integration with a live hospital telephone system.

The project is intended as an internship assignment prototype and is not a production clinical or hospital management system.

## Security

- API credentials are stored in environment variables.
- Local environment files and database files are excluded from version control.
- Do not use real patient information when testing or demonstrating the application.

## License

This project is available under the MIT License. See `LICENSE` for details.
