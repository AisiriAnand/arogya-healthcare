# Frontend Integration Map - Backend API Endpoints

This document maps all frontend files that need to be updated to call the new Python FastAPI backend.

## Summary

- **Total Frontend Files**: 15+ pages and components
- **Files Requiring Updates**: 12
- **API Calls to Migrate**: 8 main endpoints
- **Estimated Migration Time**: 2-3 days

---

## 1. Authentication Pages

### 1.1 Login Page (NEW - Create)
**File**: `frontend/app/auth/login/page.tsx` (NEW)

**Current State**: No login page exists

**Required Changes**:
```typescript
// NEW FILE: frontend/app/auth/login/page.tsx
import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const router = useRouter()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    })
    
    if (response.ok) {
      const data = await response.json()
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      router.push('/dashboard')
    }
  }

  return (
    // Login form UI
  )
}
```

**Backend Endpoint**: `POST /api/v1/auth/login`

---

### 1.2 Register Page (NEW - Create)
**File**: `frontend/app/auth/register/page.tsx` (NEW)

**Current State**: No registration page exists

**Required Changes**: Similar to login, call `POST /api/v1/auth/register`

**Backend Endpoint**: `POST /api/v1/auth/register`

---

## 2. Hospital Search & Discovery

### 2.1 Find Hospitals Page
**File**: `frontend/app/find-hospitals/page.tsx`

**Current Implementation** (Lines 68-79):
```typescript
const handleSearch = () => {
  setIsLoading(true)
  setTimeout(() => {
    const results = searchHospitals({
      query: searchTerm,
      state: filters.state,
      type: filters.type,
      minBeds: filters.minBeds > 0 ? filters.minBeds : undefined,
      hasEmergency: filters.hasEmergency,
      ruralUrban: filters.ruralUrban as "Rural" | "Urban" | "",
    })
    setFilteredHospitals(results.slice(0, 100))
    setIsLoading(false)
  }, 300)
}
```

**Required Changes**:
```typescript
const handleSearch = async () => {
  setIsLoading(true)
  try {
    const params = new URLSearchParams()
    if (searchTerm) params.append('query', searchTerm)
    if (filters.state) params.append('state', filters.state)
    if (filters.type) params.append('type', filters.type)
    if (filters.minBeds > 0) params.append('min_beds', filters.minBeds.toString())
    if (filters.hasEmergency) params.append('emergency_only', 'true')
    if (filters.ruralUrban) params.append('rural_urban', filters.ruralUrban)
    params.append('limit', '100')

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/v1/hospitals?${params.toString()}`,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      }
    )
    
    const data = await response.json()
    setFilteredHospitals(data.items || [])
  } catch (error) {
    console.error('Error searching hospitals:', error)
  } finally {
    setIsLoading(false)
  }
}
```

**Backend Endpoints**:
- `GET /api/v1/hospitals` - List hospitals with filters
- `GET /api/v1/hospitals/{id}` - Get hospital details

**Files to Update**:
- `frontend/app/find-hospitals/page.tsx` (lines 65-79)
- `frontend/data/hospital-service.ts` - Replace with API calls
- `frontend/services/location-service.ts` - Update getNearbyHealthcare()

---

## 3. Symptom Checker

### 3.1 Symptom Checker Page
**File**: `frontend/app/symptom-checker/page.tsx`

**Current Implementation** (Line 28):
```typescript
const predictionResult = await predictDisease(data)
```

**Required Changes**:
```typescript
const handleSubmit = async (data: PatientData) => {
  setIsLoading(true)
  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/v1/symptoms/analyze`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          symptoms: data.symptoms,
          age: data.age,
          gender: data.gender,
          duration_days: data.duration,
          blood_pressure: data.bloodPressure
        })
      }
    )
    
    const result = await response.json()
    setResult(result)
  } catch (error) {
    console.error('Error analyzing symptoms:', error)
  } finally {
    setIsLoading(false)
  }
}
```

**Backend Endpoints**:
- `POST /api/v1/symptoms/analyze` - Analyze symptoms with ML
- `GET /api/v1/symptoms/history` - Get user's symptom history

**Files to Update**:
- `frontend/app/symptom-checker/page.tsx` (line 28)
- `frontend/lib/symptomChecker.ts` - Keep local version as fallback
- `frontend/components/symptom-checker-form.tsx` - Update form submission

---

## 4. Medication Reminders

### 4.1 Medication Reminders Page
**File**: `frontend/app/medication-reminders/page.tsx`

**Current Implementation**: UI only, no backend calls

**Required Changes**:
```typescript
// Get reminders on page load
useEffect(() => {
  const fetchReminders = async () => {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/v1/reminders`,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      }
    )
    const data = await response.json()
    setReminders(data)
  }
  
  fetchReminders()
}, [])

