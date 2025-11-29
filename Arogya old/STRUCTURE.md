# AROGYA Healthcare - Clean Backend Structure

## 📁 Backend Organization

```
backend/
├── main.py                    # Clean main FastAPI app
├── main_old.py               # Backup of old messy implementation
├── hospital_finder/          # Hospital finder feature module
│   ├── __init__.py
│   ├── models.py            # Hospital data models
│   ├── services.py          # Hospital search services
│   └── router.py            # Hospital API routes
├── symptom_checker/          # Symptom checker feature module
│   ├── __init__.py
│   ├── models.py            # Symptom checker data models
│   ├── services.py          # Gemini LLM integration
│   └── router.py            # Symptom checker API routes
├── hospital_directory.csv   # Hospital data
└── requirements.txt          # Python dependencies
```

## 🚀 Feature Modules

### Hospital Finder Module
- **Path**: `hospital_finder/`
- **Purpose**: Interactive hospital search with 30,273+ hospitals
- **API Routes**: `/hospital/*`
- **Features**: Location search, GPS integration, category filtering

### Symptom Checker Module  
- **Path**: `symptom_checker/`
- **Purpose**: AI-powered symptom analysis using Gemini LLM
- **API Routes**: `/symptom-checker/*`
- **Features**: Triage classification, medical recommendations, caching

## 🔧 Clean Architecture Benefits

✅ **Modular Design**: Each feature in its own folder  
✅ **Separation of Concerns**: Models, services, and routes separated  
✅ **Easy Maintenance**: Clear file organization  
✅ **Scalable**: Easy to add new features  
✅ **Clean Main**: Minimal main.py with just router includes  

## 📡 API Endpoints

### Core Health
- `GET /api/health` - Backend health check

### Hospital Finder
- `GET /hospital/search` - Search hospitals by location
- `GET /hospital/search-nearby` - Find nearby hospitals
- `GET /hospital/categories` - Get hospital categories
- `GET /hospital/locations` - Location suggestions

### Symptom Checker
- `GET /symptom-checker/symptom-list` - Get common symptoms
- `POST /symptom-checker/predict` - Analyze symptoms with AI

## 🗂️ File Cleanup

### Removed Files
- `backend/main.py.bak` - Old backup (replaced with main_old.py)
- `backend/symptom_checker/` - Old ML model artifacts (187KB files)
- Mixed LLM code from main.py - Moved to dedicated module

### Added Files
- `backend/symptom_checker/` - Clean LLM module
- `backend/main_clean.py` - New clean main (renamed to main.py)
- `STRUCTURE.md` - This documentation

## 🚀 Quick Start

```bash
# Backend
cd backend
export GEMINI_API_KEY="your-key-here"  # For symptom checker
python -m uvicorn main:app --host 0.0.0.0 --port 5000 --reload

# Frontend  
cd frontend
python working_app.py
```

## 📊 Performance

- **Startup Time**: Fast (no heavy model loading)
- **Memory Usage**: Optimized (removed 187KB ML model)
- **API Response**: <100ms (cached), 6-8s (Gemini API)
- **Cache Duration**: 24 hours for symptom analysis

## 🔒 Security & Privacy

- **No PII Logging**: Only anonymized request hashes
- **Environment Variables**: API keys never in code
- **Input Validation**: Sanitized and length-limited
- **Fallback Responses**: Conservative when API unavailable

## 🔄 Adding New Features

1. Create new folder: `backend/your_feature/`
2. Add `__init__.py`, `models.py`, `services.py`, `router.py`
3. Import router in `main.py`
4. Follow the same clean pattern

This structure ensures maintainability, scalability, and clean separation of concerns!
