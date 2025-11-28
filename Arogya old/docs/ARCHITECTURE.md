# AROGYA Healthcare Platform - Architecture & Migration Guide

## Executive Summary

**Current State**: Frontend-heavy Next.js application with minimal Express.js backend
**Target State**: Production-ready system with Python FastAPI backend, PostgreSQL database, ML-powered symptom analysis, and offline-first capabilities

---

## 1. Recommended Architecture

### 1.1 System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js 16)                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  React Components + TypeScript                           │   │
│  │  - Hospital Finder                                       │   │
│  │  - Symptom Checker                                       │   │
│  │  - Medication Reminders                                  │   │
│  │  - Government Schemes                                    │   │
│  │  - Health Articles                                       │   │
│  │  - SOS Emergency                                         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↓                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Offline-First Storage (IndexedDB + LocalStorage)        │   │
│  │  - Cached hospital data                                  │   │
│  │  - Symptom analysis history                              │   │
│  │  - User preferences                                      │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │   API Gateway / Load Balancer           │
        │   (Nginx or AWS ALB)                    │
        └─────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI + Python)                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Authentication & Authorization                          │   │
│  │  - JWT token management                                  │   │
│  │  - OAuth2 integration (optional)                         │   │
│  │  - Role-based access control                             │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  API Routes (RESTful + WebSocket)                        │   │
│  │  - /api/v1/auth/*                                        │   │
│  │  - /api/v1/users/*                                       │   │
│  │  - /api/v1/hospitals/*                                   │   │
│  │  - /api/v1/doctors/*                                     │   │
│  │  - /api/v1/appointments/*                                │   │
│  │  - /api/v1/symptoms/*                                    │   │
│  │  - /api/v1/reminders/*                                   │   │
│  │  - /api/v1/schemes/*                                     │   │
│  │  - /api/v1/emergency/*                                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Business Logic Layer                                    │   │
│  │  - User management                                       │   │
│  │  - Hospital search & filtering                           │   │
│  │  - Appointment booking                                   │   │
│  │  - Notification dispatch                                 │   │
│  │  - Emergency routing                                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  ML Services                                             │   │
│  │  - Symptom analysis model (scikit-learn / TensorFlow)    │   │
│  │  - Model serving (TorchServe / TensorFlow Serving)       │   │
│  │  - Prediction caching                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Data Access Layer (SQLAlchemy ORM)                      │   │
│  │  - User models                                           │   │
│  │  - Hospital models                                       │   │
│  │  - Appointment models                                    │   │
│  │  - Medical history models                                │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │         Data Layer                      │
        ├─────────────────────────────────────────┤
        │  PostgreSQL (Primary Database)          │
        │  - User accounts & profiles             │
        │  - Hospital & doctor data               │
        │  - Appointments & reminders             │
        │  - Medical history                      │
        │  - Audit logs                           │
        ├─────────────────────────────────────────┤
        │  Redis (Cache & Sessions)               │
        │  - User sessions                        │
        │  - API response cache                   │
        │  - Rate limiting                        │
        │  - Real-time notifications              │
        ├─────────────────────────────────────────┤
        │  Elasticsearch (Search)                 │
        │  - Hospital search index                │
        │  - Doctor search index                  │
        │  - Full-text search                     │
        └─────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │    External Services                    │
        ├─────────────────────────────────────────┤
        │  SMS Gateway (Twilio)                   │
        │  - Appointment reminders                │
        │  - Emergency alerts                     │
        ├─────────────────────────────────────────┤
        │  Email Service (SendGrid)               │
        │  - Notifications                        │
        │  - Reports                              │
        ├─────────────────────────────────────────┤
        │  Maps API (Google Maps / Mapbox)        │
        │  - Hospital location display            │
        │  - Route optimization                   │
        ├─────────────────────────────────────────┤
        │  Payment Gateway (Razorpay)             │
        │  - Consultation fees                    │
        │  - Scheme applications                  │
        └─────────────────────────────────────────┘
```

### 1.2 Technology Stack

#### Frontend
- **Framework**: Next.js 16.0.5 (App Router)
- **Language**: TypeScript 5
- **UI**: React 19 + Radix UI + Tailwind CSS
- **State Management**: React Context API
- **Forms**: React Hook Form + Zod validation
- **Offline**: IndexedDB + LocalStorage
- **Maps**: Leaflet (online) + Fallback static maps (offline)
- **Animations**: Framer Motion
- **Build**: Next.js built-in (Webpack 5)

#### Backend
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.11+
- **ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+
- **Search**: Elasticsearch 8+ (optional, for large deployments)
- **Authentication**: JWT + OAuth2
- **API Documentation**: OpenAPI/Swagger (auto-generated)
- **Async**: AsyncIO + Uvicorn
- **Task Queue**: Celery + Redis (for async jobs)
- **ML**: scikit-learn / TensorFlow / PyTorch

#### DevOps & Deployment
- **Containerization**: Docker + Docker Compose
- **Orchestration**: Kubernetes (optional, for scaling)
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **APM**: Sentry (error tracking)

---

## 2. Offline-First Architecture

### 2.1 Offline Capabilities

The application is designed to work seamlessly in low-connectivity rural environments:

#### Data Synchronization Strategy
```
┌─────────────────────────────────────────┐
│  Online Mode                            │
│  - Fetch latest data from backend       │
│  - Cache to IndexedDB                   │
│  - Sync local changes to server         │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  Offline Mode                           │
│  - Use cached data from IndexedDB       │
│  - Queue local changes                  │
│  - Show offline indicator               │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  Reconnection                           │
│  - Detect online status                 │
│  - Sync queued changes                  │
│  - Merge conflicts (server wins)        │
│  - Update local cache                   │
└─────────────────────────────────────────┘
```

#### Offline-Available Features
- ✅ Symptom checker (local ML model)
- ✅ Hospital search (cached data)
- ✅ Government schemes (cached data)
- ✅ Health articles (cached data)
- ✅ Medication reminders (local storage)
- ✅ Medical history (cached)
- ❌ Real-time appointments (requires sync)
- ❌ Emergency SOS (requires connectivity)

### 2.2 Storage Strategy

```javascript
// IndexedDB Schema
{
  hospitals: {
    keyPath: 'id',
    indexes: ['state', 'type', 'latitude', 'longitude']
  },
  doctors: {
    keyPath: 'id',
    indexes: ['specialty', 'hospital_id']
  },
  symptoms: {
    keyPath: 'id',
    indexes: ['user_id', 'created_at']
  },
  reminders: {
    keyPath: 'id',
    indexes: ['user_id', 'next_due']
  },
  schemes: {
    keyPath: 'id',
    indexes: ['category', 'state']
  },
  sync_queue: {
    keyPath: 'id',
    indexes: ['endpoint', 'status', 'created_at']
  }
}
```

---

## 3. Real-Time Architecture

### 3.1 WebSocket Integration

For real-time features like appointment confirmations and emergency alerts:

```python
# Backend (FastAPI)
from fastapi import WebSocket

@app.websocket("/ws/notifications/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages
    finally:
        manager.disconnect(user_id)
```

### 3.2 Notification Types
- **Appointment Reminders**: 24h, 1h, 15m before
- **Emergency Alerts**: Real-time SOS notifications
- **Medication Reminders**: Scheduled push notifications
- **System Updates**: New schemes, health alerts

---

## 4. Security Architecture

### 4.1 Authentication Flow

```
┌──────────────┐
│   Frontend   │
└──────┬───────┘
       │ POST /auth/login
       ↓
┌──────────────────────────────────────┐
│  Backend Authentication Service      │
│  1. Validate credentials             │
│  2. Generate JWT tokens              │
│  3. Store refresh token in Redis     │
└──────┬───────────────────────────────┘
       │ Return access_token + refresh_token
       ↓
┌──────────────┐
│   Frontend   │
│  Store JWT   │
│  in Memory   │
└──────────────┘
```

### 4.2 Authorization

- **JWT Tokens**: Access (15min) + Refresh (7 days)
- **Scopes**: user, doctor, admin, emergency_responder
- **RBAC**: Role-based access control
- **CORS**: Configured for frontend domain
- **Rate Limiting**: 100 req/min per user, 1000 req/min per IP

### 4.3 Data Protection

- **Encryption**: TLS 1.3 for all API calls
- **Hashing**: bcrypt for passwords (cost factor: 12)
- **Sensitive Data**: PII encrypted at rest (AES-256)
- **Audit Logs**: All user actions logged
- **HIPAA Compliance**: Medical data handling per HIPAA standards

---

## 5. Database Schema Overview

### 5.1 Core Tables

```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    age INT,
    gender VARCHAR(10),
    blood_group VARCHAR(5),
    medical_history JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Hospitals
CREATE TABLE hospitals (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50), -- Government, Private, NGO
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    address TEXT,
    phone VARCHAR(20),
    emergency_services BOOLEAN,
    bed_capacity INT,
    specialties JSONB,
    rating DECIMAL(3, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Doctors
CREATE TABLE doctors (
    id UUID PRIMARY KEY,
    hospital_id UUID REFERENCES hospitals(id),
    name VARCHAR(255) NOT NULL,
    specialty VARCHAR(100),
    experience INT,
    rating DECIMAL(3, 2),
    consultation_fee INT,
    available_slots JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Appointments
CREATE TABLE appointments (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    doctor_id UUID REFERENCES doctors(id),
    hospital_id UUID REFERENCES hospitals(id),
    appointment_date TIMESTAMP NOT NULL,
    status VARCHAR(50), -- scheduled, completed, cancelled
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Symptom Analysis
CREATE TABLE symptom_analyses (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    symptoms JSONB NOT NULL,
    predicted_conditions JSONB,
    severity VARCHAR(20),
    recommended_action VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Medication Reminders
CREATE TABLE medication_reminders (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    medication_name VARCHAR(255),
    dosage VARCHAR(100),
    frequency VARCHAR(50),
    reminder_times JSONB,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Government Schemes
CREATE TABLE schemes (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    eligibility_criteria JSONB,
    benefits JSONB,
    application_process TEXT,
    state_specific BOOLEAN,
    states JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- User Scheme Applications
CREATE TABLE scheme_applications (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    scheme_id UUID REFERENCES schemes(id),
    status VARCHAR(50), -- eligible, applied, approved, rejected
    application_date TIMESTAMP,
    documents JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 6. ML Symptom Analysis Architecture

### 6.1 Model Pipeline

```
┌─────────────────────────────────────────┐
│  Training Pipeline (Offline)            │
│  1. Data collection & preprocessing     │
│  2. Feature engineering                 │
│  3. Model training (scikit-learn)       │
│  4. Cross-validation & evaluation       │
│  5. Model serialization (joblib)        │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  Model Serving (FastAPI)                │
│  1. Load model on startup               │
│  2. Cache predictions (Redis)           │
│  3. Serve via REST API                  │
│  4. Log predictions for monitoring      │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  Frontend Integration                   │
│  1. Send symptoms to backend            │
│  2. Receive predictions                 │
│  3. Display results with confidence     │
│  4. Store in local cache                │
└─────────────────────────────────────────┘
```

### 6.2 Model Specifications

- **Algorithm**: Random Forest / Gradient Boosting
- **Input Features**: 
  - Symptoms (one-hot encoded)
  - Age (normalized)
  - Gender (categorical)
  - Duration (days)
  - Blood pressure (if available)
- **Output**: 
  - Top 3 predicted conditions
  - Confidence scores
  - Severity level
  - Recommended action
- **Performance Target**: 
  - Accuracy: >85%
  - Precision: >80%
  - Recall: >75%

### 6.3 Model Updates

- **Retraining**: Monthly (with new data)
- **A/B Testing**: 10% traffic on new model
- **Rollback**: Automatic if accuracy drops >2%
- **Monitoring**: Prometheus metrics for model performance

---

## 7. API Versioning & Evolution

### 7.1 Versioning Strategy

```
/api/v1/  - Current stable version
/api/v2/  - Next major version (when ready)
```

### 7.2 Backward Compatibility

- Deprecation warnings in API responses
- 6-month notice before removing endpoints
- Migration guides for breaking changes

---

## 8. Monitoring & Observability

### 8.1 Metrics

```
Frontend:
- Page load time
- API response time
- Error rate
- Offline usage percentage
- Cache hit rate

Backend:
- Request latency (p50, p95, p99)
- Error rate by endpoint
- Database query time
- Cache hit rate
- ML model inference time
- Queue depth (Celery)
```

### 8.2 Logging

```
Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

Structured logging format:
{
  "timestamp": "2025-11-27T10:00:00Z",
  "level": "INFO",
  "service": "backend",
  "endpoint": "POST /api/v1/symptoms/analyze",
  "user_id": "uuid",
  "duration_ms": 245,
  "status": 200,
  "message": "Symptom analysis completed"
}
```

---

## 9. Deployment Architecture

### 9.1 Development Environment

```
docker-compose.yml:
- frontend: Next.js dev server (port 3000)
- backend: FastAPI dev server (port 8000)
- postgres: PostgreSQL (port 5432)
- redis: Redis (port 6379)
```

### 9.2 Production Environment

```
AWS / GCP / Azure:
- Frontend: CloudFront + S3 (CDN)
- Backend: ECS/EKS + ALB (load balanced)
- Database: RDS PostgreSQL (multi-AZ)
- Cache: ElastiCache Redis (cluster mode)
- Search: Elasticsearch Service
- Monitoring: CloudWatch + Datadog
```

### 9.3 Scaling Strategy

- **Frontend**: Static site generation + CDN caching
- **Backend**: Horizontal scaling with load balancer
- **Database**: Read replicas + connection pooling
- **Cache**: Redis cluster mode
- **ML**: Separate inference service with auto-scaling

---

## 10. Migration Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [ ] Set up FastAPI project structure
- [ ] Create PostgreSQL schema
- [ ] Implement authentication (JWT)
- [ ] Set up Redis
- [ ] Create Docker Compose for local dev

### Phase 2: Core APIs (Weeks 3-4)
- [ ] Implement user management endpoints
- [ ] Implement hospital search endpoints
- [ ] Implement appointment booking
- [ ] Implement medication reminders

### Phase 3: ML Integration (Weeks 5-6)
- [ ] Train symptom analysis model
- [ ] Implement ML serving endpoint
- [ ] Integrate with frontend
- [ ] Set up model monitoring

### Phase 4: Advanced Features (Weeks 7-8)
- [ ] Implement real-time notifications (WebSocket)
- [ ] Implement emergency SOS routing
- [ ] Implement offline sync
- [ ] Implement payment integration

### Phase 5: Production Ready (Weeks 9-10)
- [ ] Set up CI/CD pipeline
- [ ] Configure production deployment
- [ ] Load testing & optimization
- [ ] Security audit
- [ ] Documentation & training

---

## 11. Reasons for Architecture Choices

### Why FastAPI?
- ✅ High performance (async/await)
- ✅ Automatic OpenAPI documentation
- ✅ Built-in data validation (Pydantic)
- ✅ Easy to learn and maintain
- ✅ Great for microservices

### Why PostgreSQL?
- ✅ ACID compliance for healthcare data
- ✅ JSONB support for flexible schemas
- ✅ Full-text search capabilities
- ✅ Excellent for relational data
- ✅ Strong community support

### Why Redis?
- ✅ Ultra-fast caching
- ✅ Session management
- ✅ Real-time notifications
- ✅ Rate limiting
- ✅ Task queue (Celery)

### Why Offline-First?
- ✅ Works in rural areas with poor connectivity
- ✅ Better user experience
- ✅ Reduced server load
- ✅ Complies with rural healthcare requirements

### Why ML on Backend?
- ✅ Consistent predictions across clients
- ✅ Easy to update models without app release
- ✅ Better security (model not exposed)
- ✅ Can use larger models
- ✅ Easier monitoring and A/B testing

---

## 12. Next Steps

1. **Review this architecture** with team
2. **Set up development environment** (Docker Compose)
3. **Create database schema** in PostgreSQL
4. **Implement authentication** (JWT)
5. **Build core APIs** (hospitals, appointments, symptoms)
6. **Integrate with frontend** (update API calls)
7. **Deploy to staging** for testing
8. **Production launch** with monitoring

---

## References

- FastAPI Documentation: https://fastapi.tiangolo.com/
- SQLAlchemy ORM: https://docs.sqlalchemy.org/
- PostgreSQL: https://www.postgresql.org/docs/
- Redis: https://redis.io/documentation
- Next.js: https://nextjs.org/docs
- HIPAA Compliance: https://www.hhs.gov/hipaa/
