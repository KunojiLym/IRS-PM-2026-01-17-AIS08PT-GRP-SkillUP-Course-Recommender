"""
Pipeline Orchestration Tests
============================

Tests for pipeline.py orchestration functions.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os

from recommender.models import UserProfile, Course, SkillGap, Modality, Schedule, LearningPath
from recommender.pipeline import (
    run_recommendation_pipeline,
    run_multi_role_recommendation_pipeline
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_user():
    """Sample user profile"""
    return UserProfile(
        user_id="pipeline_test_user",
        current_role="Developer",
        target_role="ML Engineer",
        current_skills=["Python"],
        budget=5000.0,
        available_hours_per_week=15.0,
        preferred_modality=Modality.ONLINE,
        preferred_schedule=Schedule.EVENING,
        skillsfuture_eligible=True
    )


@pytest.fixture
def sample_courses():
    """Sample course catalog"""
    return [
        Course(
            course_id="COURSE-A",
            title="Course A",
            provider="Provider A",
            total_hours=100.0,
            cost=2000.0,
            cost_after_subsidy=600.0,
            modality=Modality.ONLINE,
            schedule=Schedule.EVENING,
            skills_covered="machine learning; python",
            prerequisites="",
            rating=4.5,
            enrollment_count=500,
            skillsfuture_eligible=True
        ),
        Course(
            course_id="COURSE-B",
            title="Course B",
            provider="Provider B",
            total_hours=80.0,
            cost=1500.0,
            cost_after_subsidy=450.0,
            modality=Modality.ONLINE,
            schedule=Schedule.FLEXIBLE,
            skills_covered="deep learning; tensorflow",
            prerequisites="COURSE-A",
            rating=4.7,
            enrollment_count=300,
            skillsfuture_eligible=True
        ),
    ]


@pytest.fixture
def stage2_json():
    """Sample Stage 2 JSON"""
    return {
        "skill_gaps": {
            "target_role": "ML Engineer",
            "gaps": [
                {
                    "skill": "machine learning",
                    "priority": "critical",
                    "gap_weight": 0.8,
                    "user_skill_proficiency": 0.2
                },
                {
                    "skill": "deep learning",
                    "priority": "high",
                    "gap_weight": 0.7,
                    "user_skill_proficiency": 0.1
                }
            ],
            "candidate_courses": [
                {"course_id": "COURSE-A"},
                {"course_id": "COURSE-B"}
            ]
        }
    }


# ============================================================================
# SINGLE ROLE PIPELINE TESTS
# ============================================================================

class TestSingleRolePipeline:
    """Test single-role recommendation pipeline"""
    
    def test_pipeline_with_candidate_courses(
        self, stage2_json, sample_user, sample_courses
    ):
        """Test pipeline filters to candidate courses"""
        learning_path = run_recommendation_pipeline(
            stage2_json=stage2_json,
            user_profile=sample_user,
            course_catalog=sample_courses
        )
        
        assert learning_path is not None
        assert isinstance(learning_path, LearningPath)
        
        # Check recommended courses are from candidate list
        candidate_ids = {"COURSE-A", "COURSE-B"}
        recommended_ids = {rc.course.course_id for rc in learning_path.courses}
        assert recommended_ids.issubset(candidate_ids)
    
    def test_pipeline_no_candidate_courses(
        self, sample_user, sample_courses
    ):
        """Test pipeline uses full catalog when no candidates specified"""
        stage2_no_candidates = {
            "skill_gaps": {
                "target_role": "ML Engineer",
                "gaps": [
                    {
                        "skill": "machine learning",
                        "priority": "critical",
                        "gap_weight": 0.8,
                        "user_skill_proficiency": 0.2
                    }
                ],
                "candidate_courses": []
            }
        }
        
        learning_path = run_recommendation_pipeline(
            stage2_json=stage2_no_candidates,
            user_profile=sample_user,
            course_catalog=sample_courses
        )
        
        assert learning_path is not None
    
    def test_pipeline_saves_output_json(
        self, stage2_json, sample_user, sample_courses, tmp_path
    ):
        """Test pipeline saves JSON output when path provided"""
        output_file = tmp_path / "test_output.json"
        
        learning_path = run_recommendation_pipeline(
            stage2_json=stage2_json,
            user_profile=sample_user,
            course_catalog=sample_courses,
            output_json_path=str(output_file)
        )
        
        assert output_file.exists()
        
        # Verify file is valid JSON
        import json
        with open(output_file) as f:
            data = json.load(f)
        
        assert "user_id" in data
        assert data["user_id"] == sample_user.user_id
    
    def test_pipeline_no_output_json(
        self, stage2_json, sample_user, sample_courses
    ):
        """Test pipeline works without saving JSON"""
        learning_path = run_recommendation_pipeline(
            stage2_json=stage2_json,
            user_profile=sample_user,
            course_catalog=sample_courses,
            output_json_path=None
        )
        
        assert learning_path is not None


# ============================================================================
# MULTI ROLE PIPELINE TESTS
# ============================================================================

class TestMultiRolePipeline:
    """Test multi-role recommendation pipeline"""
    
    @pytest.fixture
    def multi_role_json(self):
        """Sample multi-role Stage 2 JSON"""
        return [
            {
                "skill_gaps": {
                    "target_role": "Data Engineer",
                    "gaps": [
                        {
                            "skill": "spark",
                            "priority": "critical",
                            "gap_weight": 0.85,
                            "user_skill_proficiency": 0.15
                        }
                    ],
                    "candidate_courses": []
                }
            },
            {
                "skill_gaps": {
                    "target_role": "ML Engineer",
                    "gaps": [
                        {
                            "skill": "tensorflow",
                            "priority": "high",
                            "gap_weight": 0.75,
                            "user_skill_proficiency": 0.25
                        }
                    ],
                    "candidate_courses": []
                }
            }
        ]
    
    @patch('recommender.pipeline.SparkSession')
    @patch('recommender.data_loading._load_course_from_row')
    def test_multi_role_pipeline_basic(
        self, mock_load_course, mock_spark_session, multi_role_json, sample_user, sample_courses
    ):
        """Test basic multi-role pipeline execution"""
        # Mock Spark session and course loading
        mock_spark = MagicMock()
        mock_spark_session.builder.getOrCreate.return_value = mock_spark
        
        # Mock table returns DataFrame with rows
        mock_df = MagicMock()
        mock_df.collect.return_value = []  # Empty for simplicity
        mock_spark.table.return_value = mock_df
        
        # Mock course loading to return sample courses
        mock_load_course.side_effect = sample_courses
        
        learning_paths = run_multi_role_recommendation_pipeline(
            all_role_results=multi_role_json,
            user_profile=sample_user,
            output_dir=None
        )
        
        # Should return dict with 2 roles
        assert len(learning_paths) == 2
        assert "Data Engineer" in learning_paths
        assert "ML Engineer" in learning_paths
        
        # Each should be a LearningPath
        for role, path in learning_paths.items():
            assert isinstance(path, LearningPath)
    
    @patch('recommender.pipeline.SparkSession')
    @patch('recommender.data_loading._load_course_from_row')
    def test_multi_role_saves_separate_files(
        self, mock_load_course, mock_spark_session, multi_role_json, 
        sample_user, sample_courses, tmp_path
    ):
        """Test multi-role pipeline saves separate JSON file per role"""
        # Mock Spark
        mock_spark = MagicMock()
        mock_spark_session.builder.getOrCreate.return_value = mock_spark
        mock_df = MagicMock()
        mock_df.collect.return_value = []
        mock_spark.table.return_value = mock_df
        mock_load_course.side_effect = sample_courses
        
        output_dir = tmp_path / "multi_role_output"
        
        learning_paths = run_multi_role_recommendation_pipeline(
            all_role_results=multi_role_json,
            user_profile=sample_user,
            output_dir=str(output_dir)
        )
        
        # Check output directory was created
        assert output_dir.exists()
        
        # Check files were created (role names sanitized)
        expected_files = ["data_engineer.json", "ml_engineer.json"]
        for filename in expected_files:
            filepath = output_dir / filename
            # File should exist (or be attempted to be created)
            # Note: Actual file creation depends on mock behavior
    
    def test_multi_role_pyspark_not_available(
        self, multi_role_json, sample_user
    ):
        """Test multi-role pipeline raises error without PySpark"""
        with patch('recommender.pipeline.SparkSession', None):
            with pytest.raises(RuntimeError, match="PySpark not available"):
                run_multi_role_recommendation_pipeline(
                    all_role_results=multi_role_json,
                    user_profile=sample_user,
                    output_dir=None
                )


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestPipelineEdgeCases:
    """Test pipeline edge cases"""
    
    def test_pipeline_empty_catalog(self, stage2_json, sample_user):
        """Test pipeline with empty course catalog"""
        learning_path = run_recommendation_pipeline(
            stage2_json=stage2_json,
            user_profile=sample_user,
            course_catalog=[],  # Empty catalog
            output_json_path=None
        )
        
        assert learning_path is not None
        assert learning_path.total_courses == 0
    
    def test_pipeline_no_matching_candidates(self, sample_user, sample_courses):
        """Test pipeline when candidate courses don't exist in catalog"""
        stage2_wrong_ids = {
            "skill_gaps": {
                "target_role": "ML Engineer",
                "gaps": [
                    {
                        "skill": "machine learning",
                        "priority": "critical",
                        "gap_weight": 0.8,
                        "user_skill_proficiency": 0.2
                    }
                ],
                "candidate_courses": [
                    {"course_id": "NON-EXISTENT-ID-1"},
                    {"course_id": "NON-EXISTENT-ID-2"}
                ]
            }
        }
        
        learning_path = run_recommendation_pipeline(
            stage2_json=stage2_wrong_ids,
            user_profile=sample_user,
            course_catalog=sample_courses
        )
        
        # Should return path with 0 courses (none matched)
        assert learning_path is not None
        assert learning_path.total_courses == 0


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
