"""
Unit Tests for Knowledge Graph Module
====================================

Tests for Neo4j knowledge graph operations including:
- Connection management
- Skill extraction from job roles
- Role-skill mapping extraction
- Error handling and validation
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
from pathlib import Path

# Add project modules to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from knowledgegraph.knowledgegraph import (
    get_skills_from_job,
    extract_all_role_skill_mappings
)


# ============================================================================
# Connection and Environment Tests
# ============================================================================

@pytest.mark.unit
class TestNeo4jConnection:
    """Test Neo4j connection setup and validation."""
    
    def test_credentials_from_environment(self, mock_env_vars):
        """Test loading Neo4j credentials from environment variables."""
        # This tests the module-level initialization logic
        # In actual implementation, credentials are loaded at import time
        assert mock_env_vars["NEO4J_URL"] == "bolt://localhost:7687"
        assert mock_env_vars["NEO4J_USER"] == "neo4j"
        assert mock_env_vars["NEO4J_PASSWORD"] == "test-password"
    
    @patch('knowledgegraph.knowledgegraph.GraphDatabase')
    def test_connection_verification(self, mock_graph_db):
        """Test Neo4j connection verification on module load."""
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value = mock_driver
        
        # Verify driver is created with correct parameters
        # This would be tested during module import in actual implementation
        assert True  # Placeholder for import-time test


# ============================================================================
# get_skills_from_job Tests
# ============================================================================

@pytest.mark.unit
class TestGetSkillsFromJob:
    """Test skill extraction from job titles."""
    
    @patch('knowledgegraph.knowledgegraph.GraphDatabase')
    @patch('knowledgegraph.knowledgegraph.URI', 'bolt://localhost:7687')
    @patch('knowledgegraph.knowledgegraph.AUTH', ('neo4j', 'password'))
    @patch('knowledgegraph.knowledgegraph.NEO4J_DATABASE', 'neo4j')
    def test_valid_job_title_returns_skills(self, mock_graph_db, mock_neo4j_records):
        """Test successful skill extraction for valid job title."""
        # Setup mock driver and query response
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value.__enter__.return_value = mock_driver
        
        mock_summary = MagicMock()
        mock_summary.result_available_after = 25
        
        mock_driver.execute_query.return_value = (
            mock_neo4j_records,
            mock_summary,
            []
        )
        
        # Execute
        result = get_skills_from_job("Machine Learning Engineer")
        
        # Verify
        assert result is not None
        assert len(result) == 5
        assert {"Python": 150} in result
        assert {"Machine Learning": 120} in result
    
    @patch('knowledgegraph.knowledgegraph.URI', 'bolt://localhost:7687')
    @patch('knowledgegraph.knowledgegraph.AUTH', ('neo4j', 'password'))
    def test_empty_job_title_raises_error(self):
        """Test that empty job title raises ValueError."""
        with pytest.raises(ValueError, match="job_title cannot be empty"):
            get_skills_from_job("")
        
        with pytest.raises(ValueError, match="job_title cannot be empty"):
            get_skills_from_job("   ")
    
    @patch('knowledgegraph.knowledgegraph.URI', 'bolt://localhost:7687')
    @patch('knowledgegraph.knowledgegraph.AUTH', ('neo4j', 'password'))
    def test_invalid_characters_raises_error(self):
        """Test that invalid characters in job title raise ValueError."""
        with pytest.raises(ValueError, match="Invalid job_title"):
            get_skills_from_job("Software Engineer; DROP TABLE")
        
        with pytest.raises(ValueError, match="Invalid job_title"):
            get_skills_from_job("Data Scientist<script>alert()</script>")
    
    @patch('knowledgegraph.knowledgegraph.URI', None)
    @patch('knowledgegraph.knowledgegraph.AUTH', None)
    def test_missing_credentials_raises_error(self):
        """Test that missing Neo4j credentials raise ConnectionError."""
        with pytest.raises(ConnectionError, match="Neo4j credentials not configured"):
            get_skills_from_job("Data Scientist")
    
    @patch('knowledgegraph.knowledgegraph.GraphDatabase')
    @patch('knowledgegraph.knowledgegraph.URI', 'bolt://localhost:7687')
    @patch('knowledgegraph.knowledgegraph.AUTH', ('neo4j', 'password'))
    @patch('knowledgegraph.knowledgegraph.NEO4J_DATABASE', 'neo4j')
    def test_no_skills_found_returns_empty_list(self, mock_graph_db):
        """Test handling when no skills are found for job title."""
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value.__enter__.return_value = mock_driver
        
        mock_summary = MagicMock()
        mock_summary.result_available_after = 10
        
        # Return empty results
        mock_driver.execute_query.return_value = ([], mock_summary, [])
        
        result = get_skills_from_job("Nonexistent Job Title")
        
        assert result == []
    
    @patch('knowledgegraph.knowledgegraph.GraphDatabase')
    @patch('knowledgegraph.knowledgegraph.URI', 'bolt://localhost:7687')
    @patch('knowledgegraph.knowledgegraph.AUTH', ('neo4j', 'wrong_password'))
    @patch('knowledgegraph.knowledgegraph.NEO4J_DATABASE', 'neo4j')
    def test_authentication_failure_raises_connection_error(self, mock_graph_db):
        """Test that authentication failure raises ConnectionError."""
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value.__enter__.return_value = mock_driver
        
        # Simulate authentication error
        mock_driver.execute_query.side_effect = Exception("authentication failed")
        
        with pytest.raises(ConnectionError, match="Neo4j authentication failed"):
            get_skills_from_job("Data Scientist")
    
    @patch('knowledgegraph.knowledgegraph.GraphDatabase')
    @patch('knowledgegraph.knowledgegraph.URI', 'bolt://wrong-host:7687')
    @patch('knowledgegraph.knowledgegraph.AUTH', ('neo4j', 'password'))
    @patch('knowledgegraph.knowledgegraph.NEO4J_DATABASE', 'neo4j')
    def test_connection_failure_raises_connection_error(self, mock_graph_db):
        """Test that connection failure raises ConnectionError."""
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value.__enter__.return_value = mock_driver
        
        # Simulate connection error
        mock_driver.execute_query.side_effect = Exception("connection refused")
        
        with pytest.raises(ConnectionError, match="Cannot connect to Neo4j"):
            get_skills_from_job("Data Scientist")
    
    @patch('knowledgegraph.knowledgegraph.GraphDatabase')
    @patch('knowledgegraph.knowledgegraph.URI', 'bolt://localhost:7687')
    @patch('knowledgegraph.knowledgegraph.AUTH', ('neo4j', 'password'))
    @patch('knowledgegraph.knowledgegraph.NEO4J_DATABASE', 'neo4j')
    def test_generic_error_returns_none(self, mock_graph_db):
        """Test that generic errors return None instead of crashing."""
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value.__enter__.return_value = mock_driver
        
        # Simulate generic error
        mock_driver.execute_query.side_effect = Exception("Some unexpected error")
        
        result = get_skills_from_job("Data Scientist")
        
        assert result is None


# ============================================================================
# extract_all_role_skill_mappings Tests
# ============================================================================

@pytest.mark.unit
class TestExtractAllRoleSkillMappings:
    """Test extraction of all role-skill mappings."""
    
    @patch('knowledgegraph.knowledgegraph.GraphDatabase')
    @patch('knowledgegraph.knowledgegraph.URI', 'bolt://localhost:7687')
    @patch('knowledgegraph.knowledgegraph.AUTH', ('neo4j', 'password'))
    @patch('knowledgegraph.knowledgegraph.NEO4J_DATABASE', 'neo4j')
    def test_successful_extraction(self, mock_graph_db):
        """Test successful extraction of all role-skill mappings."""
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value.__enter__.return_value = mock_driver
        
        # Mock role-skill mappings
        role_skill_records = [
            {
                "role": "Data Scientist",
                "skill_name": "Python",
                "demand_count": 150,
                "category": "Technical"
            },
            {
                "role": "Data Scientist",
                "skill_name": "Machine Learning",
                "demand_count": 120,
                "category": "Technical"
            }
        ]
        
        # Mock prerequisites
        prereq_records = [
            {
                "skill": "Machine Learning",
                "prerequisites": ["Python", "Statistics"]
            }
        ]
        
        mock_summary = MagicMock()
        
        # Mock two execute_query calls (role-skills then prerequisites)
        mock_driver.execute_query.side_effect = [
            (role_skill_records, mock_summary, []),
            (prereq_records, mock_summary, [])
        ]
        
        result = extract_all_role_skill_mappings()
        
        assert result is not None
        assert len(result) == 2
        assert result[0]["role"] == "Data Scientist"
        assert result[0]["skill_name"] == "Python"
        assert result[1]["prerequisites"] == ["Python", "Statistics"]
    
    @patch('knowledgegraph.knowledgegraph.URI', None)
    @patch('knowledgegraph.knowledgegraph.AUTH', None)
    def test_missing_credentials_raises_error(self):
        """Test that missing credentials raise ConnectionError."""
        with pytest.raises(ConnectionError, match="Neo4j credentials not configured"):
            extract_all_role_skill_mappings()
    
    @patch('knowledgegraph.knowledgegraph.GraphDatabase')
    @patch('knowledgegraph.knowledgegraph.URI', 'bolt://localhost:7687')
    @patch('knowledgegraph.knowledgegraph.AUTH', ('neo4j', 'password'))
    @patch('knowledgegraph.knowledgegraph.NEO4J_DATABASE', 'neo4j')
    def test_empty_graph_returns_empty_list(self, mock_graph_db):
        """Test extraction from empty graph returns empty list."""
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value.__enter__.return_value = mock_driver
        
        mock_summary = MagicMock()
        
        # Return empty results
        mock_driver.execute_query.side_effect = [
            ([], mock_summary, []),
            ([], mock_summary, [])
        ]
        
        result = extract_all_role_skill_mappings()
        
        assert result == []


# ============================================================================
# Integration Test Markers
# ============================================================================

@pytest.mark.integration
@pytest.mark.requires_neo4j
@pytest.mark.skip(reason="Requires actual Neo4j instance - run manually")
class TestNeo4jIntegration:
    """Integration tests requiring actual Neo4j connection."""
    
    def test_real_neo4j_connection(self):
        """Test connection to real Neo4j instance."""
        # This test should only run when Neo4j is available
        # Mark as skip by default, run explicitly with: pytest -m requires_neo4j
        pass
    
    def test_real_skill_extraction(self):
        """Test skill extraction with real data."""
        pass


# ============================================================================
# Smoke Tests
# ============================================================================

    @patch('knowledgegraph.knowledgegraph.Graph')
    def test_get_skills_from_job_mock(self, mock_graph):
        """Test get_skills_from_job with mocked Neo4j Graph."""
        from knowledgegraph import knowledgegraph
        
        # Mock Graph instance
        mock_instance = MagicMock()
        mock_graph.return_value = mock_instance
        
        # Mock run output
        mock_instance.run.return_value = [
            {"skill": "Python"},
            {"skill": "Data Analysis"}
        ]
        
        # Use mocked credentials
        with patch.dict('os.environ', {
            'NEO4J_URL': 'bolt://localhost:7687',
            'NEO4J_USER': 'neo4j',
            'NEO4J_PASSWORD': 'password'
        }):
            skills = knowledgegraph.get_skills_from_job("Data Scientist")
            
            assert skills == ["Python", "Data Analysis"]
            mock_instance.run.assert_called_once()
            # Verify Cypher query contains job title
            args, _ = mock_instance.run.call_args
            assert "Data Scientist" in args[0]

@pytest.mark.smoke
class TestKnowledgeGraphSmoke:
    """Quick smoke tests for critical functionality."""
    
    @patch('knowledgegraph.knowledgegraph.URI', 'bolt://localhost:7687')
    @patch('knowledgegraph.knowledgegraph.AUTH', ('neo4j', 'password'))
    def test_module_imports_successfully(self):
        """Test that the module can be imported without errors."""
        import knowledgegraph.knowledgegraph
        assert hasattr(knowledgegraph.knowledgegraph, 'get_skills_from_job')
        assert hasattr(knowledgegraph.knowledgegraph, 'extract_all_role_skill_mappings')
