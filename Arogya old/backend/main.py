from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import joblib
import json
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
import hashlib
import requests
import time
from datetime import timedelta

# Import hospital finder router
from hospital_finder.router import router as hospital_router

# Environment configuration for Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_API_URL = os.getenv("GEMINI_API_URL", "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent")

# Simple cache for Gemini responses
CACHE_FILE = Path("gemini_cache.json")
CACHE_DURATION = timedelta(hours=24)

# Logging setup
LOG_FILE = Path("predictions.log")

app = FastAPI(title="Rural Healthcare Backend", version="1.0.0")

# Include hospital finder router
app.include_router(hospital_router)

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
    age: int = None
    sex: str = ""
    onset_days: int = None
    severity: str = ""
    comorbidities: List[str] = []

class PredictionResult(BaseModel):
    condition: str
    score: float
    explanation: str = ""

class SymptomCheckResponse(BaseModel):
    predictions: List[PredictionResult]
    model_version: str
    triage: str = ""
    confidence: float = 0.0
    recommendation_text: str = ""

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

# Helper functions for Gemini LLM integration
def get_input_hash(symptoms_text: str, age: int = None, sex: str = "") -> str:
    """Generate hash for caching identical inputs"""
    content = f"{symptoms_text}_{age}_{sex}"
    return hashlib.md5(content.encode()).hexdigest()

def load_cache() -> dict:
    """Load cache from file"""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
                # Filter out expired entries
                current_time = time.time()
                return {
                    k: v for k, v in cache_data.items() 
                    if current_time - v.get('timestamp', 0) < CACHE_DURATION.total_seconds()
                }
        except:
            pass
    return {}

def save_cache(cache_data: dict):
    """Save cache to file"""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache_data, f)
    except:
        pass

def log_request(input_hash: str, top_prediction: str, confidence: float, triage: str, model_version: str):
    """Log anonymized request data"""
    try:
        with open(LOG_FILE, 'a') as f:
            timestamp = datetime.now().isoformat()
            log_entry = f"{timestamp},{input_hash},{top_prediction},{confidence:.2f},{triage},{model_version}\n"
            f.write(log_entry)
    except:
        pass

def call_gemini_api(prompt: str) -> dict:
    """Call Gemini API with timeout and retry logic"""
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=503, detail="Gemini API key not configured")
    
    headers = {
        "Content-Type": "application/json",
    }
    
    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "topK": 32,
            "topP": 1,
            "maxOutputTokens": 1024,
        }
    }
    
    # Add API key to URL
    url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=8)
        response.raise_for_status()
        
        result = response.json()
        if 'candidates' in result and len(result['candidates']) > 0:
            content = result['candidates'][0]['content']['parts'][0]['text']
            return {"content": content, "success": True}
        else:
            return {"error": "No valid response from Gemini", "success": False}
            
    except requests.exceptions.Timeout:
        # Retry once on timeout
        try:
            response = requests.post(url, headers=headers, json=data, timeout=8)
            response.raise_for_status()
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                content = result['candidates'][0]['content']['parts'][0]['text']
                return {"content": content, "success": True}
        except:
            pass
        return {"error": "Request timeout", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}

def build_gemini_prompt(symptoms_text: str, age: int = None, sex: str = "", onset_days: int = None, severity: str = "", comorbidities: List[str] = []) -> str:
    """Build carefully designed prompt for Gemini"""
    
    context_parts = []
    if age:
        context_parts.append(f"Age: {age} years")
    if sex:
        context_parts.append(f"Sex: {sex}")
    if onset_days:
        context_parts.append(f"Symptom onset: {onset_days} days ago")
    if severity:
        context_parts.append(f"Severity: {severity}")
    if comorbidities:
        context_parts.append(f"Comorbidities: {', '.join(comorbidities)}")
    
    context = "\n".join(context_parts)
    
    prompt = f"""
You are a medical AI assistant. Analyze the following symptoms and provide a structured assessment.

PATIENT INFORMATION:
{context}

SYMPTOMS:
{symptoms_text}

TASK: Interpret these symptoms and provide a structured JSON response with:
1. Top 3 likely diagnoses with probabilities (0-1) and brief explanations
2. Triage level (emergency/urgent/non-urgent/self-care)
3. Overall confidence (0-1)
4. Recommended next steps
5. Critical red flags that require immediate attention

SAFETY INSTRUCTION: If symptoms suggest life-threatening conditions (severe chest pain, sudden weakness, severe breathing difficulty, high fever with altered mental status, severe headache with neurological symptoms), ALWAYS set triage to "emergency" and recommend immediate medical attention.

RESPONSE FORMAT (strict JSON):
{{
    "predictions": [
        {{"label": "Diagnosis 1", "probability": 0.7, "explanation": "Brief reasoning"}},
        {{"label": "Diagnosis 2", "probability": 0.2, "explanation": "Brief reasoning"}},
        {{"label": "Diagnosis 3", "probability": 0.1, "explanation": "Brief reasoning"}}
    ],
    "triage": "emergency|urgent|non-urgent|self-care",
    "confidence": 0.85,
    "recommendation_text": "Clear medical advice and next steps",
    "model_version": "gemini-llm-v1"
}}

Provide ONLY the JSON response, no additional text.
"""
    
    return prompt

