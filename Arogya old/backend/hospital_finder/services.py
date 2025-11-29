import pandas as pd
import math
from typing import List, Optional, Tuple
from .models import Hospital, LocationSuggestion
from .karnataka_enhancer import KarnatakaHospitalEnhancer

class HospitalFinderService:
    def __init__(self):
        self.hospitals: List[Hospital] = []
        self.locations: List[LocationSuggestion] = []
        self.karnataka_enhancer = KarnatakaHospitalEnhancer()
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
                    longitude=lon,
                    town=str(row.get('Town', '')),
                    subtown=str(row.get('Subtown', '')),
                    village=str(row.get('Village', ''))
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
            
            # Enhance Karnataka hospitals with better data
            print("Enhancing Karnataka hospitals...")
            self.hospitals = self.karnataka_enhancer.enhance_karnataka_hospitals(self.hospitals)
            karnataka_count = len([h for h in self.hospitals if h.state.lower() == 'karnataka'])
            print(f"Enhanced {karnataka_count} Karnataka hospitals with village-level data")
            
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
        """Search hospitals by location name - enhanced for Karnataka"""
        query = query.lower().strip()
        
        # Check if this is a Karnataka search
        if self._is_karnataka_search(query):
            print(f"Using enhanced Karnataka search for: {query}")
            return self.karnataka_enhancer.search_karnataka_enhanced(query, self.hospitals)
        
        # First, check if query matches any state exactly
        all_states = set()
        for hospital in self.hospitals:
            all_states.add(hospital.state.lower())
        
        if query in all_states:
            # Exact state match - return all hospitals from this state
            state_hospitals = [h for h in self.hospitals if h.state.lower() == query]
            # Sort by name for better readability
            state_hospitals.sort(key=lambda h: h.name.lower())
            return state_hospitals[:100]  # Return up to 100 hospitals for state searches
        
        # Next, try to find exact matches in hospital locations
        location_matches = []
        for hospital in self.hospitals:
            # Check if query matches hospital's location details
            if (query in hospital.name.lower() or 
                query in hospital.address.lower() or
                query in hospital.district.lower() or
                query in getattr(hospital, 'town', '').lower() or
                query in getattr(hospital, 'subtown', '').lower() or
                query in getattr(hospital, 'village', '').lower()):
                location_matches.append(hospital)
        
        if location_matches:
            # Sort by relevance and return
            location_matches.sort(key=lambda h: (
                query in h.name.lower(),  # Prioritize name matches
                query in h.district.lower(),  # Then district matches
                query in h.state.lower()  # Then state matches
            ), reverse=True)
            return location_matches[:50]  # Return top 50 results
        
        # If no direct matches, try fuzzy matching with common city names
        common_cities = {
            'bangalore': 'karnataka',
            'bengaluru': 'karnataka', 
            'mandya': 'karnataka',
            'kolar': 'karnataka',
            'agra': 'uttar pradesh',
            'delhi': 'delhi',
            'new delhi': 'delhi',
            'mumbai': 'maharashtra',
            'pune': 'maharashtra',
            'chennai': 'tamil nadu',
            'hyderabad': 'telangana',
            'kolkata': 'west bengal'
        }
        
        # Check if query matches known cities
        if query in common_cities:
            state = common_cities[query]
            state_hospitals = [h for h in self.hospitals if h.state.lower() == state]
            return state_hospitals[:50]
        
        # Fallback: return hospitals from matching state (partial match)
        state_matches = []
        for state in all_states:
            if query in state:
                state_hospitals = [h for h in self.hospitals if h.state.lower() == state]
                state_matches.extend(state_hospitals)
        
        if state_matches:
            state_matches.sort(key=lambda h: h.name.lower())
            return state_matches[:50]
        
        return []
    
    def _is_karnataka_search(self, query: str) -> bool:
        """Check if the search is related to Karnataka"""
        karnataka_keywords = [
            'karnataka', 'bangalore', 'bengaluru', 'mandya', 'kolar', 'mysore', 'mysuru',
            'chikballapur', 'tumkur', 'davanagere', 'bellary', 'bijapur', 'raichur',
            'gulbarga', 'bidar', 'hubli', 'dharwad', 'belgaum', 'bagalkot', 'gadag',
            'haveri', 'shivamogga', 'chitradurga', 'chikmagalur', 'udupi', 'dakshina kannada',
            'uttara kannada', 'kodagu', 'hassan', 'koppal', 'yadgir', 'chamarajanagar', 'ramanagara',
            'district hospital', 'taluk hospital', 'chc', 'phc', 'sub centre'
        ]
        
        return any(keyword in query for keyword in karnataka_keywords)
    
    def filter_by_category(self, hospitals: List[Hospital], categories: List[str]) -> List[Hospital]:
        """Filter hospitals by category - improved filtering for real data"""
        if not categories or (len(categories) == 1 and categories[0] == ''):
            return hospitals
        
        filtered = []
        for hospital in hospitals:
            for category in categories:
                category_lower = category.lower().strip()
                
                # Enhanced category matching for real data
                if (category_lower in str(hospital.category).lower() or
                    category_lower in str(hospital.care_type).lower() or
                    any(category_lower in specialty.lower() for specialty in hospital.specialties) or
                    category_lower in ' '.join(hospital.specialties).lower() or
                    # Common category mappings for real data
                    (category_lower == 'government' and ('public' in str(hospital.category).lower() or 'government' in str(hospital.category).lower())) or
                    (category_lower == 'private' and 'private' in str(hospital.category).lower()) or
                    (category_lower == 'multi' and ('multi' in str(hospital.category).lower() or 'multi' in str(hospital.care_type).lower())) or
                    (category_lower == 'emergency' and ('emergency' in str(hospital.facilities).lower() or 'emergency' in str(hospital.name).lower())) or
                    (category_lower == 'hospital' and 'hospital' in str(hospital.care_type).lower()) or
                    (category_lower == 'clinic' and 'clinic' in str(hospital.care_type).lower()) or
                    (category_lower == 'dispensary' and 'dispensary' in str(hospital.care_type).lower())):
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
