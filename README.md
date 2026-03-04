AI Psychologist & Team Insights Dashboard

A comprehensive, AI-powered emotional wellness and workplace wellbeing platform. This application features a dual-dashboard system (Personal & Team), real-time streaming AI chat, and secure authentication, built with Django Rest Framework and React.

🚀 Features

🧠 Personal Dashboard (AI Psychologist)

Daily Snapshots: Visual metrics for Focus State, Social Connectivity, and Emotional Balance.

Wellness Actions: Interactive accordions suggesting breathing exercises, digital boundaries, etc.

AI Chat Interface:

Real-time Streaming: AI responses appear token-by-token (like ChatGPT).

Stop Generation: Users can halt AI responses mid-stream.

Session Management: Create, save, and browse history of chat sessions.

Multi-Mode: Switch between "Specialist" and "Counselor" AI personas.

👥 Team Dashboard (Manager View)

Systemic Patterns: Insights into communication silos, meeting overload, and feedback latency.

Leadership Recommendations: Actionable steps to improve team cohesion (e.g., Async-first weeks).

Health Metrics: Visual representation of team cohesion and resilience.

🔐 Security & Auth

JWT Authentication: Secure login/registration using Access and Refresh tokens (dj-rest-auth).

Silent Refresh: Auto-renews tokens in the background without logging the user out.

Role-Based Access: (Configurable) Separation between individual user data and team insights.

🎨 UI/UX

Premium Dark Theme: Built with Tailwind CSS colors (Slate 900/800).

Collapsible Sidebar: Responsive navigation with smooth transitions.

Lucide Icons: Consistent, modern iconography.

🛠️ Tech Stack

Frontend

React: Functional components, Hooks (useState, useEffect, useRef).

Styling: Tailwind CSS (via injected global styles), Lucide React (Icons).

API Client: Custom class with built-in JWT interceptors for auto-refreshing tokens.

Backend

Django & DRF: Robust REST API structure.

Authentication: dj-rest-auth, django-allauth, simplejwt.

Database: SQLite (default) / PostgreSQL (production ready).

AI Engine: Ollama (Local LLM) running llama3.2:1b.

⚙️ Prerequisites

Python 3.10+

Node.js & npm

Ollama: Installed and running locally for the AI features.

📥 Installation Guide

1. AI Setup (Ollama)

This project uses a local LLM to save costs and ensure privacy.

Download Ollama from ollama.com.

Pull the required model:

ollama pull llama3.2:1b


Ensure Ollama is running (ollama serve).

2. Backend Setup (Django)

# Clone the repository
git clone <your-repo-url>
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install django djangorestframework django-cors-headers dj-rest-auth djangorestframework-simplejwt django-allauth ollama

# Run Migrations
python manage.py makemigrations
python manage.py migrate

# Create Superuser (Admin)
python manage.py createsuperuser

# Start Server
python manage.py runserver


3. Frontend Setup (React)

cd frontend

# Install dependencies
npm install lucide-react

# Start Development Server
npm start


🔧 Configuration

Backend (settings.py)

Ensure your REST_FRAMEWORK settings use JWT and your CORS settings allow the frontend.

# settings.py

INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'corsheaders',
    ...
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]

# JWT Settings (Optional customization)
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}


Frontend (App.jsx)

If your backend runs on a different port, update the API_BASE constant at the top of the file:

const API_BASE = '[http://127.0.0.1:8000/](http://127.0.0.1:8000/)'; 


📖 Usage

Register: Open the app and create a new account.

Personal Dashboard: View your daily snapshot.

Chat: * Click "Chat" in the sidebar.

Click "New Session" -> Enter a Title (e.g., "Work Stress") -> Select Mode ("Specialist").

Start typing. The AI will stream the response.

Click the red Stop square to cancel generation if needed.

Team View: Click "Team Overview" to see organizational insights (currently mocked/static in frontend, ready for backend integration).

🐛 Troubleshooting

"Authentication credentials were not provided":

Ensure your settings.py includes rest_framework_simplejwt.authentication.JWTAuthentication.

Check if localStorage has access_token.

AI not replying (Stream empty):

Verify Ollama is running: curl http://localhost:11434.

Check Django terminal for "DEBUG TOKEN" logs.

Ensure llama3.2:1b is actually installed.

CORS Errors:

Install django-cors-headers.

Add corsheaders.middleware.CorsMiddleware to the top of MIDDLEWARE.

📄 License

MIT License
