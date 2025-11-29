import pandas as pd
import math
from typing import List, Optional, Tuple
from .models import Hospital, LocationSuggestion

class HospitalFinderService:
    def __init__(self):
        self.hospitals: List[Hospital] = []
        self.locations: List[LocationSuggestion] = []
        self.load_data()
    
    def load_data(self):
        """Load hospital data from CSV on startup"""
        try:
            df = pd.read_csv('hospital_directory.csv')
            
            for _, row in df.iterrows():
                # Parse coordinates
                lat, lon = self._parse_coordinates(row['Location_Coordinates'])
                
                # Parse specialties and facilities
                specialties = self._parse_list_field(row.get('Specialties', ''))
                facilities = self._parse_list_field(row.get('Facilities', ''))
                
                hospital = Hospital(
                    id=str(row['Sr_No']),
                    name=str(row['Hospital_Name']),
                    category=str(row['Hospital_Category']),
                    care_type=str(row['Hospital_Care_Type']),
                    address=str(row['Address_Original_First_Line']),
                    state=str(row['State']),
                    district=str(row['District']),
                    pincode=str(row['Pincode']),
                    telephone=str(row['Telephone']),
                    mobile=str(row['Mobile_Number']),
                    emergency=str(row['Emergency_Num']),
                    ambulance=str(row['Ambulance_Phone_No']),
                    bloodbank=str(row['Bloodbank_Phone_No']),
                    email=str(row['Hospital_Primary_Email_Id']),
                    website=str(row['Website']),
                    specialties=specialties,
                    facilities=facilities,
                    latitude=lat,
                    longitude=lon
                )
                
                self.hospitals.append(hospital)
                
                # Add to locations for search suggestions
                if row['Location'] and str(row['Location']) != '0' and str(row['Location']) != 'nan':
                    location = LocationSuggestion(
                        name=str(row['Location']),
                        state=str(row['State']),
                        district=str(row['District']),
                        latitude=lat,
                        longitude=lon
                    )
                    self.locations.append(location)
            
            print(f"Loaded {len(self.hospitals)} hospitals and {len(self.locations)} locations")
            
        except Exception as e:
            print(f"Error loading hospital data: {e}")
            self.hospitals = []
            self.locations = []
    
    def _parse_coordinates(self, coord_str: str) -> Tuple[float, float]:
        """Parse latitude, longitude from coordinate string"""
        try:
            if pd.isna(coord_str) or not coord_str or coord_str == '0':
                return 0.0, 0.0
            
            # Remove spaces and split by comma
            coords = str(coord_str).replace(' ', '').split(',')
            if len(coords) == 2:
                lat = float(coords[0])
                lon = float(coords[1])
                return lat, lon
        except:
            pass
        
        return 0.0, 0.0
    
    def _parse_list_field(self, field: str) -> List[str]:
        """Parse comma-separated fields into list"""
        if pd.isna(field) or not field or str(field) == '0':
            return []
        
        # Split by comma and clean up
        items = [item.strip() for item in str(field).split(',') if item.strip()]
        return items
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        if lat1 == 0 or lon1 == 0 or lat2 == 0 or lon2 == 0:
            return float('inf')
        
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lon/2)**2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance
    
    def search_by_radius(self, lat: float, lon: float, radius_km: float) -> List[Hospital]:
        """Search hospitals within radius of coordinates"""
        results = []
        
        for hospital in self.hospitals:
            if hospital.latitude == 0 or hospital.longitude == 0:
                continue
            
            distance = self.calculate_distance(lat, lon, hospital.latitude, hospital.longitude)
            
            if distance <= radius_km:
                hospital.distance_km = distance
                results.append(hospital)
        
        # Sort by distance
        results.sort(key=lambda h: h.distance_km if h.distance_km else float('inf'))
        return results
    
    def search_by_location_name(self, query: str) -> List[Hospital]:
        """Search hospitals by location name"""
        query = query.lower()
        results = []
        
        # Find matching locations first
        matching_locations = [
            loc for loc in self.locations 
            if query in loc.name.lower() or 
               query in loc.district.lower() or 
               query in loc.state.lower()
        ]
        
        if matching_locations:
            # Use the first matching location as center
            center = matching_locations[0]
            return self.search_by_radius(center.latitude, center.longitude, 50)  # 50km radius
        
        # If no location match, search hospital names and addresses
        for hospital in self.hospitals:
            if (query in hospital.name.lower() or 
                query in hospital.address.lower() or
                query in hospital.district.lower() or
                query in hospital.state.lower()):
                results.append(hospital)
        
        return results
    
    def filter_by_category(self, hospitals: List[Hospital], categories: List[str]) -> List[Hospital]:
        """Filter hospitals by category"""
        if not categories:
            return hospitals
        
        filtered = []
        for hospital in hospitals:
            for category in categories:
                category_lower = category.lower()
                if (category_lower in hospital.category.lower() or
                    category_lower in hospital.care_type.lower() or
                    category_lower in ' '.join(hospital.specialties).lower()):
                    filtered.append(hospital)
                    break
        
        return filtered
    
    def get_location_suggestions(self, query: str = "") -> List[LocationSuggestion]:
        """Get location suggestions for autocomplete"""
        if not query:
            # Return popular locations
            return self.locations[:20]
        
        query = query.lower()
        suggestions = [
            loc for loc in self.locations
            if query in loc.name.lower() or query in loc.district.lower()
        ]
        
        return suggestions[:10]
    
    def get_categories(self) -> List[str]:
        """Get all available hospital categories"""
        categories = set()
        for hospital in self.hospitals:
            if hospital.category and hospital.category != '0':
                categories.add(hospital.category)
            if hospital.care_type and hospital.care_type != '0':
                categories.add(hospital.care_type)
        
        return sorted(list(categories))

# Global service instance
hospital_service = HospitalFinderService()
