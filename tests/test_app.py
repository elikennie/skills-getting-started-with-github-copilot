"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities database before each test"""
    # Store original activities
    from app import activities
    
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Competitive and recreational soccer practices and matches",
            "schedule": "Mondays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 18,
            "participants": ["liam@mergington.edu", "ava@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Drills, pickup games, and intramural competitions",
            "schedule": "Wednesdays and Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["noah@mergington.edu", "mia@mergington.edu"]
        },
        "Art Club": {
            "description": "Drawing, painting, and mixed media projects",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Choir and instrumental rehearsals; performances throughout the year",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["charlotte@mergington.edu", "ethan@mergington.edu"]
        },
        "Debate Team": {
            "description": "Practice public speaking, argumentation, and compete in tournaments",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["amelia@mergington.edu", "mason@mergington.edu"]
        },
        "Science Club": {
            "description": "Hands-on experiments, science fairs, and exploration of STEM topics",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["oliver@mergington.edu", "harper@mergington.edu"]
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_dict(self):
        """Test that get_activities returns a dictionary"""
        response = client.get("/activities")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
    
    def test_get_activities_contains_all_activities(self):
        """Test that all expected activities are returned"""
        response = client.get("/activities")
        activities_data = response.json()
        
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Soccer Team",
            "Basketball Club", "Art Club", "Music Ensemble", "Debate Team",
            "Science Club"
        ]
        
        for activity in expected_activities:
            assert activity in activities_data
    
    def test_get_activities_structure(self):
        """Test that activity structure has expected fields"""
        response = client.get("/activities")
        activities_data = response.json()
        
        for activity_name, activity_details in activities_data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert "newstudent@mergington.edu" in response.json()["message"]
    
    def test_signup_adds_participant(self):
        """Test that signup actually adds the participant"""
        email = "test@mergington.edu"
        
        # Signup
        response = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]
    
    def test_signup_duplicate_student(self):
        """Test that duplicate signups are rejected"""
        email = "michael@mergington.edu"  # Already signed up for Chess Club
        
        response = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity(self):
        """Test that signup fails for non-existent activity"""
        response = client.post(
            "/activities/Fake Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_signup_multiple_activities(self):
        """Test that a student can signup for multiple activities"""
        email = "versatile@mergington.edu"
        
        # Signup for Chess Club
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Signup for Programming Class
        response2 = client.post(
            f"/activities/Programming Class/signup?email={email}"
        )
        assert response2.status_code == 200
        
        # Verify both signups
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]
        assert email in activities_data["Programming Class"]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successful(self):
        """Test successful unregistration from an activity"""
        email = "michael@mergington.edu"  # Already signed up for Chess Club
        
        response = client.delete(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
    
    def test_unregister_removes_participant(self):
        """Test that unregister actually removes the participant"""
        email = "michael@mergington.edu"
        
        # Unregister
        response = client.delete(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_not_registered_student(self):
        """Test that unregistering a non-registered student fails"""
        email = "notregistered@mergington.edu"
        
        response = client.delete(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_nonexistent_activity(self):
        """Test that unregister fails for non-existent activity"""
        response = client.delete(
            "/activities/Fake Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_signup_and_unregister(self):
        """Test signup followed by unregister"""
        email = "testuser@mergington.edu"
        
        # Signup
        signup_response = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data["Chess Club"]["participants"]


class TestIntegration:
    """Integration tests for the API"""
    
    def test_root_redirects_to_static(self):
        """Test that root endpoint redirects to static files"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
    
    def test_activity_availability_tracking(self):
        """Test that activity availability is correctly tracked"""
        response = client.get("/activities")
        activities_data = response.json()
        
        chess_club = activities_data["Chess Club"]
        initial_spots = chess_club["max_participants"] - len(chess_club["participants"])
        
        # Signup a new student
        client.post("/activities/Chess Club/signup?email=new@mergington.edu")
        
        # Check updated availability
        response = client.get("/activities")
        activities_data = response.json()
        chess_club = activities_data["Chess Club"]
        new_spots = chess_club["max_participants"] - len(chess_club["participants"])
        
        assert new_spots == initial_spots - 1
