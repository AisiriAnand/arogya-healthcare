# AROGYA Healthcare - Rural Healthcare Platform

## Features

- **Hospital Finder**: Interactive map with 30,273+ hospitals across India
- **Symptom Checker**: AI-powered symptom analysis using Gemini LLM
- **Health Dashboard**: Personal health tracking and reminders
- **Emergency Services**: Quick access to nearby healthcare facilities

## Quick Start

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
export GEMINI_API_KEY="your-gemini-api-key-here"  # Required for symptom checker
python -m uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

### Frontend Setup
```bash
cd frontend
pip install -r requirements.txt
python working_app.py
```

### Access Points
- **Frontend**: http://localhost:5001
- **Backend API**: http://localhost:5000/docs
- **Hospital Finder**: http://localhost:5001/hospital-finder
- **Symptom Checker**: http://localhost:5001/symptom-checker

## Symptom Checker - Gemini LLM Integration

The symptom checker is now powered by Google's Gemini LLM for intelligent medical analysis.

### Environment Setup
Set your Gemini API key before running:
```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
```

### Features
- **AI Analysis**: Top 3 likely conditions with confidence scores
- **Triage System**: Emergency/Urgent/Non-urgent/Self-care classification
- **Safety First**: Automatic emergency detection for critical symptoms
- **Caching**: 24-hour response caching for identical inputs
- **Privacy**: No PII logged, anonymized request tracking

### API Response Format
```json
{
  "predictions": [
    {
      "condition": "Common Cold",
      "score": 0.85,
      "explanation": "Based on runny nose and cough symptoms"
    }
  ],
  "model_version": "gemini-llm-v1",
  "triage": "self-care",
  "confidence": 0.85,
  "recommendation_text": "Rest, fluids, and over-the-counter medication"
}
```

## Hospital Finder

Interactive map-based hospital locator with:
- **30,273+ Hospitals**: Comprehensive database across India
- **Real-time Search**: By location, category, and GPS
- **Color-coded Markers**: Emergency (red), Government (blue), Private (green)
- **Contact Integration**: Direct call and directions functionality

## Technology Stack

- **Backend**: FastAPI, Python
- **Frontend**: Flask, Tailwind CSS, Leaflet.js
- **AI**: Google Gemini LLM
- **Database**: CSV-based hospital data
- **Caching**: In-memory JSON cache

## Development

### Branch Structure
- `main`: Production-ready code
- `feature/llm-symptom`: Gemini LLM integration

### API Documentation
Visit http://localhost:5000/docs for complete API documentation.

## License

© 2024 AROGYA Healthcare. All rights reserved.
