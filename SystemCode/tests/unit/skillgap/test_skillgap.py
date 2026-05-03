"""
Unit Tests for Skill Gap Analysis Module
========================================

Tests for skill gap identification, prioritization, and analysis including:
- Embedding generation and caching
- User profile loading
- Knowledge graph data loading
- Skill similarity calculations
- Gap prioritization logic
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add project modules to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


# ============================================================================
# Embedding Tests
# ============================================================================

@pytest.mark.unit
class TestEmbedding:
    """Test embedding generation and caching."""
    
    @patch('skillgap.skillgap.embedder')
    def test_get_embedding_generates_new(self, mock_embedder):
        """Test that new embeddings are generated for unseen text."""
        from skillgap import skillgap
        
        # Clear cache
        skillgap._embedding_cache.clear()
        
        # Mock embedder
        mock_embedding = np.array([[0.1, 0.2, 0.3]])
        mock_embedder.encode.return_value = mock_embedding
        
        result = skillgap.get_embedding("Python")
        
        # Verify embedder was called
        mock_embedder.encode.assert_called_once_with(["python"])
        np.testing.assert_array_equal(result, mock_embedding)
    
    @patch('skillgap.skillgap.embedder')
    def test_get_embedding_uses_cache(self, mock_embedder):
        """Test that cached embeddings are reused."""
        from skillgap import skillgap
        
        # Pre-populate cache
        cached_embedding = np.array([[0.5, 0.6, 0.7]])
        skillgap._embedding_cache["python"] = cached_embedding
        
        result = skillgap.get_embedding("Python")
        
        # Verify embedder was NOT called (cache hit)
        mock_embedder.encode.assert_not_called()
        np.testing.assert_array_equal(result, cached_embedding)
    
    @patch('skillgap.skillgap.embedder')
    def test_get_embedding_case_insensitive(self, mock_embedder):
        """Test that embedding keys are case-insensitive."""
        from skillgap import skillgap
        
        skillgap._embedding_cache.clear()
        mock_embedding = np.array([[0.1, 0.2, 0.3]])
        mock_embedder.encode.return_value = mock_embedding
        
        # First call
        result1 = skillgap.get_embedding("PYTHON")
        # Second call with different case should use cache
        result2 = skillgap.get_embedding("python")
        
        # Should only call encode once
        assert mock_embedder.encode.call_count == 1
        np.testing.assert_array_equal(result1, result2)

    @patch('skillgap.skillgap.embedder', None)
    def test_get_embedding_fallback_when_no_embedder(self):
        """Test that get_embedding returns zeros when embedder is not available."""
        from skillgap import skillgap

        # Clear cache to ensure fallback is triggered
        skillgap._embedding_cache.clear()

        result = skillgap.get_embedding("test skill")

        # Should return zeros array with standard MiniLM-L6-v2 size (384)
        expected = np.zeros(384)
        np.testing.assert_array_equal(result, expected)
        assert result.shape == (384,)

    def test_get_embedding_dict_input_with_skill_key(self):
        """Test get_embedding with dict input containing 'skill' key."""
        from skillgap import skillgap

        # Clear cache
        skillgap._embedding_cache.clear()

        # Mock embedder
        mock_embedding = np.array([[0.1, 0.2, 0.3]])
        with patch('skillgap.skillgap.embedder') as mock_embedder:
            mock_embedder.encode.return_value = mock_embedding

            result = skillgap.get_embedding({"skill": "Python"})

            # Should extract 'skill' value and encode it
            mock_embedder.encode.assert_called_once_with(["python"])
            np.testing.assert_array_equal(result, mock_embedding)

    def test_get_embedding_dict_input_without_skill_key(self):
        """Test get_embedding with dict input missing 'skill' key."""
        from skillgap import skillgap

        # Clear cache
        skillgap._embedding_cache.clear()

        # Mock embedder
        mock_embedding = np.array([[0.1, 0.2, 0.3]])
        with patch('skillgap.skillgap.embedder') as mock_embedder:
            mock_embedder.encode.return_value = mock_embedding

            result = skillgap.get_embedding({"name": "Python", "level": "beginner"})

            # Should convert dict to string and encode it
            mock_embedder.encode.assert_called_once()
            args = mock_embedder.encode.call_args[0][0]
            assert len(args) == 1
            # The dict gets converted to string and lowercased
            assert "python" in args[0] and "beginner" in args[0]

    def test_get_embedding_non_string_input(self):
        """Test get_embedding with non-string input (int, float, etc.)."""
        from skillgap import skillgap

        # Clear cache
        skillgap._embedding_cache.clear()

        # Mock embedder
        mock_embedding = np.array([[0.1, 0.2, 0.3]])
        with patch('skillgap.skillgap.embedder') as mock_embedder:
            mock_embedder.encode.return_value = mock_embedding

            result = skillgap.get_embedding(123)

            # Should convert to string and encode
            mock_embedder.encode.assert_called_once_with(["123"])
            np.testing.assert_array_equal(result, mock_embedding)


# ============================================================================
# User Profile Loading Tests
# ============================================================================

@pytest.mark.unit
class TestLoadUserProfile:
    """Test user profile loading from various sources."""
    
    @patch('skillgap.skillgap.IN_DATABRICKS', False)
    def test_load_user_profile_fallback(self):
        """Test fallback when not in Databricks environment."""
        from skillgap import skillgap
        
        profile = skillgap.load_user_profile("test_user_001")
        
        assert profile["user_id"] == "test_user_001"
        assert profile["user_skills"] == []
        assert profile["target_roles"] == []
        assert profile["budget"] == 2000.0
        assert profile["weekly_hours"] == 8.0
        assert profile["modality"] == "hybrid"
    
    @patch('skillgap.skillgap.IN_DATABRICKS', True)
    @patch('skillgap.skillgap.execute_sql_query')
    def test_load_user_profile_from_table_success(self, mock_execute):
        """Test successful loading of user profile from Databricks table."""
        from skillgap import skillgap
        
        # Mock DataFrame with user profile data
        mock_df = pd.DataFrame([{
            "user_id": "test_user_001",
            "user_skills": ["Python", "SQL"],
            "target_roles": ["Data Scientist"],
            "budget": 3000.0,
            "weekly_hours": 10.0,
            "modality": "online"
        }])
        
        mock_execute.return_value = mock_df

        profile = skillgap.load_user_profile("test_user_001")
        
        assert profile["user_id"] == "test_user_001"
        assert profile["user_skills"] == ["Python", "SQL"]
        assert profile["target_roles"] == ["Data Scientist"]
        assert profile["budget"] == 3000.0
        assert profile["weekly_hours"] == 10.0
        assert profile["modality"] == "online"
    
    @patch('skillgap.skillgap.IN_DATABRICKS', True)
    @patch('skillgap.skillgap.execute_sql_query')
    def test_load_user_profile_empty_result(self, mock_execute):
        """Test fallback when profile not found in table."""
        from skillgap import skillgap
        
        # Mock empty DataFrame
        mock_df = pd.DataFrame()
        mock_execute.return_value = mock_df

        profile = skillgap.load_user_profile("nonexistent_user")
        
        # Should return fallback profile
        assert profile["user_id"] == "nonexistent_user"
        assert profile["user_skills"] == []
        assert profile["budget"] == 2000.0
    
    @patch('skillgap.skillgap.IN_DATABRICKS', True)
    @patch('skillgap.skillgap.execute_sql_query')
    def test_load_user_profile_handles_null_values(self, mock_execute):
        """Test handling of null values in profile data."""
        from skillgap import skillgap
        
        # Mock DataFrame with null values
        mock_df = pd.DataFrame([{
            "user_id": "test_user_001",
            "user_skills": ["Python"],
            "target_roles": ["Data Scientist"],
            "budget": None,
            "weekly_hours": None,
            "modality": None
        }])
        
        mock_execute.return_value = mock_df

        profile = skillgap.load_user_profile("test_user_001")
        
        # Should use default values for nulls
        assert profile["budget"] == 2000.0
        assert profile["weekly_hours"] == 8.0
        assert profile["modality"] == "hybrid"


# ============================================================================
# Knowledge Graph Loading Tests
# ============================================================================

@pytest.mark.unit
class TestLoadKGOutput:
    """Test knowledge graph output loading."""
    
    @patch('skillgap.skillgap.IN_DATABRICKS', False)
    @patch('skillgap.skillgap.find_similar_roles_in_kg')
    def test_load_kg_output_fallback(self, mock_find_similar):
        """Test fallback when not in Databricks."""
        from skillgap import skillgap
        
        # Mock no similar roles found
        mock_find_similar.return_value = []

        kg_data = skillgap.load_kg_output_for_role("NonExistentRole")

        # Should return empty DataFrame with correct schema
        assert isinstance(kg_data, pd.DataFrame)
        assert len(kg_data) == 0
    
    @patch('skillgap.skillgap.IN_DATABRICKS', True)
    @patch('skillgap.skillgap.execute_sql_query')
    def test_load_kg_output_success(self, mock_execute):
        """Test successful loading from knowledge graph table."""
        from skillgap import skillgap
        
        # Mock KG data
        mock_df = pd.DataFrame([
            {
                "skill_name": "Python",
                "demand_count": 150,
                "category": "Technical",
                "prerequisites": []
            },
            {
                "skill_name": "Machine Learning",
                "demand_count": 120,
                "category": "Technical",
                "prerequisites": ["Python"]
            }
        ])
        
        mock_execute.return_value = mock_df

        kg_data = skillgap.load_kg_output_for_role("Data Scientist")
        
        assert len(kg_data) == 2
        assert kg_data.iloc[0]["skill_name"] == "Python"
        assert kg_data.iloc[0]["demand_count"] == 150


# ============================================================================
# Similarity Calculation Tests
# ============================================================================

@pytest.mark.unit
class TestSimilarityCalculations:
    """Test skill similarity calculations."""
    
    def test_cosine_similarity_identical_skills(self):
        """Test that identical skills have similarity of 1.0."""
        # Mock embeddings (identical)
        embedding1 = np.array([[1.0, 0.0, 0.0]])
        embedding2 = np.array([[1.0, 0.0, 0.0]])
        
        from sklearn.metrics.pairwise import cosine_similarity
        similarity = cosine_similarity(embedding1, embedding2)[0][0]
        
        assert similarity == pytest.approx(1.0, abs=0.001)
    
    def test_cosine_similarity_orthogonal_skills(self):
        """Test that orthogonal skills have similarity of 0.0."""
        embedding1 = np.array([[1.0, 0.0, 0.0]])
        embedding2 = np.array([[0.0, 1.0, 0.0]])
        
        from sklearn.metrics.pairwise import cosine_similarity
        similarity = cosine_similarity(embedding1, embedding2)[0][0]
        
        assert similarity == pytest.approx(0.0, abs=0.001)


# ============================================================================
# Gap Prioritization Tests
# ============================================================================

class TestNormalization:
    """Test skill list normalization."""
    
    def test_normalize_skill_list_string(self):
        from skillgap import skillgap
        result = skillgap.normalize_skill_list("Python, Java; SQL")
        assert "Python" in result
        assert "Java" in result
        assert "SQL" in result
        assert len(result) == 3

    def test_normalize_skill_list_list(self):
        from skillgap import skillgap
        result = skillgap.normalize_skill_list(["Python", "Java"])
        assert result == ["Python", "Java"]

    def test_normalize_skill_list_dict(self):
        from skillgap import skillgap
        # Test list of dicts with 'skill' key
        result = skillgap.normalize_skill_list([{"skill": "Python"}, {"skill": "Java"}])
        assert result == ["Python", "Java"]

    def test_normalize_skill_list_empty(self):
        from skillgap import skillgap
        assert skillgap.normalize_skill_list("") == []
        assert skillgap.normalize_skill_list(None) == []

    def test_normalize_skill_list_list_of_dicts_unknown_keys(self):
        """Test normalize_skill_list with list of dicts having unknown keys."""
        from skillgap import skillgap
        result = skillgap.normalize_skill_list([{"name": "Python"}, {"title": "Java"}])
        assert "Python" in result
        assert "Java" in result
        assert len(result) == 2

    def test_normalize_skill_list_numpy_array(self):
        """Test normalize_skill_list with numpy array input."""
        from skillgap import skillgap
        import numpy as np
        result = skillgap.normalize_skill_list(np.array(["Python", "SQL"]))
        assert result == ["Python", "SQL"]

    def test_normalize_skill_list_mixed_list(self):
        """Test normalize_skill_list with mixed types in list."""
        from skillgap import skillgap
        result = skillgap.normalize_skill_list(["Python", 123, {"skill": "Java"}])
        assert "Python" in result
        # Mixed types should be converted to strings
        assert "123" in result  # 123 becomes "123"
        assert "Java" in result  # dict with 'skill' key gets extracted

    def test_normalize_skill_list_unknown_type(self):
        """Test normalize_skill_list with unknown input type."""
        from skillgap import skillgap
        result = skillgap.normalize_skill_list(set(["Python", "SQL"]))
        assert result == []  # Unknown type returns empty list

    def test_normalize_skill_list_dict_values(self):
        """Test normalize_skill_list with dict input (extracts keys)."""
        from skillgap import skillgap
        result = skillgap.normalize_skill_list({"Python": "beginner", "SQL": "intermediate"})
        assert "Python" in result
        assert "SQL" in result
        assert len(result) == 2

@pytest.mark.unit
class TestGapPrioritization:
    """Test skill gap prioritization logic."""
    
    def test_gap_weight_calculation(self):
        """Test gap weight calculation formula."""
        # Gap weight = 1.0 - max_similarity
        max_similarity = 0.3
        expected_gap_weight = 1.0 - max_similarity
        
        assert expected_gap_weight == pytest.approx(0.7, abs=0.001)
    
    def test_priority_score_calculation(self):
        """Test priority score calculation (arbiter formula)."""
        # Priority = 0.45*demand + 0.35*peer + 0.20*distance
        demand_score = 0.85
        peer_score = 0.80
        distance_score = 0.70
        
        expected_priority = (0.45 * demand_score + 
                           0.35 * peer_score + 
                           0.20 * distance_score)
        
        assert expected_priority == pytest.approx(0.8025, abs=0.001)

class TestSkillFiltering:
    """Test filtering of user declared skills."""
    
    @patch('skillgap.skillgap.get_embedding')
    def test_filter_user_declared_skills(self, mock_get_embedding):
        from skillgap import skillgap
        
        # Mock embeddings
        # "Python" and "Python Programming" should be similar
        def side_effect(text):
            if "Python" in text: return np.array([[1.0, 0.0]])
            if "Java" in text: return np.array([[0.0, 1.0]])
            return np.array([[0.5, 0.5]])
            
        mock_get_embedding.side_effect = side_effect
        
        gaps_list = [
            {"skill": "Python Programming", "priority_score": 0.9},
            {"skill": "Cloud Computing", "priority_score": 0.8}
        ]
        user_declared_skills = ["Python"]
        
        # Filter with threshold 0.85
        result = skillgap.filter_user_declared_skills(
            gaps_list, user_declared_skills, similarity_threshold=0.85
        )
        
        filtered_gaps = result['filtered_gaps']
        removed = result['removed_gaps']

        # "Python Programming" should be removed because it's similar to "Python"
        assert len(filtered_gaps) == 1
        assert filtered_gaps[0]["skill"] == "Cloud Computing"
        assert len(removed) == 1
        assert removed[0]["skill"] == "Python Programming"


# ============================================================================
# Integration Test Markers
# ============================================================================

@pytest.mark.integration
@pytest.mark.requires_databricks
@pytest.mark.skip(reason="Requires Databricks connection - run manually")
class TestSkillGapIntegration:
    """Integration tests requiring Databricks."""
    
    def test_end_to_end_gap_analysis(self):
        """Test complete skill gap analysis pipeline."""
        pass


# ============================================================================
# Smoke Tests
# ============================================================================

@pytest.mark.smoke
class TestSkillGapSmoke:
    """Quick smoke tests for critical functionality."""
    
    def test_module_imports_successfully(self):
        """Test that the module can be imported."""
        import skillgap.skillgap
        assert hasattr(skillgap.skillgap, 'get_embedding')
        assert hasattr(skillgap.skillgap, 'load_user_profile')
        assert hasattr(skillgap.skillgap, 'load_kg_output_for_role')
    
    def test_embedding_cache_exists(self):
        """Test that embedding cache is initialized."""
        from skillgap import skillgap
        assert hasattr(skillgap, '_embedding_cache')
        assert isinstance(skillgap._embedding_cache, dict)

# ============================================================================
# Processing Pipeline Tests
# ============================================================================

class TestProcessingPipeline:
    """Test the main processing pipeline functions."""

    @patch('skillgap.skillgap.load_user_profile')
    @patch('skillgap.skillgap.load_kg_output_for_role')
    @patch('skillgap.skillgap.load_jd_demand_scores')
    @patch('skillgap.skillgap.load_peer_data')
    @patch('skillgap.skillgap.build_knowledge_graph')
    @patch('skillgap.skillgap.find_skill_gaps')
    @patch('skillgap.skillgap.arbitrate_skill_gaps')
    @patch('skillgap.skillgap.filter_user_declared_skills')
    @patch('skillgap.skillgap.build_json_output')
    @patch('skillgap.skillgap.write_single_role_to_delta')
    @patch('skillgap.skillgap.update_user_profile_skills')
    def test_process_single_user_direct_input_mode(self, mock_update, mock_write, mock_build_json,
                                                  mock_filter, mock_arbitrate, mock_find_gaps,
                                                  mock_build_graph, mock_load_peer, mock_load_jd,
                                                  mock_load_kg, mock_load_profile):
        """Test process_single_user with direct input (Streamlit mode)."""
        from skillgap import skillgap

        # Mock all the dependencies
        mock_load_profile.return_value = {
            "user_id": "test_user",
            "user_skills": ["Python"],
            "target_roles": ["Data Scientist"]
        }

        mock_load_kg.return_value = pd.DataFrame([
            {"skill_name": "Python", "demand_count": 100, "category": "Technical", "prerequisites": []},
            {"skill_name": "ML", "demand_count": 80, "category": "Technical", "prerequisites": ["Python"]}
        ])

        mock_load_jd.return_value = (["Python", "ML"], {"Python": 0.8, "ML": 0.6})
        mock_load_peer.return_value = ({"primary_db": {"Python": 0.9, "ML": 0.7}}, None)

        mock_graph = Mock()
        mock_build_graph.return_value = mock_graph

        mock_find_gaps.return_value = {"ML": (0.8, 0.2)}
        mock_arbitrate.return_value = [{"skill": "ML", "priority": "high"}]

        mock_filter.return_value = {
            'filtered_gaps': [{"skill": "ML", "priority": "high"}],
            'removed_gaps': [],
            'filter_metadata': {}
        }

        mock_build_json.return_value = {"skill_gaps": {"target_role": "Data Scientist", "gaps": []}}

        # Test direct input mode
        result = skillgap.process_single_user(
            user_id="test_user",
            user_skills=["Python"],
            target_roles=["Data Scientist"]
        )

        assert result["success"] is True
        assert result["user_id"] == "test_user"
        assert "all_role_results" in result

    @patch('skillgap.skillgap.load_user_profile')
    def test_process_single_user_no_target_roles(self, mock_load_profile):
        """Test process_single_user with no target roles specified."""
        from skillgap import skillgap

        mock_load_profile.return_value = {
            "user_id": "test_user",
            "user_skills": ["Python"],
            "target_roles": []
        }

        result = skillgap.process_single_user("test_user")

        assert result["success"] is False
        assert "No target roles specified" in result["error"]

    @patch('skillgap.skillgap.load_user_profile')
    @patch('skillgap.skillgap.load_kg_output_for_role')
    def test_process_single_user_empty_kg_data(self, mock_load_kg, mock_load_profile):
        """Test process_single_user when no KG data is available for a role."""
        from skillgap import skillgap

        mock_load_profile.return_value = {
            "user_id": "test_user",
            "user_skills": ["Python"],
            "target_roles": ["Unknown Role"]
        }

        mock_load_kg.return_value = pd.DataFrame()  # Empty DataFrame

        result = skillgap.process_single_user("test_user")

        assert result["success"] is True
        assert result["total_roles"] == 0  # No roles processed due to empty KG

# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Test error handling in various functions."""

    @patch('skillgap.skillgap.IN_DATABRICKS', True)
    @patch('skillgap.skillgap.execute_sql_query')
    def test_load_user_profile_sql_error_fallback(self, mock_execute):
        """Test that load_user_profile falls back to CSV when SQL fails."""
        from skillgap import skillgap

        # Mock SQL query to fail
        mock_execute.side_effect = Exception("SQL connection failed")

        # This should fall back to CSV loading
        profile = skillgap.load_user_profile("test_user_1")

        # Should load from CSV
        assert profile["user_id"] == "test_user_1"
        assert "Python" in profile["user_skills"]

    @patch('skillgap.skillgap.IN_DATABRICKS', True)
    @patch('skillgap.skillgap.execute_sql_query')
    def test_find_similar_roles_error_handling(self, mock_execute):
        """Test error handling in find_similar_roles_in_kg."""
        from skillgap import skillgap

        # Mock SQL query to fail
        mock_execute.side_effect = Exception("Database error")

        result = skillgap.find_similar_roles_in_kg("Test Role")

        # Should return empty list on error
        assert result == []

    @patch('skillgap.skillgap.IN_DATABRICKS', True)
    @patch('skillgap.skillgap.execute_sql_query')
    def test_load_peer_data_partial_match(self, mock_execute):
        """Test load_peer_data with partial role matches."""
        from skillgap import skillgap

        # Mock partial match data
        mock_execute.return_value = pd.DataFrame([
            {"Skills": "Python, SQL", "Current_Job_Title": "Data Analyst"},
            {"Skills": "Java, Spring", "Current_Job_Title": "Software Engineer"}
        ])

        peer_data, _ = skillgap.load_peer_data("Data Scientist")

        # Should find skills from partial matches
        assert "primary_db" in peer_data
        assert len(peer_data["primary_db"]) > 0

    @patch('skillgap.skillgap.IN_DATABRICKS', True)
    @patch('skillgap.skillgap.execute_sql_query')
    def test_load_peer_data_general_fallback(self, mock_execute):
        """Test load_peer_data general fallback when no matches found."""
        from skillgap import skillgap

        # Mock no matches, then general data
        mock_execute.side_effect = [
            pd.DataFrame(),  # No exact matches
            pd.DataFrame(),  # No partial matches
            pd.DataFrame([   # General data
                {"Skills": "Python, SQL", "Current_Job_Title": "Various"},
                {"Skills": "Java, AWS", "Current_Job_Title": "Various"}
            ])
        ]

        peer_data, _ = skillgap.load_peer_data("Unknown Role")

        # Should use general data
        assert "primary_db" in peer_data

