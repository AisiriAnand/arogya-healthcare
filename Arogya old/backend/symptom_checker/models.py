from pydantic import BaseModel
from typing import List, Optional

class SymptomCheckRequest(BaseModel):
    symptoms: List[str] = []
    description: str = ""
    age: Optional[int] = None
    sex: str = ""
    onset_days: Optional[int] = None
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
