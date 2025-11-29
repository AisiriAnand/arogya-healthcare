from pydantic import BaseModel
from typing import List, Optional

class Hospital(BaseModel):
    id: str
    name: str
    category: str
    care_type: str
    address: str
    state: str
    district: str
    pincode: str
    telephone: str
    mobile: str
    emergency: str
    ambulance: str
    bloodbank: str
    email: str
    website: str
    specialties: List[str]
    facilities: List[str]
    latitude: float
    longitude: float
    distance_km: Optional[float] = None
    town: Optional[str] = None
    subtown: Optional[str] = None
    village: Optional[str] = None

class HospitalSearchResponse(BaseModel):
    hospitals: List[Hospital]
    total_count: int
    search_center: Optional[dict] = None
    search_radius: Optional[float] = None

class LocationSuggestion(BaseModel):
    name: str
    state: str
    district: str
    latitude: float
    longitude: float
