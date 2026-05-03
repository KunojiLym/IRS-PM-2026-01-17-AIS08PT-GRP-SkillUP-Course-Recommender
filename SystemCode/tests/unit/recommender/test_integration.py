"""
Integration Tests for Stage 2 → Stage 3 Pipeline
================================================

Tests the complete integration flow from skillgap.py output to recommendations.
"""

import pytest
import json
from pathlib import Path
from typing import Dict, Any

from recommender.models import UserProfile, Modality, Schedule, Course
from recommender.integration import parse_stage2_json, parse_stage2_multi_role_json
from recommender.pipeline import run_recommendation_pipeline, run_multi_role_recommendation_pipeline
from recommender.serialization import serialize_learning_path_to_json


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def stage2_single_role_output() -> Dict[str, Any]:
    """Sample Stage 2 JSON output for single role"""
    return {
        "skill_gaps": {
            "target_role": "Machine Learning Engineer",
            "total_gaps": 3,
            "gaps": [
                {
                    "skill": "deep learning",
                    "category": "Technical",
                    "gap_weight": 0.75,
                    "user_skill_proficiency": 0.25,
                    "demand_score": 0.85,
                    "peer_score": 0.88,
                    "graph_distance": 2,
                    "priority": "critical",
                    "rationale": "Required in 85% of ML Engineer postings"
                },
                {
                    "skill": "tensorflow",
                    "category": "Technical",
                    "gap_weight": 0.68,
                    "user_skill_proficiency": 0.15,
                    "demand_score": 0.78,
                    "peer_score": 0.82,
                    "graph_distance": 3,
                    "priority": "high",
                    "rationale": "Industry-standard framework"
                },
                {
                    "skill": "mlops",
                    "category": "Technical",
                    "gap_weight": 0.62,
                    "user_skill_proficiency": 0.10,
                    "demand_score": 0.72,
                    "peer_score": 0.75,
                    "graph_distance": 4,
                    "priority": "high",
                    "rationale": "Production ML deployment expertise"
                }
            ],
            "candidate_courses": [
                {
                    "course_id": "SF-DL-001",
                    "covers_skills": ["deep learning", "tensorflow"],
                    "pre_constraint": True
                },
                {
                    "course_id": "SF-MLOPS-004",
                    "covers_skills": ["mlops", "tensorflow"],
                    "pre_constraint": False
                }
            ]
        }
    }


@pytest.fixture
def stage2_multi_role_output() -> list:
    """Sample Stage 2 JSON output for multiple roles"""
    return [
        {
            "skill_gaps": {
                "target_role": "Data Engineer",
                "gaps": [
                    {
                        "skill": "apache spark",
                        "priority": "critical",
                        "gap_weight": 0.8,
                        "user_skill_proficiency": 0.2
                    }
                ],
                "candidate_courses": [
                    {"course_id": "SPARK-101"}
                ]
            }
        },
        {
            "skill_gaps": {
                "target_role": "ML Engineer",
                "gaps": [
                    {
                        "skill": "tensorflow",
                        "priority": "high",
                        "gap_weight": 0.85,
                        "user_skill_proficiency": 0.15
                    }
                ],
                "candidate_courses": [
                    {"course_id": "TF-201"}
                ]
            }
        }
    ]


@pytest.fixture
def sample_user_profile():
    """Sample user profile"""
    return UserProfile(
        user_id="integration_test_user",
        current_role="Software Developer",
        target_role="Machine Learning Engineer",
        current_skills=["Python", "SQL"],
        budget=5000.0,
        available_hours_per_week=12.0,
        preferred_modality=Modality.ONLINE,
        preferred_schedule=Schedule.EVENING,
        skillsfuture_eligible=True
    )


