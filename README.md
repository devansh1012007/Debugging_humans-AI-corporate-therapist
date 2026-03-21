AI Corporate Therapist (MindSpace)

The Problem We Are Solving

Workplace Burnout & Stigma: Employees often hesitate to seek traditional therapy due to cost, stigma, or scheduling. We provide immediate, private, first-line AI emotional support.

Systemic Blind Spots: Management frequently misses early signs of team fatigue and communication breakdowns. We provide aggregated, anonymized insights into organizational health.

Crisis Escalation: AI isn't a silver bullet. We actively track user distress and seamlessly flag when a human therapist is required.

Core Features

Personalized AI Therapy: Real-time, streaming AI chat with different modes (Therapy, Specialist) tailored to user history.

Psychological Tracking: Dashboards that track emotional balance, personality data, and daily wellness snapshots.

Organizational Insights: Manager-level drill-downs to view team cohesion metrics based on corporate hierarchy (without exposing individual private chats).

Human Intervention Flagging: A built-in system to detect and escalate users who need real human psychiatric help.

Architecture & Tech Stack

Frontend: Plain HTML, CSS (Tailwind), and Vanilla JavaScript (index.html, mindspace_landing.html). No React or npm build required.

Backend: Django Rest Framework running locally, handling secure JWT authentication, user data, and session histories.

Database: PostgreSQL containerized via Docker.

AI Microservice: An external/local FastAPI server utilizing Langchain, HuggingFace, and FAISS for Retrieval-Augmented Generation (RAG).

Localhost Setup Guide

1. Start the Database
Run the provided Docker Compose file to spin up the PostgreSQL database:
docker-compose up -d db

2. Start the AI Server
Navigate to the AI+RAG folder and start the FastAPI microservice on your localhost (typically port 8001):
uvicorn ai_server:app --host 0.0.0.0 --port 8001

3. Start the Django Backend
Apply migrations and start the Django server on your localhost:
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

4. Launch the Frontend
Since the frontend is pure HTML/JS, simply open frontend/index.html or frontend/mindspace_landing.html directly in any web browser to start using the application.
