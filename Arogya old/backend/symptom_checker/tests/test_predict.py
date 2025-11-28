"""
Tests for the symptom checker prediction endpoint
"""

import pytest
import json
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestSymptomChecker:
    """Test cases for symptom checker API endpoints"""
    
    def test_health_check(self):
        """Test the health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "Backend server is running"}
    
    def test_symptom_list_endpoint(self):
        """Test the symptom list endpoint"""
        response = client.get("/api/symptom-checker/symptom-list")
        assert response.status_code == 200
        data = response.json()
        assert "symptoms" in data
        assert isinstance(data["symptoms"], list)
    
    def test_predict_endpoint_valid_input(self):
        """Test the predict endpoint with valid input"""
        # Test with description
        response = client.post(
            "/api/symptom-checker/predict",
            json={
                "description": "itching skin rash nodal skin eruptions",
                "symptoms": []
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "predictions" in data
            assert "model_version" in data
            assert "explain" in data
            assert isinstance(data["predictions"], list)
            
            # Check prediction structure
            if data["predictions"]:
                pred = data["predictions"][0]
                assert "condition" in pred
                assert "score" in pred
                assert isinstance(pred["score"], (int, float))
                assert 0 <= pred["score"] <= 1
        else:
            # If model is not loaded, should return 503
            assert response.status_code == 503
    
    def test_predict_endpoint_symptoms_list(self):
        """Test the predict endpoint with symptoms list"""
        response = client.post(
            "/api/symptom-checker/predict",
            json={
                "symptoms": ["itching", "skin_rash"],
                "description": ""
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "predictions" in data
        else:
            assert response.status_code == 503
    
    def test_predict_endpoint_empty_input(self):
        """Test the predict endpoint with empty input"""
        response = client.post(
            "/api/symptom-checker/predict",
            json={
                "symptoms": [],
                "description": ""
            }
        )
        
        # Should handle empty input gracefully
        assert response.status_code in [200, 503, 422]
    
    def test_predict_endpoint_invalid_input(self):
        """Test the predict endpoint with invalid input"""
        response = client.post(
            "/api/symptom-checker/predict",
            json={
                "invalid_field": "test"
            }
        )
        
        # Should return validation error
        assert response.status_code == 422

if __name__ == "__main__":
    pytest.main([__file__])