@pytest.fixture
def sample_courses():
    """Sample course catalog"""
    return [
        Course(
            course_id="SF-DL-001",
            title="Deep Learning Fundamentals",
            provider="NUS",
            total_hours=120.0,
            cost=2800.0,
            cost_after_subsidy=840.0,
            modality=Modality.ONLINE,
            schedule=Schedule.EVENING,
            skills_covered="deep learning; tensorflow; neural networks",
            prerequisites="",
            rating=4.8,
            enrollment_count=1250,
            skillsfuture_eligible=True
        ),
        Course(
            course_id="SF-MLOPS-004",
            title="MLOps: Production ML",
            provider="Coursera",
            total_hours=60.0,
            cost=1800.0,
            cost_after_subsidy=720.0,
            modality=Modality.ONLINE,
            schedule=Schedule.WEEKEND,
            skills_covered="mlops; kubernetes; tensorflow",
            prerequisites="SF-DL-001",
            rating=4.5,
            enrollment_count=620,
            skillsfuture_eligible=True
        ),
    ]


# ============================================================================
# STAGE 2 PARSING TESTS
# ============================================================================

class TestStage2Parsing:
    """Test Stage 2 JSON parsing"""
    
    def test_parse_single_role_complete_data(self, stage2_single_role_output):
        """Test parsing complete Stage 2 single role output"""
        target_role, skill_gaps, candidate_ids = parse_stage2_json(stage2_single_role_output)
        
        # Check target role
        assert target_role == "Machine Learning Engineer"
        
        # Check skill gaps
        assert len(skill_gaps) == 3
        assert skill_gaps[0].skill == "deep learning"
        assert 0.0 <= skill_gaps[0].priority <= 1.0
        assert skill_gaps[0].gap_size == 0.75
        
        # Check candidate courses
        assert len(candidate_ids) == 2
        assert "SF-DL-001" in candidate_ids
        assert "SF-MLOPS-004" in candidate_ids
    
    def test_parse_priority_mapping(self, stage2_single_role_output):
        """Test priority text to numeric mapping"""
        _, skill_gaps, _ = parse_stage2_json(stage2_single_role_output)
        
        # Critical priority should map to 0.95
        critical_gap = next(g for g in skill_gaps if g.skill == "deep learning")
        assert critical_gap.priority == pytest.approx(0.95, abs=0.01)
        
        # High priority should map to 0.75
        high_gap = next(g for g in skill_gaps if g.skill == "tensorflow")
        assert high_gap.priority == pytest.approx(0.75, abs=0.01)
    
    def test_parse_multi_role(self, stage2_multi_role_output):
        """Test parsing multi-role Stage 2 output"""
        role_data_map = parse_stage2_multi_role_json(stage2_multi_role_output)
        
        assert len(role_data_map) == 2
        assert "Data Engineer" in role_data_map
        assert "ML Engineer" in role_data_map
        
        # Check Data Engineer data
        de_gaps, de_courses = role_data_map["Data Engineer"]
        assert len(de_gaps) == 1
        assert de_gaps[0].skill == "apache spark"
        assert "SPARK-101" in de_courses


# ============================================================================
# PIPELINE INTEGRATION TESTS
# ============================================================================

