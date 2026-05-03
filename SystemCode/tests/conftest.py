"""
Shared Test Fixtures and Configuration
======================================

This module provides pytest fixtures and utilities shared across all tests.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, List, Any

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# ============================================================================
# Environment & Configuration Fixtures
# ============================================================================

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    env_vars = {
        "OPENAI_API_KEY": "test-openai-key-12345",
        "NEO4J_URL": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "test-password",
        "NEO4J_DATABASE": "neo4j",
        "LLM_MODEL": "gpt-3.5-turbo",
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars


@pytest.fixture
def mock_databricks_env(monkeypatch):
    """Mock Databricks environment variables."""
    env_vars = {
        "DATABRICKS_HOST": "https://test.cloud.databricks.com",
        "DATABRICKS_CLIENT_ID": "test-client-id",
        "DATABRICKS_CLIENT_SECRET": "test-client-secret",
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars


# ============================================================================
# Neo4j Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_neo4j_driver():
    """Mock Neo4j GraphDatabase driver."""
    driver = MagicMock()
    
    # Mock successful connection verification
    driver.verify_connectivity.return_value = None
    
    # Mock session context manager
    session = MagicMock()
    driver.__enter__ = Mock(return_value=driver)
    driver.__exit__ = Mock(return_value=False)
    
    return driver


@pytest.fixture
def mock_neo4j_records():
    """Mock Neo4j query results."""
    return [
        {"s.skill_name": "Python", "skill_count": 150},
        {"s.skill_name": "Machine Learning", "skill_count": 120},
        {"s.skill_name": "SQL", "skill_count": 100},
        {"s.skill_name": "Docker", "skill_count": 80},
        {"s.skill_name": "AWS", "skill_count": 75},
    ]


@pytest.fixture
def mock_neo4j_summary():
    """Mock Neo4j query summary."""
    summary = MagicMock()
    summary.result_available_after = 25  # milliseconds
    return summary


# ============================================================================
# OpenAI Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for LLM interactions."""
    client = MagicMock()
    
    # Mock chat completions
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"name": "Test User", "summary": "Test summary", "location": "Singapore"}'
    
    client.chat.completions.create.return_value = mock_response
    
    return client


@pytest.fixture
def mock_llm_response():
    """Mock LLM JSON response."""
    return {
        "message": "I understand you're currently a Software Engineer. What role are you aiming for?",
        "suggestions": ["Data Scientist", "ML Engineer", "Backend Developer"],
        "collected": {
            "cv_role": "Software Engineer",
            "target_role": None,
            "budget": None,
            "time_commit": None
        }
    }


# ============================================================================
# Data Fixtures
# ============================================================================

@pytest.fixture
def sample_cv_text():
    """Sample CV text for testing."""
    return """
    John Doe
    Software Engineer
    Singapore
    
    EXPERIENCE:
    - 3 years as Software Engineer at Tech Corp
    - Proficient in Python, SQL, and AWS
    - Led team of 5 developers
    
    EDUCATION:
    - B.Sc. Computer Science, NUS
    
    SKILLS:
    Python, SQL, JavaScript, Docker, AWS, Git
    """


@pytest.fixture
def sample_job_description():
    """Sample job description for testing."""
    return {
        "role": "Machine Learning Engineer",
        "skills": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "AWS"],
        "experience_years": 3,
        "industry": "FinTech"
    }


@pytest.fixture
def sample_user_profile():
    """Sample user profile for testing."""
    return {
        "user_id": "test_user_001",
        "current_role": "Software Engineer",
        "target_role": "Machine Learning Engineer",
        "current_skills": ["Python", "SQL", "Git"],
        "budget": 3000.0,
        "available_hours_per_week": 10.0,
        "skillsfuture_eligible": True
    }


@pytest.fixture
def sample_skill_gaps():
    """Sample skill gaps for testing."""
    return [
        {
            "skill": "Machine Learning",
            "priority": "critical",
            "gap_weight": 0.75,
            "user_skill_proficiency": 0.1,
            "demand_score": 0.85,
            "peer_score": 0.88,
            "graph_distance": 2
        },
        {
            "skill": "Deep Learning",
            "priority": "high",
            "gap_weight": 0.65,
            "user_skill_proficiency": 0.0,
            "demand_score": 0.80,
            "peer_score": 0.82,
            "graph_distance": 3
        }
    ]


@pytest.fixture
def sample_courses():
    """Sample course catalog for testing."""
    return [
        {
            "course_id": "ML-101",
            "title": "Machine Learning Fundamentals",
            "provider": "NUS-ISS",
            "duration_weeks": 8,
            "cost": 1200.0,
            "subsidy_rate": 0.7,
            "modality": "online",
            "schedule": "evening",
            "skills_covered": ["Machine Learning", "Python"],
            "rating": 4.5,
            "enrollment_count": 500
        },
        {
            "course_id": "DL-201",
            "title": "Deep Learning Specialization",
            "provider": "Coursera",
            "duration_weeks": 12,
            "cost": 2500.0,
            "subsidy_rate": 0.5,
            "modality": "online",
            "schedule": "flexible",
            "skills_covered": ["Deep Learning", "TensorFlow"],
            "rating": 4.8,
            "enrollment_count": 1250
        }
    ]


# ============================================================================
# File System Fixtures
# ============================================================================

@pytest.fixture
def temp_cv_file(tmp_path):
    """Create a temporary CV file for testing."""
    cv_file = tmp_path / "test_cv.pdf"
    cv_file.write_text("Mock CV content")
    return cv_file


@pytest.fixture
def temp_json_output(tmp_path):
    """Create a temporary JSON output file for testing."""
    json_file = tmp_path / "test_output.json"
    return json_file


# ============================================================================
# Database Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_spark_session():
    """Mock PySpark session for Databricks testing."""
    spark = MagicMock()
    
    # Mock DataFrame operations
    mock_df = MagicMock()
    mock_df.count.return_value = 100
    mock_df.collect.return_value = []
    
    spark.read.table.return_value = mock_df
    spark.sql.return_value = mock_df
    
    return spark


@pytest.fixture
def mock_delta_table():
    """Mock Delta table for Databricks testing."""
    delta_table = MagicMock()
    delta_table.toDF.return_value = MagicMock()
    return delta_table


# ============================================================================
# Test Markers and Configuration
# ============================================================================

def pytest_configure(config):
    """Configure custom test markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "requires_neo4j: mark test as requiring Neo4j connection"
    )
    config.addinivalue_line(
        "markers", "requires_databricks: mark test as requiring Databricks"
    )
    config.addinivalue_line(
        "markers", "requires_openai: mark test as requiring OpenAI API"
    )


# ============================================================================
# Test Utilities
# ============================================================================

class MockResponse:
    """Mock HTTP response object."""
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
    
    def json(self):
        return self.json_data


@pytest.fixture
def mock_requests_get(monkeypatch):
    """Mock requests.get for API testing."""
    def mock_get(*args, **kwargs):
        return MockResponse({"status": "ok"}, 200)
    
    monkeypatch.setattr("requests.get", mock_get)
    return mock_get
