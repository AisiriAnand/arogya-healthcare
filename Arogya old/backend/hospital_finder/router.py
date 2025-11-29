from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from .services import hospital_service
from .models import Hospital, HospitalSearchResponse, LocationSuggestion

router = APIRouter(prefix="/hospital", tags=["hospital"])

@router.get("/karnataka-stats")
async def get_karnataka_stats():
    """Get Karnataka hospital statistics and facility breakdown"""
    try:
        stats = hospital_service.karnataka_enhancer.get_karnataka_hospital_stats(hospital_service.hospitals)
        return {
            "success": True,
            "data": stats,
            "message": "Karnataka hospital statistics retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search-location", response_model=List[Hospital])
async def search_by_location(
    q: str = Query(..., description="Location name to search")
):
    """Search hospitals by location name (city, district, state)"""
    try:
        hospitals = hospital_service.search_by_location_name(q)
        return hospitals
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search-nearby", response_model=HospitalSearchResponse)
async def search_nearby(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    radius_km: float = Query(default=5.0, description="Search radius in kilometers"),
    category: Optional[str] = Query(default=None, description="Filter by category")
):
    """Search hospitals within radius of coordinates"""
    try:
        hospitals = hospital_service.search_by_radius(lat, lon, radius_km)
        
        # Apply category filter if provided
        if category:
            hospitals = hospital_service.filter_by_category(hospitals, [category])
        
        return HospitalSearchResponse(
            hospitals=hospitals,
            total_count=len(hospitals),
            search_center={"lat": lat, "lon": lon},
            search_radius=radius_km
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_model=HospitalSearchResponse)
async def search_hospitals(
    q: Optional[str] = Query(default=None, description="Search query"),
    lat: Optional[float] = Query(default=None, description="Latitude for nearby search"),
    lon: Optional[float] = Query(default=None, description="Longitude for nearby search"),
    radius_km: float = Query(default=10.0, description="Search radius in kilometers"),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    emergency_only: bool = Query(default=False, description="Show only emergency hospitals")
):
    """Advanced hospital search with multiple filters"""
    try:
        hospitals = []
        
        if lat and lon:
            # Nearby search
            hospitals = hospital_service.search_by_radius(lat, lon, radius_km)
        elif q:
            # Location name search
            hospitals = hospital_service.search_by_location_name(q)
        else:
            # Return all hospitals (limited)
            hospitals = hospital_service.hospitals[:100]
        
        # Apply filters
        if category:
            hospitals = hospital_service.filter_by_category(hospitals, [category])
        
        if emergency_only:
            hospitals = [h for h in hospitals if h.emergency and h.emergency != '0']
        
        return HospitalSearchResponse(
            hospitals=hospitals,
            total_count=len(hospitals),
            search_center={"lat": lat, "lon": lon} if lat and lon else None,
            search_radius=radius_km if lat and lon else None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/locations", response_model=List[LocationSuggestion])
async def get_location_suggestions(
    q: str = Query(default="", description="Query for location suggestions")
):
    """Get location suggestions for autocomplete"""
    try:
        return hospital_service.get_location_suggestions(q)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories", response_model=List[str])
async def get_categories():
    """Get all available hospital categories"""
    try:
        return hospital_service.get_categories()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{hospital_id}", response_model=Hospital)
async def get_hospital_details(hospital_id: str):
    """Get detailed information about a specific hospital"""
    try:
        for hospital in hospital_service.hospitals:
            if hospital.id == hospital_id:
                return hospital
        
        raise HTTPException(status_code=404, detail="Hospital not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=dict)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "total_hospitals": len(hospital_service.hospitals),
        "total_locations": len(hospital_service.locations)
    }