class TestPipelineIntegration:
    """Test end-to-end pipeline integration"""
    
    def test_single_role_pipeline_complete(
        self, stage2_single_role_output, sample_user_profile, sample_courses, tmp_path
    ):
        """Test complete single-role pipeline execution"""
        output_file = tmp_path / "recommendations.json"
        
        learning_path = run_recommendation_pipeline(
            stage2_json=stage2_single_role_output,
            user_profile=sample_user_profile,
            course_catalog=sample_courses,
            output_json_path=str(output_file)
        )
        
        # Check learning path
        assert learning_path is not None
        assert learning_path.user_id == sample_user_profile.user_id
        assert learning_path.total_courses >= 0
        
        # Check output file was created
        assert output_file.exists()
        
        # Verify JSON structure
        with open(output_file) as f:
            json_data = json.load(f)
        
        assert "user_id" in json_data
        assert "summary" in json_data
        assert "recommended_courses" in json_data
    
    def test_pipeline_filters_candidate_courses(
        self, stage2_single_role_output, sample_user_profile, sample_courses
    ):
        """Test that pipeline filters to candidate courses from Stage 2"""
        learning_path = run_recommendation_pipeline(
            stage2_json=stage2_single_role_output,
            user_profile=sample_user_profile,
            course_catalog=sample_courses
        )
        
        # All recommended courses should be from candidate list
        candidate_ids = {"SF-DL-001", "SF-MLOPS-004"}
        recommended_ids = {rc.course.course_id for rc in learning_path.courses}
        
        assert recommended_ids.issubset(candidate_ids)
    
    def test_pipeline_empty_candidate_courses(
        self, sample_user_profile, sample_courses
    ):
        """Test pipeline with no candidate courses specified"""
        stage2_no_candidates = {
            "skill_gaps": {
                "target_role": "ML Engineer",
                "gaps": [
                    {
                        "skill": "deep learning",
                        "priority": "critical",
                        "gap_weight": 0.8,
                        "user_skill_proficiency": 0.2
                    }
                ],
                "candidate_courses": []  # Empty candidate list
            }
        }
        
        learning_path = run_recommendation_pipeline(
            stage2_json=stage2_no_candidates,
            user_profile=sample_user_profile,
            course_catalog=sample_courses
        )
        
        # Should use full catalog
        assert learning_path is not None


# ============================================================================
# OUTPUT VALIDATION TESTS
# ============================================================================

class TestOutputValidation:
    """Test Stage 3 output validation"""
    
    def test_output_json_schema(
        self, stage2_single_role_output, sample_user_profile, sample_courses
    ):
        """Test that output JSON has correct schema"""
        learning_path = run_recommendation_pipeline(
            stage2_json=stage2_single_role_output,
            user_profile=sample_user_profile,
            course_catalog=sample_courses
        )
        
        json_output = serialize_learning_path_to_json(learning_path)
        
        # Required top-level keys
        assert "user_id" in json_output
        assert "generated_at" in json_output
        assert "summary" in json_output
        assert "cbr_insight" in json_output
        assert "recommended_courses" in json_output
        
        # Summary fields
        summary = json_output["summary"]
        assert "total_courses" in summary
        assert "total_duration_weeks" in summary
        assert "total_cost_sgd" in summary
        assert "total_cost_after_subsidy_sgd" in summary
        assert "total_savings_sgd" in summary
        assert "subsidy_rate" in summary
        
        # Recommended courses structure
        if json_output["recommended_courses"]:
            course = json_output["recommended_courses"][0]
            assert "rank" in course
            assert "sequence_position" in course
            assert "course" in course
            assert "scores" in course
    
    def test_output_no_enum_objects(
        self, stage2_single_role_output, sample_user_profile, sample_courses
    ):
        """Test that output contains no enum objects (all strings)"""
        learning_path = run_recommendation_pipeline(
            stage2_json=stage2_single_role_output,
            user_profile=sample_user_profile,
            course_catalog=sample_courses
        )
        
        json_output = serialize_learning_path_to_json(learning_path)
        
        # Verify can be serialized to JSON string
        json_str = json.dumps(json_output)
        assert len(json_str) > 0
        
        # Verify enum values are strings
        if json_output["recommended_courses"]:
            course_data = json_output["recommended_courses"][0]["course"]
            assert isinstance(course_data["modality"], str)
            assert isinstance(course_data["schedule"], str)


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test error handling in integration"""
    
    def test_missing_skill_gaps_key(self, sample_user_profile, sample_courses):
        """Test handling of malformed Stage 2 JSON"""
        bad_json = {"invalid_key": "invalid_value"}
        
        with pytest.raises(KeyError):
            parse_stage2_json(bad_json)
    
    def test_empty_gaps_array(self, sample_user_profile, sample_courses):
        """Test handling of empty gaps array - should raise ValueError"""
        stage2_empty_gaps = {
            "skill_gaps": {
                "target_role": "ML Engineer",
                "gaps": [],  # Empty
                "candidate_courses": []
            }
        }
        
        with pytest.raises(ValueError, match="No valid skill gaps found"):
            parse_stage2_json(stage2_empty_gaps)


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
