from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Rural Healthcare Backend", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class Doctor(BaseModel):
    id: int
    name: str
    specialty: str
    hospital: str
    experience: int
    rating: float

class Article(BaseModel):
    id: int
    title: str
    category: str
    content: str
    author: str
    date: str

class Reminder(BaseModel):
    id: int
    medication: str
    dosage: str
    frequency: str
    time: str

# Sample data
doctors_data = [
    {
        "id": 1,
        "name": "Dr. Rajesh Kumar",
        "specialty": "General Medicine",
        "hospital": "Rural Health Center",
        "experience": 10,
        "rating": 4.5
    },
    {
        "id": 2,
        "name": "Dr. Priya Singh",
        "specialty": "Pediatrics",
        "hospital": "Community Hospital",
        "experience": 8,
        "rating": 4.7
    },
    {
        "id": 3,
        "name": "Dr. Amit Patel",
        "specialty": "Surgery",
        "hospital": "District Hospital",
        "experience": 15,
        "rating": 4.6
    }
]

articles_data = [
    {
        "id": 1,
        "title": "Understanding Diabetes",
        "category": "Chronic Diseases",
        "content": "Diabetes is a chronic disease that affects how your body processes blood glucose.",
        "author": "Dr. Health Expert",
        "date": "2024-01-15"
    },
    {
        "id": 2,
        "title": "Importance of Regular Exercise",
        "category": "Wellness",
        "content": "Regular exercise helps maintain a healthy lifestyle and prevents many diseases.",
        "author": "Fitness Coach",
        "date": "2024-01-20"
    }
]

reminders_data = [
    {
        "id": 1,
        "medication": "Aspirin",
        "dosage": "100mg",
        "frequency": "Once daily",
        "time": "08:00 AM"
    }
]

# Endpoints
@app.get("/api/health")
async def health_check():
    return {"status": "Backend server is running"}

@app.get("/api/doctors", response_model=List[Doctor])
async def get_doctors():
    return doctors_data

@app.get("/api/articles", response_model=List[Article])
async def get_articles():
    return articles_data

@app.get("/api/reminders", response_model=List[Reminder])
async def get_reminders():
    return reminders_data

# Error handling
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return {"error": "Internal server error"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5000))
    print(f"Backend server is running on http://localhost:{port}")
    print(f"Health check: http://localhost:{port}/api/health")
    uvicorn.run(app, host="0.0.0.0", port=port)