# ============================================================================
# Utility Functions Tests
# ============================================================================

class TestUtilityFunctions:
    """Test utility and helper functions."""

    def test_load_jd_demand_scores_empty_df(self):
        """Test load_jd_demand_scores with empty DataFrame."""
        from skillgap import skillgap

        result_skills, result_db = skillgap.load_jd_demand_scores("Test Role", pd.DataFrame())

        assert result_skills == []
        assert result_db == {}

    def test_compute_career_distance_no_prerequisites(self):
        """Test compute_career_distance with skill having no prerequisites."""
        from skillgap import skillgap
        import networkx as nx

        # Create a simple graph
        g = nx.DiGraph()
        g.add_node("Python")

        distance = skillgap.compute_career_distance(["Java"], "Python", g)

        assert distance == 1  # No prerequisites, distance = 1

    def test_compute_career_distance_with_prerequisites(self):
        """Test compute_career_distance with prerequisites."""
        from skillgap import skillgap
        import networkx as nx

        # Create graph with prerequisites
        g = nx.DiGraph()
        g.add_edge("Python", "ML", relation="skill-prerequisite-skill")

        distance = skillgap.compute_career_distance([], "ML", g)

        assert distance == 2  # ML requires Python, which user doesn't have

    def test_jd_demand_expert_edge_cases(self):
        """Test jd_demand_expert with edge cases."""
        from skillgap import skillgap

        # Empty role_required_skills - should return the skill's demand score
        score = skillgap.jd_demand_expert("Python", {"Python": 0.8}, [])
        assert score == 0.8  # Should return the skill's demand score when no role skills

        # Skill not in demand_db
        score = skillgap.jd_demand_expert("Unknown", {"Python": 0.8}, ["Python"])
        assert score == 0.0

    def test_peer_cv_expert_edge_cases(self):
        """Test peer_cv_expert with edge cases."""
        from skillgap import skillgap

        # No peer data
        score = skillgap.peer_cv_expert("Python", None)
        assert score == 0.5

        # Empty peer data
        score = skillgap.peer_cv_expert("Python", {})
        assert score == 0.5

        # Skill not in peer data
        score = skillgap.peer_cv_expert("Unknown", {"primary_db": {"Python": 0.8}})
        assert score == 0.0

