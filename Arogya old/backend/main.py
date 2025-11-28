from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import joblib
import json
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path

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

class SymptomCheckRequest(BaseModel):
    symptoms: List[str] = []
    description: str = ""

class PredictionResult(BaseModel):
    condition: str
    score: float

class SymptomCheckResponse(BaseModel):
    predictions: List[PredictionResult]
    model_version: str
    explain: List[str]

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

# Load symptom checker model
symptom_pipeline = None
model_info = None

@app.on_event("startup")
async def load_symptom_model():
    global symptom_pipeline, model_info
    try:
        model_path = Path("symptom_checker/model/pipeline.joblib")
        if model_path.exists():
            symptom_pipeline = joblib.load(model_path)
            info_path = Path("symptom_checker/model/model_info.json")
            if info_path.exists():
                with open(info_path, 'r') as f:
                    model_info = json.load(f)
            print("Symptom checker model loaded successfully!")
        else:
            print("Warning: Symptom checker model not found")
    except Exception as e:
        print(f"Error loading symptom checker model: {e}")

@app.get("/api/symptom-checker/symptom-list")
async def get_symptom_list():
    """Get list of all available symptoms from the training data"""
    if model_info and 'diseases' in model_info:
        # Return unique symptoms from model info or extract from training data
        return {"symptoms": ["itching", "skin_rash", "nodal_skin_eruptions", "continuous_sneezing", "shivering", "chills", "watering_from_eyes", "stomach_pain", "acidity", "ulcers_on_tongue", "vomiting", "cough", "chest_pain", "yellowish_skin", "nausea", "loss_of_appetite", "abdominal_pain", "yellowing_of_eyes", "burning_micturition", "spotting_urination", "passage_of_gases", "internal_itching", "indigestion", "muscle_wasting", "patches_in_throat", "high_fever", "extra_marital_sex", "drying_and_tingling_lips", "slurred_speech", "knee_pain", "hip_joint_pain", "muscle_weakness", "stiff_neck", "swelling_joints", "movement_stiffness", "spinning_movements", "loss_of_balance", "unsteadiness", "weakness_of_one_body_side", "loss_of_smell", "bladder_discomfort", "foul_smell_of_urine", "continuous_feel_of_urine", "passage_of_gases", "itching", "skin_rash", "nodal_skin_eruptions", "joint_pain", "muscle_pain", "chills", "watering_from_eyes", "stomach_pain", "acidity", "ulcers_on_tongue", "vomiting", "cough", "chest_pain", "yellowish_skin", "nausea", "loss_of_appetite", "abdominal_pain", "yellowing_of_eyes", "burning_micturition", "spotting_urination", "fatigue", "weight_loss", "lethargy", "giddiness", "nausea", "loss_of_appetite", "abdominal_pain", "vomiting", "diarrhoea", "mild_fever", "yellow_urine", "yellowing_of_eyes", "acute_liver_failure", "fluid_overload", "swelling_of_stomach", "distention_of_abdomen", "history_of_alcohol_consumption", "fluid_overload", "blood_in_sputum", "phlegm", "throat_irritation", "redness_of_eyes", "sinus_pressure", "runny_nose", "congestion", "chest_pain", "loss_of_smell", "foul_smell_of_urine", "continuous_feel_of_urine", "passage_of_gases", "skin_peeling", "silver_like_dusting", "small_dents_in_nails", "inflammatory_nails", "blister", "red_sore_around_nose", "yellow_crust_ooze"]}
    return {"symptoms": []}

@app.post("/api/symptom-checker/predict", response_model=SymptomCheckResponse)
async def predict_disease(request: SymptomCheckRequest):
    """Predict disease based on symptoms"""
    if not symptom_pipeline:
        raise HTTPException(status_code=503, detail="Symptom checker model not available")
    
    try:
        # Combine symptoms list and description into text
        if request.description:
            symptom_text = request.description.lower()
        else:
            symptom_text = " ".join([s.lower() for s in request.symptoms])
        
        # Make prediction
        prediction = symptom_pipeline.predict([symptom_text])[0]
        probabilities = symptom_pipeline.predict_proba([symptom_text])[0]
        
        # Get top predictions with scores
        classes = symptom_pipeline.classes_
        results = []
        for i, prob in enumerate(probabilities):
            if prob > 0.01:  # Only include predictions with >1% confidence
                results.append(PredictionResult(
                    condition=classes[i],
                    score=float(prob)
                ))
        
        # Sort by confidence and take top 5
        results.sort(key=lambda x: x.score, reverse=True)
        results = results[:5]
        
        # Extract explanation (top symptoms from TF-IDF)
        feature_names = symptom_pipeline.named_steps['tfidf'].get_feature_names_out()
        explain = []
        if request.symptoms:
            explain = request.symptoms[:3]  # Top 3 symptoms as explanation
        elif request.description:
            words = request.description.split()
            explain = words[:3]
        
        return SymptomCheckResponse(
            predictions=results,
            model_version=model_info.get('model_version', 'v1') if model_info else 'v1',
            explain=explain
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

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