// Create reminder
const handleCreateReminder = async (reminderData) => {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/v1/reminders`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify(reminderData)
    }
  )
  
  if (response.ok) {
    const newReminder = await response.json()
    setReminders([...reminders, newReminder])
  }
}

// Update reminder
const handleUpdateReminder = async (id, reminderData) => {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/v1/reminders/${id}`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify(reminderData)
    }
  )
  
  if (response.ok) {
    // Update local state
  }
}

// Delete reminder
const handleDeleteReminder = async (id) => {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/v1/reminders/${id}`,
    {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    }
  )
  
  if (response.ok) {
    setReminders(reminders.filter(r => r.id !== id))
  }
}
```

**Backend Endpoints**:
- `POST /api/v1/reminders` - Create reminder
- `GET /api/v1/reminders` - Get user's reminders
- `PUT /api/v1/reminders/{id}` - Update reminder
- `DELETE /api/v1/reminders/{id}` - Delete reminder

**Files to Update**:
- `frontend/app/medication-reminders/page.tsx` (entire file)

---

## 5. Appointments

### 5.1 Appointments Page (NEW - Create)
**File**: `frontend/app/appointments/page.tsx` (NEW)

**Required Changes**:
```typescript
// Get user's appointments
const fetchAppointments = async () => {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/v1/appointments`,
    {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    }
  )
  const data = await response.json()
  setAppointments(data)
}