# ============================================================================
# Output Functions Tests
# ============================================================================

class TestOutputFunctions:
    """Test output generation functions."""

    def test_build_json_output_with_metadata(self):
        """Test build_json_output with filter metadata and removed gaps."""
        from skillgap import skillgap

        gaps = [
            {"skill": "Python", "category": "Technical", "gap_weight": 0.5, "user_skill_proficiency": 0.5,
             "demand_score": 0.8, "peer_score": 0.7, "graph_distance": 1, "priority": "high", "rationale": "test"}
        ]

        filter_metadata = {"removed_count": 1, "remaining_count": 1}
        removed_gaps = [{"skill": "Java", "filter_reason": "User declared"}]

        result = skillgap.build_json_output("Data Scientist", gaps, filter_metadata, removed_gaps)

        assert "skill_gaps" in result
        assert result["skill_gaps"]["target_role"] == "Data Scientist"
        assert "filter_metadata" in result["skill_gaps"]
        assert "removed_gaps" in result["skill_gaps"]
        assert "unified_score" not in result["skill_gaps"]["gaps"][0]  # Should be removed

    def test_build_json_output_minimal(self):
        """Test build_json_output with minimal inputs."""
        from skillgap import skillgap

        gaps = [{"skill": "Python", "category": "Technical"}]

        result = skillgap.build_json_output("Test Role", gaps)

        assert result["skill_gaps"]["target_role"] == "Test Role"
        assert len(result["skill_gaps"]["gaps"]) == 1
        assert result["skill_gaps"]["top_5_skills"] == ["Python"]
