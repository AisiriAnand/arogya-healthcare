"""
Karnataka Hospital Data Enhancer
Provides enhanced data for Karnataka hospitals with village-level accuracy
"""

import pandas as pd
import requests
from typing import List, Dict, Optional
from .models import Hospital

class KarnatakaHospitalEnhancer:
    def __init__(self):
        self.karnataka_districts = {
            'bangalore': ['Bangalore Urban', 'Bangalore Rural'],
            'bengaluru': ['Bangalore Urban', 'Bangalore Rural'],
            'mandya': ['Mandya'],
            'kolar': ['Kolar'],
            'mysore': ['Mysore'],
            'chikballapur': ['Chikballapur'],
            'tumkur': ['Tumkur'],
            'davanagere': ['Davanagere'],
            'bellary': ['Bellary'],
            'bijapur': ['Bijapur'],
            'raichur': ['Raichur'],
            'gulbarga': ['Gulbarga'],
            'bidar': ['Bidar'],
            'hubli': ['Dharwad'],
            'dharwad': ['Dharwad'],
            'belgaum': ['Belgaum'],
            'bagalkot': ['Bagalkot'],
            'gadag': ['Gadag'],
            'haveri': ['Haveri'],
            'shivamogga': ['Shivamogga'],
            'chitradurga': ['Chitradurga'],
            'chikmagalur': ['Chikmagalur'],
            'udupi': ['Udupi'],
            'dakshina kannada': ['Dakshina Kannada'],
            'uttara kannada': ['Uttara Kannada'],
            'kodagu': ['Kodagu'],
            'hassan': ['Hassan'],
            'koppal': ['Koppal'],
            'yadgir': ['Yadgir'],
            'chamarajanagar': ['Chamarajanagar'],
            'ramanagara': ['Ramanagara']
        }
        
        # Enhanced facility types for Karnataka
        self.karnataka_facilities = {
            'district_hospital': 'District Hospital',
            'taluk_hospital': 'Taluk Hospital', 
            'chc': 'Community Health Centre',
            'phc': 'Primary Health Centre',
            'sub_centre': 'Sub Centre',
            'urban_health_centre': 'Urban Health Centre',
            'dispensary': 'Dispensary',
            'maternity_home': 'Maternity Home',
            'family_welfare_centre': 'Family Welfare Centre'
        }
    
    def enhance_karnataka_hospitals(self, hospitals: List[Hospital]) -> List[Hospital]:
        """Enhance Karnataka hospitals with more accurate data"""
        enhanced_hospitals = []
        
        for hospital in hospitals:
            if hospital.state.lower() == 'karnataka':
                # Enhance with Karnataka-specific data
                enhanced = self._enhance_single_hospital(hospital)
                enhanced_hospitals.append(enhanced)
            else:
                # Keep non-Karnataka hospitals as-is
                enhanced_hospitals.append(hospital)
        
        return enhanced_hospitals
    
    def _enhance_single_hospital(self, hospital: Hospital) -> Hospital:
        """Enhance a single Karnataka hospital with better data"""
        enhanced_data = hospital.dict()
        
        # Add facility type classification
        facility_type = self._classify_facility_type(hospital)
        enhanced_data['facility_type'] = facility_type
        
        # Add village/area information
        area_info = self._extract_area_info(hospital)
        enhanced_data['area_info'] = area_info
        
        # Add Karnataka-specific metadata
        enhanced_data['is_karnataka_enhanced'] = True
        enhanced_data['data_source'] = 'National + Karnataka Enhanced'
        
        return Hospital(**enhanced_data)
    
    def _classify_facility_type(self, hospital: Hospital) -> str:
        """Classify hospital facility type based on name and characteristics"""
        name_lower = hospital.name.lower()
        category_lower = hospital.category.lower()
        care_type_lower = hospital.care_type.lower()
        
        # District Hospital classification
        if ('district' in name_lower or 
            'district hospital' in name_lower or
            'dh ' in name_lower or
            category_lower in ['district', 'district hospital']):
            return 'District Hospital'
        
        # Taluk Hospital classification  
        if ('taluk' in name_lower or
            'taluk hospital' in name_lower or
            'th ' in name_lower or
            'taluk' in category_lower):
            return 'Taluk Hospital'
        
        # CHC classification
        if ('community health centre' in name_lower or
            'chc' in name_lower or
            'community health' in category_lower):
            return 'Community Health Centre'
        
        # PHC classification
        if ('primary health centre' in name_lower or
            'phc' in name_lower or
            'primary health' in category_lower):
            return 'Primary Health Centre'
        
        # Sub Centre classification
        if ('sub centre' in name_lower or
            'sub center' in name_lower or
            'sub-centre' in name_lower):
            return 'Sub Centre'
        
        # Urban Health Centre
        if ('urban health' in name_lower or
            'uhc' in name_lower or
            'urban' in category_lower):
            return 'Urban Health Centre'
        
        # Default classification
        if 'hospital' in care_type_lower:
            return 'General Hospital'
        elif 'clinic' in care_type_lower:
            return 'Clinic'
        elif 'dispensary' in care_type_lower:
            return 'Dispensary'
        else:
            return 'Health Facility'
    
    def _extract_area_info(self, hospital: Hospital) -> Dict:
        """Extract area/village information from hospital data"""
        area_info = {
            'village': None,
            'taluk': None,
            'district': hospital.district,
            'division': None,
            'area_type': None  # Urban/Rural
        }
        
        # Extract from address
        address_parts = hospital.address.lower().split(',')
        
        for part in address_parts:
            part_clean = part.strip()
            
            # Village detection
            if any(keyword in part_clean for keyword in ['village', 'vil.', 'post']):
                area_info['village'] = part_clean.title()
            
            # Taluk detection  
            if any(keyword in part_clean for keyword in ['taluk', 'tq.', 'tal']):
                area_info['taluk'] = part_clean.title()
        
        # Determine area type based on facility type and location
        if hospital.district.lower() in ['bangalore urban', 'bengaluru urban']:
            area_info['area_type'] = 'Urban'
        elif 'urban' in hospital.name.lower():
            area_info['area_type'] = 'Urban'
        else:
            area_info['area_type'] = 'Rural'
        
        return area_info
    
    def get_karnataka_hospital_stats(self, hospitals: List[Hospital]) -> Dict:
        """Get statistics for Karnataka hospitals"""
        karnataka_hospitals = [h for h in hospitals if h.state.lower() == 'karnataka']
        
        stats = {
            'total_hospitals': len(karnataka_hospitals),
            'by_facility_type': {},
            'by_district': {},
            'by_area_type': {'Urban': 0, 'Rural': 0}
        }
        
        for hospital in karnataka_hospitals:
            # Facility type stats
            facility_type = self._classify_facility_type(hospital)
            stats['by_facility_type'][facility_type] = stats['by_facility_type'].get(facility_type, 0) + 1
            
            # District stats
            district = hospital.district
            stats['by_district'][district] = stats['by_district'].get(district, 0) + 1
            
            # Area type stats
            area_info = self._extract_area_info(hospital)
            area_type = area_info.get('area_type', 'Unknown')
            if area_type in stats['by_area_type']:
                stats['by_area_type'][area_type] += 1
        
        return stats
    
    def search_karnataka_enhanced(self, query: str, hospitals: List[Hospital]) -> List[Hospital]:
        """Enhanced search specifically for Karnataka"""
        query_lower = query.lower()
        karnataka_hospitals = [h for h in hospitals if h.state.lower() == 'karnataka']
        results = []
        
        for hospital in karnataka_hospitals:
            # Enhanced search with facility types and area info
            facility_type = self._classify_facility_type(hospital)
            area_info = self._extract_area_info(hospital)
            
            # Match against query
            if (query_lower in hospital.name.lower() or
                query_lower in hospital.district.lower() or
                query_lower in hospital.address.lower() or
                query_lower in facility_type.lower() or
                (area_info['taluk'] and query_lower in area_info['taluk'].lower()) or
                (area_info['village'] and query_lower in area_info['village'].lower())):
                
                # Enhance hospital with additional info
                enhanced = self._enhance_single_hospital(hospital)
                results.append(enhanced)
        
        # Sort by relevance
        results.sort(key=lambda h: (
            query_lower in h.name.lower(),  # Name match first
            query_lower in h.district.lower(),  # District match
            query_lower in getattr(h, 'facility_type', '').lower(),  # Facility type match
        ), reverse=True)
        
        return results[:100]  # Return up to 100 results
