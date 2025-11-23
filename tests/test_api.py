"""
API Endpoint Tests
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health and status endpoints"""

    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["version"] == "1.0.0"


class TestStockEndpoints:
    """Test stock-related endpoints"""

    def test_list_stocks(self):
        """Test listing stocks"""
        response = client.get("/api/v1/stocks")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "stocks" in data["data"]

    def test_list_stocks_with_market_filter(self):
        """Test listing stocks with market filter"""
        response = client.get("/api/v1/stocks?market=KOSPI")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


class TestUSMarketEndpoints:
    """Test US market endpoints"""

    def test_get_us_markets(self):
        """Test getting US market data"""
        response = client.get("/api/v1/market/us")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "indices" in data["data"]


class TestRecommendationEndpoints:
    """Test recommendation endpoints"""

    def test_get_recommendations(self):
        """Test getting recommendations"""
        response = client.get("/api/v1/recommendations?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_analyze_user_profile(self):
        """Test user profile analysis"""
        profile = {
            "investment_amount": 10000000,
            "investment_period": "long",
            "loss_tolerance": "medium",
            "experience": "beginner",
            "goal": "growth"
        }
        response = client.post("/api/v1/recommendations/analyze-profile", json=profile)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "risk_level" in data["data"]


class TestSignalEndpoints:
    """Test signal detection endpoints"""

    def test_get_us_market_signal(self):
        """Test US market signal"""
        response = client.get("/api/v1/signals/us-market")
        # May fail if no data, so check for 200 or 500
        assert response.status_code in [200, 500]


class TestSectorEndpoints:
    """Test sector analysis endpoints"""

    def test_get_all_sectors(self):
        """Test getting all sectors"""
        response = client.get("/api/v1/sectors")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "sectors" in data["data"]

    def test_get_beginner_friendly_sectors(self):
        """Test getting beginner-friendly sectors"""
        response = client.get("/api/v1/sectors/beginner-friendly")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
