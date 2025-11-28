# AROGYA Quick Start Guide

## 📚 Read These First (In Order)
1. **PROJECT_SUMMARY.md** - Overview (5 min)
2. **ARCHITECTURE.md** - System design (15 min)
3. **API_SPEC.json** - All endpoints (10 min)
4. **FRONTEND_INTEGRATION_MAP.md** - Frontend integration (10 min)

## 🚀 Local Development Setup

### Docker (Recommended)
```bash
git clone <repo>
cd arogya
docker-compose up -d
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

### Manual Setup
```bash
cd backend-python
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

## 📋 Implementation Priority

**Week 1**: Auth (register, login, refresh)
**Week 2**: Hospitals & Doctors (list, filter, details)
**Week 3**: Appointments (CRUD)
**Week 4-5**: ML Symptom Analysis
**Week 6**: Reminders & Schemes
**Week 7**: Emergency SOS

## 🗄️ Key Database Tables
- users (id, email, password_hash, full_name, age, gender, blood_group)
- hospitals (id, name, type, latitude, longitude, address, phone, emergency_services)
- doctors (id, hospital_id, name, specialty, experience, rating)
- appointments (id, user_id, doctor_id, appointment_date, status)
- symptom_analyses (id, user_id, symptoms, predicted_conditions, severity)
- medication_reminders (id, user_id, medication_name, dosage, frequency)
- schemes (id, name, description, category, eligibility_criteria)

## 🔐 Auth Flow
```
User Login → Validate → Return JWT tokens → Frontend stores → Include in all requests
```

## 🧪 Test Endpoint
```bash
# Login
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}' \
  | jq -r '.access_token')

# Get hospitals
curl -X GET http://localhost:8000/api/v1/hospitals \
  -H "Authorization: Bearer $TOKEN"
```

## 📊 Project Structure
```
backend-python/
├── app/
│   ├── main.py
│   ├── models/          (SQLAlchemy)
│   ├── schemas/         (Pydantic)
│   ├── routes/          (API endpoints)
│   ├── services/        (Business logic)
│   ├── ml/              (ML models)
│   └── utils/           (Helpers)
├── requirements.txt
└── .env.example
```

## 🤖 ML Symptom Analysis
Input: symptoms, age, gender, duration → Model predicts conditions with confidence scores

## 🔄 Offline-First
- Cache data to IndexedDB
- Queue changes when offline
- Sync when reconnected

## 🐛 Common Issues
- **ModuleNotFoundError**: Activate venv and cd to backend-python
- **Connection refused**: Run `docker-compose up -d postgres redis`
- **JWT fails**: Check JWT_SECRET in .env
- **CORS errors**: Add frontend URL to CORS config
- **ML model not found**: Run `python app/ml/train_model.py`

## ✅ Next Steps
1. Review ARCHITECTURE.md
2. Set up local dev environment
3. Start with auth endpoints
4. Test with Postman
5. Integrate with frontend one page at a time
