from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Import feature routers
from hospital_finder.router import router as hospital_router
from symptom_checker.router import router as symptom_router
from medication_reminders.router import router as medication_router

app = FastAPI(title="AROGYA Healthcare Backend", version="2.0.0")

# Include feature routers
app.include_router(hospital_router)
app.include_router(symptom_router)
app.include_router(medication_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic health check
@app.get("/api/health")
async def health_check():
    return {"status": "Backend server is running", "version": "2.0.0"}

# Basic endpoints for backwards compatibility
@app.get("/api/doctors")
async def get_doctors():
    return [
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
            "name": "Dr. Priya Sharma",
            "specialty": "Pediatrics",
            "hospital": "District Hospital",
            "experience": 15,
            "rating": 4.6
        }
    ]

@app.get("/api/articles")
async def get_articles():
    return [
        {
            "id": 1,
            "title": "Understanding Diabetes",
            "category": "Chronic Diseases",
            "content": "Diabetes is a chronic disease that affects how your body processes blood glucose.",
            "author": "Dr. Health Expert",
            "date": "2024-01-15"
        }
    ]

@app.get("/api/reminders")
async def get_reminders():
    return [
        {
            "id": 1,
            "medication": "Aspirin",
            "dosage": "100mg",
            "frequency": "Once daily",
            "time": "08:00 AM"
        }
    ]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5000))
    print(f"AROGYA Healthcare Backend v2.0.0 running on http://localhost:{port}")
    print("Features: Hospital Finder, Symptom Checker (Gemini LLM)")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
