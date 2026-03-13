import pytest
from fastapi.testclient import TestClient
from src.app import app

# Create test client
client = TestClient(app)

# Test data for isolation
ORIGINAL_ACTIVITIES = {
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
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
    },
    "Basketball Club": {
        "description": "Practice basketball skills and play in tournaments",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["noah@mergington.edu", "ava@mergington.edu"]
    },
    "Art Workshop": {
        "description": "Explore painting, drawing, and sculpture techniques",
        "schedule": "Mondays, 4:00 PM - 5:30 PM",
        "max_participants": 16,
        "participants": ["liam@mergington.edu", "isabella@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce school plays and performances",
        "schedule": "Fridays, 3:30 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["elijah@mergington.edu", "charlotte@mergington.edu"]
    },
    "Math Olympiad": {
        "description": "Prepare for math competitions and solve challenging problems",
        "schedule": "Thursdays, 4:00 PM - 5:00 PM",
        "max_participants": 10,
        "participants": ["benjamin@mergington.edu", "amelia@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments and explore scientific concepts",
        "schedule": "Wednesdays, 4:00 PM - 5:00 PM",
        "max_participants": 14,
        "participants": ["henry@mergington.edu", "grace@mergington.edu"]
    }
}

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state before each test"""
    from src.app import activities
    activities.clear()
    activities.update(ORIGINAL_ACTIVITIES.copy())

class TestActivitiesAPI:
    """Test suite for the activities API endpoints"""

    def test_get_activities(self):
        """Test retrieving all activities"""
        # Arrange - No special setup needed
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9  # All activities present
        
        # Check structure of one activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_signup_success(self):
        """Test successful signup"""
        # Arrange
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        
        # Verify participant was added (additional assertion)
        response = client.get("/activities")
        activities = response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_duplicate(self):
        """Test signing up for the same activity twice"""
        # Arrange
        email = "dupstudent@mergington.edu"
        activity_name = "Chess Club"
        
        # Act - First signup (should succeed)
        response1 = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert first signup
        assert response1.status_code == 200
        
        # Act - Second signup (should fail)
        response2 = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert second signup fails
        assert response2.status_code == 400
        
        data = response2.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]

    def test_signup_invalid_activity(self):
        """Test signing up for non-existent activity"""
        # Arrange
        email = "test@mergington.edu"
        invalid_activity = "NonExistent"
        
        # Act
        response = client.post(f"/activities/{invalid_activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_delete_success(self):
        """Test successful participant removal"""
        # Arrange
        email = "removeme@mergington.edu"
        activity_name = "Chess Club"
        
        # Pre-condition: Add the participant first
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
        
        # Verify participant was removed (additional assertion)
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities[activity_name]["participants"]

    def test_delete_not_signed_up(self):
        """Test deleting a participant who isn't signed up"""
        # Arrange
        email = "nosignup@mergington.edu"
        activity_name = "Chess Club"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"]

    def test_delete_invalid_activity(self):
        """Test deleting from non-existent activity"""
        # Arrange
        email = "test@mergington.edu"
        invalid_activity = "NonExistent"
        
        # Act
        response = client.delete(f"/activities/{invalid_activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_root_redirect(self):
        """Test root endpoint redirects to static index"""
        # Arrange - No special setup needed
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307  # Temporary redirect
        
        assert response.headers["location"] == "/static/index.html"