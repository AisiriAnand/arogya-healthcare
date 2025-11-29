from fastapi import APIRouter, HTTPException
from .models import SymptomCheckRequest, SymptomCheckResponse, PredictionResult
from .services import symptom_service

router = APIRouter(prefix="/symptom-checker", tags=["symptom-checker"])

@router.get("/symptom-list")
async def get_symptom_list():
    """Get list of common symptoms for UI"""
    return {
        "symptoms": [
            "itching", "skin_rash", "nodal_skin_eruptions", "continuous_sneezing", "shivering", "chills",
            "watering_from_eyes", "stomach_pain", "acidity", "ulcers_on_tongue", "vomiting", "cough",
            "chest_pain", "yellowish_skin", "nausea", "loss_of_appetite", "abdominal_pain", "yellowing_of_eyes",
            "burning_micturition", "spotting_urination", "passage_of_gases", "internal_itching", "indigestion",
            "muscle_wasting", "patches_in_throat", "high_fever", "slurred_speech", "knee_pain", "hip_joint_pain",
            "muscle_weakness", "stiff_neck", "swelling_joints", "movement_stiffness", "spinning_movements",
            "loss_of_balance", "unsteadiness", "weakness_of_one_body_side", "loss_of_smell", "bladder_discomfort",
            "foul_smell_of_urine", "continuous_feel_of_urine", "fatigue", "weight_loss", "lethargy", "giddiness",
            "diarrhoea", "mild_fever", "yellow_urine", "blood_in_sputum", "phlegm", "throat_irritation",
            "redness_of_eyes", "sinus_pressure", "runny_nose", "congestion", "headache", "dizziness", "weakness"
        ]
    }

@router.post("/predict", response_model=SymptomCheckResponse)
async def predict_disease(request: SymptomCheckRequest):
    """Analyze symptoms using Gemini LLM"""
    try:
        # Validate input
        if not request.description and not request.symptoms:
            raise HTTPException(status_code=400, detail="No symptoms provided")
        
        # Combine symptoms
        symptoms_text = request.description or " ".join(request.symptoms)
        symptoms_text = symptoms_text.strip()[:1000]  # Limit length
        
        # Get analysis from service
        result = symptom_service.analyze_symptoms(
            symptoms_text=symptoms_text,
            age=request.age,
            sex=request.sex,
            onset_days=request.onset_days,
            severity=request.severity,
            comorbidities=request.comorbidities
        )
        
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
        
        return SymptomCheckResponse(
            predictions=predictions,
            model_version=result.get('model_version', 'gemini-llm-v1'),
            triage=result.get('triage', 'refer'),
            confidence=float(result.get('confidence', 0.0)),
            recommendation_text=result.get('recommendation_text', 'Please consult a clinician.')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Return fallback response on any error
        fallback = symptom_service._get_fallback_response()
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
