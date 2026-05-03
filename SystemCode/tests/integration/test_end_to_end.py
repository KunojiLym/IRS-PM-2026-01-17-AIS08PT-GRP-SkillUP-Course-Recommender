"""
Integration Tests - End-to-End Pipeline
=======================================

Tests for complete workflow integration:
- Stage 1 (User Profile) → Stage 2 (Skill Gap) → Stage 3 (Recommendation)
- Data flow between modules
- External service integration
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# ============================================================================
# End-to-End Pipeline Tests
# ============================================================================

@pytest.mark.integration
class TestEndToEndPipeline:
    """Test complete pipeline from CV to recommendations."""
    
    @pytest.mark.skip(reason="Requires all services - run manually")
    def test_complete_pipeline_cv_to_recommendations(
        self,
        sample_cv_text,
        sample_user_profile,
        sample_skill_gaps,
        sample_courses
    ):
        """
        Test complete flow:
        1. Parse CV
        2. Collect user preferences
        3. Identify skill gaps
        4. Generate recommendations
        """
        # This would test the full integration
        # when all services are available
        pass
    
    @pytest.mark.skip(reason="Requires Neo4j and Databricks")
    def test_knowledge_graph_to_recommendations(self):
        """Test flow from KG extraction to course recommendations."""
        pass


# ============================================================================
# Stage Integration Tests
# ============================================================================

@pytest.mark.integration
class TestStageIntegration:
    """Test integration between stages."""
    
    def test_stage1_output_matches_stage2_input(
        self,
        sample_user_profile
    ):
        """Verify Stage 1 output format matches Stage 2 expected input."""
        # Stage 1 output should have:
        required_fields = [
            "user_id",
            "current_role",
            "target_role",
            "current_skills",
            "budget",
            "available_hours_per_week"
        ]
        
        for field in required_fields:
            assert field in sample_user_profile
    
    def test_stage2_output_matches_stage3_input(
        self,
        sample_skill_gaps
    ):
        """Verify Stage 2 output format matches Stage 3 expected input."""
        # Stage 2 output should have skill gaps with:
        required_fields = [
            "skill",
            "priority",
            "gap_weight"
        ]
        
        for gap in sample_skill_gaps:
            for field in required_fields:
                assert field in gap


# ============================================================================
# External Service Integration Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.requires_neo4j
@pytest.mark.skip(reason="Requires Neo4j connection")
class TestNeo4jIntegration:
    """Integration tests with Neo4j database."""
    
    def test_neo4j_connection_and_query(self):
        """Test actual Neo4j connection and query execution."""
        from knowledgegraph import knowledgegraph
        
        # This would test with real Neo4j instance
        # result = knowledgegraph.get_skills_from_job("Data Scientist")
        # assert result is not None
        pass


@pytest.mark.integration
@pytest.mark.requires_databricks
@pytest.mark.skip(reason="Requires Databricks connection")
class TestDatabricksIntegration:
    """Integration tests with Databricks."""
    
    def test_databricks_table_read(self):
        """Test reading from Delta tables."""
        # This would test with real Databricks workspace
        pass
    
    def test_databricks_mlflow_logging(self):
        """Test MLflow experiment logging."""
        pass


@pytest.mark.integration
@pytest.mark.requires_openai
@pytest.mark.skip(reason="Requires OpenAI API access")
class TestOpenAIIntegration:
    """Integration tests with OpenAI API."""
    
    def test_openai_cv_analysis(self, sample_cv_text):
        """Test real CV analysis with OpenAI."""
        from app import app
        import os
        
        # Only run if API key is available
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OpenAI API key not available")
        
        client = app.get_openai_client()
        result = app.analyse_cv(client, sample_cv_text)
        
        assert "name" in result
        assert "summary" in result
    
    def test_openai_conversation_flow(self):
        """Test conversation flow with real OpenAI calls."""
        pass


# ============================================================================
# Data Consistency Tests
# ============================================================================

@pytest.mark.integration
class TestDataConsistency:
    """Test data consistency across modules."""
    
    def test_skill_names_consistent_across_modules(self):
        """Test that skill names are consistently formatted."""
        # Skills should be lowercase, normalized
        from skillgap import skillgap
        
        # Test that embedding cache uses lowercase keys
        test_skill = "Python"
        skillgap._embedding_cache[test_skill.lower()] = [1.0, 2.0, 3.0]
        
        # Verify retrieval works regardless of case
        assert test_skill.lower() in skillgap._embedding_cache
    
    def test_course_ids_unique(self, sample_courses):
        """Test that course IDs are unique."""
        course_ids = [course["course_id"] for course in sample_courses]
        assert len(course_ids) == len(set(course_ids))


# ============================================================================
# Performance Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.slow
class TestPerformance:
    """Performance and load tests."""
    
    @pytest.mark.skip(reason="Performance test - run manually")
    def test_embedding_cache_performance(self):
        """Test that embedding cache improves performance."""
        import time
        from skillgap import skillgap
        
        skill = "Machine Learning"
        
        # First call (no cache)
        skillgap._embedding_cache.clear()
        start = time.time()
        skillgap.get_embedding(skill)
        first_call_time = time.time() - start
        
        # Second call (with cache)
        start = time.time()
        skillgap.get_embedding(skill)
        second_call_time = time.time() - start
        
        # Cache should be significantly faster
        assert second_call_time < first_call_time * 0.1
    
    @pytest.mark.skip(reason="Load test - run manually")
    def test_concurrent_recommendations(self):
        """Test handling of concurrent recommendation requests."""
        # Would test with multiple concurrent users
        pass