// Book appointment
const handleBookAppointment = async (doctorId, appointmentDate, notes) => {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/v1/appointments`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify({
        doctor_id: doctorId,
        appointment_date: appointmentDate,
        notes: notes
      })
    }
  )
  
  if (response.ok) {
    const appointment = await response.json()
    setAppointments([...appointments, appointment])
  }
}

// Cancel appointment
const handleCancelAppointment = async (appointmentId) => {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/v1/appointments/${appointmentId}`,
    {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    }
  )
  
  if (response.ok) {
    setAppointments(appointments.filter(a => a.id !== appointmentId))
  }
}
```

**Backend Endpoints**:
- `POST /api/v1/appointments` - Book appointment
- `GET /api/v1/appointments` - Get user's appointments
- `GET /api/v1/appointments/{id}` - Get appointment details
- `PUT /api/v1/appointments/{id}` - Update appointment
- `DELETE /api/v1/appointments/{id}` - Cancel appointment

---

## 6. Government Schemes

### 6.1 Schemes Page
**File**: `frontend/app/schemes/page.tsx`

**Current Implementation**: Uses static data from `data/schemes-data.ts`

**Required Changes**:
```typescript
useEffect(() => {
  const fetchSchemes = async () => {
    const params = new URLSearchParams()
    if (selectedCategory) params.append('category', selectedCategory)
    if (selectedState) params.append('state', selectedState)
    
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/v1/schemes?${params.toString()}`
    )
    const data = await response.json()
    setSchemes(data.items || data)
  }
  
  fetchSchemes()
}, [selectedCategory, selectedState])
```

**Backend Endpoints**:
- `GET /api/v1/schemes` - List schemes with filters
- `GET /api/v1/schemes/{id}` - Get scheme details
- `POST /api/v1/schemes/{id}/apply` - Apply for scheme

**Files to Update**:
- `frontend/app/schemes/page.tsx` (entire file)
- `frontend/app/schemes/[id]/page.tsx` - Update scheme details page

---

## 7. Emergency SOS

### 7.1 SOS Button Component
**File**: `frontend/components/sos-button.tsx`

**Current Implementation**: UI only, no backend integration

**Required Changes**:
```typescript
const handleSOS = async () => {
  try {
    // Get user's current location
    const position = await new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject)
    })
    
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/v1/emergency/sos`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          emergency_type: emergencyType,
          description: emergencyDescription,
          emergency_contacts: emergencyContacts
        })
      }
    )
    
    if (response.ok) {
      const data = await response.json()
      // Show nearest hospital info
      showNearestHospital(data.nearest_hospital)
    }
  } catch (error) {
    console.error('Error sending SOS:', error)
  }
}
```

**Backend Endpoints**:
- `POST /api/v1/emergency/sos` - Send emergency alert

**Files to Update**:
- `frontend/components/sos-button.tsx` (entire file)

---

## 8. User Profile & Dashboard

### 8.1 Dashboard Page
**File**: `frontend/app/dashboard/page.tsx`

**Current Implementation**: Stub only

**Required Changes**:
```typescript
useEffect(() => {
  const fetchUserProfile = async () => {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/profile`,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      }
    )
    const data = await response.json()
    setUserProfile(data)
  }
  
  fetchUserProfile()
}, [])
```

**Backend Endpoints**:
- `GET /api/v1/users/profile` - Get user profile
- `PUT /api/v1/users/profile` - Update user profile

**Files to Update**:
- `frontend/app/dashboard/page.tsx` (entire file)

---

## 9. Environment Configuration

### 9.1 Create `.env.local`
**File**: `frontend/.env.local` (NEW)

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Maps
NEXT_PUBLIC_NOMINATIM_API=https://nominatim.openstreetmap.org

# Feature Flags
NEXT_PUBLIC_ENABLE_OFFLINE_MODE=true
NEXT_PUBLIC_ENABLE_ML_SYMPTOM_CHECKER=true
```

### 9.2 Create `.env.example`
**File**: `frontend/.env.example` (NEW)

```bash
# Copy this file to .env.local and update values
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_NOMINATIM_API=https://nominatim.openstreetmap.org
NEXT_PUBLIC_ENABLE_OFFLINE_MODE=true
NEXT_PUBLIC_ENABLE_ML_SYMPTOM_CHECKER=true
```

---

## 10. API Client Service

### 10.1 Create API Client Utility
**File**: `frontend/services/api-client.ts` (NEW)

```typescript
export class APIClient {
  private baseURL: string
  private accessToken: string | null = null

  constructor(baseURL: string = process.env.NEXT_PUBLIC_API_URL || '') {
    this.baseURL = baseURL
    this.accessToken = typeof window !== 'undefined' 
      ? localStorage.getItem('access_token') 
      : null
  }

  setAccessToken(token: string) {
    this.accessToken = token
    localStorage.setItem('access_token', token)
  }

  private async request(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<Response> {
    const url = `${this.baseURL}${endpoint}`
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    }

    if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`
    }

    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (response.status === 401) {
      // Handle token refresh
      await this.refreshToken()
      return this.request(endpoint, options)
    }

    return response
  }

  async get(endpoint: string) {
    const response = await this.request(endpoint, { method: 'GET' })
    return response.json()
  }

  async post(endpoint: string, data: any) {
    const response = await this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    })
    return response.json()
  }

  async put(endpoint: string, data: any) {
    const response = await this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
    return response.json()
  }

  async delete(endpoint: string) {
    const response = await this.request(endpoint, { method: 'DELETE' })
    return response.status === 204 ? null : response.json()
  }

  private async refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) return

    const response = await fetch(`${this.baseURL}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    })

    if (response.ok) {
      const data = await response.json()
      this.setAccessToken(data.access_token)
    }
  }
}

export const apiClient = new APIClient()
```

---

## 11. Migration Checklist

### Phase 1: Setup
- [ ] Create `.env.local` with `NEXT_PUBLIC_API_URL`
- [ ] Create API client service (`frontend/services/api-client.ts`)
- [ ] Create auth pages (login, register)
- [ ] Set up JWT token storage and refresh logic

### Phase 2: Core Features
- [ ] Update hospital search page
- [ ] Update symptom checker page
- [ ] Update medication reminders page
- [ ] Create appointments page

### Phase 3: Additional Features
- [ ] Update government schemes page
- [ ] Update SOS button
- [ ] Create/update dashboard
- [ ] Update user profile page

### Phase 4: Testing & Optimization
- [ ] Test all API calls
- [ ] Add error handling
- [ ] Add loading states
- [ ] Test offline functionality
- [ ] Performance optimization

---

## 12. Example API Call Patterns

### Pattern 1: Simple GET Request
```typescript
const data = await apiClient.get('/api/v1/hospitals')
```

### Pattern 2: GET with Query Parameters
```typescript
const params = new URLSearchParams({
  state: 'Karnataka',
  type: 'Government',
  limit: '20'
})
const data = await apiClient.get(`/api/v1/hospitals?${params.toString()}`)
```

### Pattern 3: POST Request
```typescript
const data = await apiClient.post('/api/v1/symptoms/analyze', {
  symptoms: ['fever', 'cough'],
  age: 30,
  gender: 'male'
})
```

### Pattern 4: Error Handling
```typescript
try {
  const data = await apiClient.get('/api/v1/hospitals')
} catch (error) {
  console.error('Error fetching hospitals:', error)
  // Show error to user
}
```

---

## 13. Testing Endpoints

### Using cURL

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Get hospitals
curl -X GET "http://localhost:8000/api/v1/hospitals?state=Karnataka" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Analyze symptoms
curl -X POST http://localhost:8000/api/v1/symptoms/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"symptoms":["fever","cough"],"age":30,"gender":"male"}'
```

### Using Postman

1. Import `API_SPEC.json` into Postman
2. Set `{{base_url}}` variable to `http://localhost:8000`
3. Get access token from login endpoint
4. Set `{{access_token}}` variable
5. Test endpoints

---

## 14. Offline Sync Strategy

When backend is available, sync queued changes:

```typescript
// frontend/services/sync-service.ts
export async function syncOfflineChanges() {
  const syncQueue = await getOfflineSyncQueue()
  
  for (const item of syncQueue) {
    try {
      const response = await apiClient.request(item.endpoint, {
        method: item.method,
        body: JSON.stringify(item.body)
      })
      
      if (response.ok) {
        await removeFromSyncQueue(item.id)
      }
    } catch (error) {
      console.error('Sync failed for:', item.endpoint)
    }
  }
}
```

---

## 15. Performance Optimization

### Caching Strategy
```typescript
// Cache hospital data for 24 hours
const cacheKey = 'hospitals_cache'
const cacheExpiry = 24 * 60 * 60 * 1000

const cachedData = localStorage.getItem(cacheKey)
if (cachedData) {
  const { data, timestamp } = JSON.parse(cachedData)
  if (Date.now() - timestamp < cacheExpiry) {
    return data
  }
}

const freshData = await apiClient.get('/api/v1/hospitals')
localStorage.setItem(cacheKey, JSON.stringify({
  data: freshData,
  timestamp: Date.now()
}))
```

---

## Summary of Changes

| File | Type | Changes | Priority |
|------|------|---------|----------|
| `frontend/app/auth/login/page.tsx` | NEW | Create login page | HIGH |
| `frontend/app/auth/register/page.tsx` | NEW | Create register page | HIGH |
| `frontend/app/find-hospitals/page.tsx` | UPDATE | Use backend API | HIGH |
| `frontend/app/symptom-checker/page.tsx` | UPDATE | Use backend ML API | HIGH |
| `frontend/app/medication-reminders/page.tsx` | UPDATE | Use backend CRUD | MEDIUM |
| `frontend/app/appointments/page.tsx` | NEW | Create appointments page | MEDIUM |
| `frontend/app/schemes/page.tsx` | UPDATE | Use backend API | MEDIUM |
| `frontend/components/sos-button.tsx` | UPDATE | Use backend SOS API | MEDIUM |
| `frontend/app/dashboard/page.tsx` | UPDATE | Use backend profile API | LOW |
| `frontend/services/api-client.ts` | NEW | Create API client | HIGH |
| `frontend/.env.local` | NEW | Environment config | HIGH |

**Total Estimated Effort**: 2-3 days for experienced developer