def parse_gemini_response(content: str) -> dict:
    """Parse Gemini response to extract JSON"""
    try:
        # Try to extract JSON from the response
        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
        else:
            # If no JSON found, try parsing the entire content
            return json.loads(content)
    except:
        # If parsing fails, return fallback response
        return {
            "predictions": [
                {"label": "Unable to compute", "probability": 0.0, "explanation": "Could not parse AI response"}
            ],
            "triage": "refer",
            "confidence": 0.0,
            "recommendation_text": "Please consult a clinician for proper evaluation.",
            "model_version": "gemini-llm-v1"
        }

def get_fallback_response() -> dict:
    """Fallback response when API fails"""
    return {
        "predictions": [
            {"label": "Unable to compute", "probability": 0.0, "explanation": "AI service unavailable"}
        ],
        "triage": "refer",
        "confidence": 0.0,
        "recommendation_text": "Please consult a clinician for proper evaluation.",
        "model_version": "gemini-llm-v1"
    }

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
    """Predict disease based on symptoms using Gemini LLM"""
    try:
        # Validate and sanitize input
        if not request.description and not request.symptoms:
            raise HTTPException(status_code=400, detail="No symptoms provided")
        
        # Combine symptoms list and description into text
        symptoms_text = request.description or " ".join(request.symptoms)
        symptoms_text = symptoms_text.strip()[:1000]  # Limit length
        
        # Generate cache key
        cache_key = get_input_hash(symptoms_text, request.age, request.sex)
        
        # Check cache first
        cache = load_cache()
        if cache_key in cache:
            cached_result = cache[cache_key]['response']
            log_request(cache_key, 
                      cached_result.get('predictions', [{}])[0].get('label', 'unknown'),
                      cached_result.get('confidence', 0.0),
                      cached_result.get('triage', 'unknown'),
                      cached_result.get('model_version', 'unknown'))
            return SymptomCheckResponse(**cached_result)
        
        # Build prompt for Gemini
        prompt = build_gemini_prompt(
            symptoms_text=symptoms_text,
            age=request.age,
            sex=request.sex,
            onset_days=request.onset_days,
            severity=request.severity,
            comorbidities=request.comorbidities
        )
        
        # Call Gemini API
        gemini_response = call_gemini_api(prompt)
        
        if not gemini_response['success']:
            # Use fallback response
            result = get_fallback_response()
        else:
            # Parse Gemini response
            result = parse_gemini_response(gemini_response['content'])
        
        # Convert to response format
        predictions = []
        for pred in result.get('predictions', []):
            predictions.append(PredictionResult(
                condition=pred.get('label', 'Unknown'),
                score=float(pred.get('probability', 0.0)),
                explanation=pred.get('explanation', '')
            ))
        
        # Limit to top 3 predictions
        predictions = predictions[:3]
        
        # Create response
        response = SymptomCheckResponse(
            predictions=predictions,
            model_version=result.get('model_version', 'gemini-llm-v1'),
            triage=result.get('triage', 'refer'),
            confidence=float(result.get('confidence', 0.0)),
            recommendation_text=result.get('recommendation_text', 'Please consult a clinician.')
        )
        
        # Cache the response
        cache[cache_key] = {
            'response': response.dict(),
            'timestamp': time.time()
        }
        save_cache(cache)
        
        # Log the request (anonymized)
        top_prediction = predictions[0].condition if predictions else 'unknown'
        log_request(cache_key, top_prediction, response.confidence, response.triage, response.model_version)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        # Return fallback response on any error
        fallback = get_fallback_response()
        predictions = [PredictionResult(
            condition=p['label'],
            score=float(p['probability']),
            explanation=p['explanation']
        ) for p in fallback['predictions']]
        
        return SymptomCheckResponse(
            predictions=predictions,
            model_version=fallback['model_version'],
            triage=fallback['triage'],
            confidence=fallback['confidence'],
            recommendation_text=fallback['recommendation_text']
        )

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
