import os
import json
import hashlib
import requests
import time
from datetime import timedelta, datetime
from pathlib import Path
from typing import Dict, List, Any

# Environment configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_API_URL = os.getenv("GEMINI_API_URL", "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent")

# Cache configuration
CACHE_FILE = Path("symptom_cache.json")
CACHE_DURATION = timedelta(hours=24)

# Logging
LOG_FILE = Path("symptom_requests.log")

class SymptomCheckerService:
    def __init__(self):
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load cache from file"""
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, 'r') as f:
                    cache_data = json.load(f)
                    current_time = time.time()
                    return {
                        k: v for k, v in cache_data.items() 
                        if current_time - v.get('timestamp', 0) < CACHE_DURATION.total_seconds()
                    }
            except:
                pass
        return {}
    
    def _save_cache(self, cache_data: Dict):
        """Save cache to file"""
        try:
            with open(CACHE_FILE, 'w') as f:
                json.dump(cache_data, f)
        except:
            pass
    
    def _log_request(self, input_hash: str, top_prediction: str, confidence: float, triage: str, model_version: str):
        """Log anonymized request data"""
        try:
            with open(LOG_FILE, 'a') as f:
                timestamp = datetime.now().isoformat()
                log_entry = f"{timestamp},{input_hash},{top_prediction},{confidence:.2f},{triage},{model_version}\n"
                f.write(log_entry)
        except:
            pass
    
    def _get_input_hash(self, symptoms_text: str, age: int = None, sex: str = "") -> str:
        """Generate hash for caching identical inputs"""
        content = f"{symptoms_text}_{age}_{sex}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _call_gemini_api(self, prompt: str) -> Dict:
        """Call Gemini API with timeout and retry logic"""
        if not GEMINI_API_KEY:
            return {"error": "Gemini API key not configured", "success": False}
        
        headers = {"Content-Type": "application/json"}
        
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "topK": 32,
                "topP": 1,
                "maxOutputTokens": 1024,
            }
        }
        
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
    
    def _build_prompt(self, symptoms_text: str, age: int = None, sex: str = "", onset_days: int = None, severity: str = "", comorbidities: List[str] = []) -> str:
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
    
    def _parse_response(self, content: str) -> Dict:
        """Parse Gemini response to extract JSON"""
        try:
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                return json.loads(content)
        except:
            return {
                "predictions": [
                    {"label": "Unable to compute", "probability": 0.0, "explanation": "Could not parse AI response"}
                ],
                "triage": "refer",
                "confidence": 0.0,
                "recommendation_text": "Please consult a clinician for proper evaluation.",
                "model_version": "gemini-llm-v1"
            }
    
    def _get_fallback_response(self) -> Dict:
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
    
    def analyze_symptoms(self, symptoms_text: str, age: int = None, sex: str = "", onset_days: int = None, severity: str = "", comorbidities: List[str] = []) -> Dict:
        """Main symptom analysis function"""
        
        # Generate cache key
        cache_key = self._get_input_hash(symptoms_text, age, sex)
        
        # Check cache first
        if cache_key in self.cache:
            cached_result = self.cache[cache_key]['response']
            self._log_request(cache_key, 
                            cached_result.get('predictions', [{}])[0].get('label', 'unknown'),
                            cached_result.get('confidence', 0.0),
                            cached_result.get('triage', 'unknown'),
                            cached_result.get('model_version', 'unknown'))
            return cached_result
        
        # Build prompt and call API
        prompt = self._build_prompt(symptoms_text, age, sex, onset_days, severity, comorbidities)
        gemini_response = self._call_gemini_api(prompt)
        
        if not gemini_response['success']:
            result = self._get_fallback_response()
        else:
            result = self._parse_response(gemini_response['content'])
        
        # Cache the response
        self.cache[cache_key] = {
            'response': result,
            'timestamp': time.time()
        }
        self._save_cache(self.cache)
        
        # Log the request
        top_prediction = result.get('predictions', [{}])[0].get('label', 'unknown')
        self._log_request(cache_key, top_prediction, result.get('confidence', 0.0), result.get('triage', 'unknown'), result.get('model_version', 'unknown'))
        
        return result

# Global service instance
symptom_service = SymptomCheckerService()
