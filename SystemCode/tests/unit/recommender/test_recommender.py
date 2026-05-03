"""
Unit Tests for Course Recommendation System (Stage 3)
=====================================================

Comprehensive pytest test suite covering all recommender modules.
Updated to use correct Course dataclass API.
"""

import pytest
from datetime import datetime
from typing import List

from recommender.models import (
    UserProfile, SkillGap, Course, HistoricalCase,
    Modality, Schedule, LearningPath, RecommendedCourse
)
from recommender.config import RecommenderConfig
from recommender.csp import ConstraintSolver
from recommender.cbr import CaseLibrary
from recommender.fuzzy import FuzzyScorer
from recommender.scoring import ScoreFusion
from recommender.sequencing import CourseSequencer
from recommender.recommender import CourseRecommender
from recommender.utils import jaccard_similarity, semantic_similarity, normalize_score
from recommender.integration import parse_stage2_json, parse_stage2_multi_role_json
from recommender.serialization import serialize_learning_path_to_json


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_config():
    """Default configuration for testing"""
    return RecommenderConfig(min_relevance_threshold=0.3)


@pytest.fixture
def sample_user_profile():
    """Sample user profile for testing"""
    return UserProfile(
        user_id="test_user_001",
        current_role="Software Developer",
        target_role="ML Engineer",
        current_skills=["Python", "SQL", "Git"],
        budget=3000.0,
        available_hours_per_week=10.0,
        preferred_modality=Modality.ONLINE,
        preferred_schedule=Schedule.EVENING,
        skillsfuture_eligible=True,
        preferred_providers=["NUS-ISS", "Coursera"]
    )


@pytest.fixture
def sample_skill_gaps():
    """Sample skill gaps for testing"""
    return [
        SkillGap("machine learning", priority=0.95, current_level=0.1, target_level=0.8, gap_size=0.7),
        SkillGap("deep learning", priority=0.85, current_level=0.0, target_level=0.7, gap_size=0.7),
        SkillGap("statistics", priority=0.80, current_level=0.3, target_level=0.7, gap_size=0.4),
    ]


@pytest.fixture
def sample_course_catalog():
    """Sample course catalog using correct Course API"""
    return [
        Course(
            course_id="ML-101",
            title="Machine Learning Fundamentals",
            provider="NUS-ISS",
            total_hours=80.0,  # 8 weeks × 10 hrs/week
            cost=1200.0,
            cost_after_subsidy=360.0,  # 70% subsidy
            modality=Modality.ONLINE,
            schedule=Schedule.EVENING,
            skills_covered="machine learning; python",
            prerequisites="",
            rating=4.5,
            enrollment_count=500,
            skillsfuture_eligible=True
        ),
        Course(
            course_id="STAT-201",
            title="Statistics for Data Science",
            provider="Coursera",
            total_hours=60.0,  # 6 weeks × 10 hrs/week
            cost=800.0,
            cost_after_subsidy=400.0,  # 50% subsidy
            modality=Modality.ONLINE,
            schedule=Schedule.FLEXIBLE,
            skills_covered="statistics; probability",
            prerequisites="",
            rating=4.3,
            enrollment_count=300,
            skillsfuture_eligible=True
        ),
        Course(
            course_id="DL-301",
            title="Deep Learning Specialization",
            provider="Coursera",
            total_hours=120.0,  # 12 weeks × 10 hrs/week
            cost=2000.0,
            cost_after_subsidy=800.0,  # 60% subsidy
            modality=Modality.ONLINE,
            schedule=Schedule.FLEXIBLE,
            skills_covered="deep learning; neural networks; python",
            prerequisites="ML-101",
            rating=4.7,
            enrollment_count=800,
            skillsfuture_eligible=True
        ),
        Course(
            course_id="EXPENSIVE-999",
            title="Executive Data Science Program",
            provider="MIT",
            total_hours=100.0,  # 10 weeks × 10 hrs/week
            cost=10000.0,
            cost_after_subsidy=10000.0,  # 0% subsidy
            modality=Modality.ONSITE,
            schedule=Schedule.WEEKDAY,
            skills_covered="machine learning; strategy",
            prerequisites="",
            rating=5.0,
            enrollment_count=50,
            skillsfuture_eligible=False
        ),
    ]


@pytest.fixture
def sample_historical_cases():
    """Sample historical cases for CBR testing"""
    return [
        HistoricalCase(
            case_id="case_001",
            user_profile=UserProfile(
                user_id="historical_user_001",
                current_role="Software Engineer",
                target_role="Data Scientist",
                current_skills=["Python", "SQL"],
                budget=2500.0,
                available_hours_per_week=12.0,
                preferred_modality=Modality.ONLINE,
                preferred_schedule=Schedule.EVENING,
                skillsfuture_eligible=True
            ),
            skill_gaps=[
                SkillGap("machine learning", priority=0.9, current_level=0.2, target_level=0.8, gap_size=0.6),
                SkillGap("statistics", priority=0.85, current_level=0.3, target_level=0.7, gap_size=0.4),
            ],
            completed_courses=["ML-101", "STAT-201"],
            completion_rate=0.9,
            satisfaction_score=4.5,
            total_duration_weeks=14
        ),
    ]


# ============================================================================
# UTILITY FUNCTION TESTS
# ============================================================================

class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_jaccard_similarity_identical(self):
        """Test Jaccard similarity with identical sets"""
        set1 = {"Python", "SQL", "Java"}
        set2 = {"Python", "SQL", "Java"}
        assert jaccard_similarity(set1, set2) == 1.0
    
    def test_jaccard_similarity_disjoint(self):
        """Test Jaccard similarity with disjoint sets"""
        set1 = {"Python", "SQL"}
        set2 = {"Java", "C++"}
        assert jaccard_similarity(set1, set2) == 0.0
    
    def test_jaccard_similarity_partial(self):
        """Test Jaccard similarity with partial overlap"""
        set1 = {"Python", "SQL", "Java"}
        set2 = {"Python", "Java", "C++"}
        # Intersection: {Python, Java} = 2, Union: {Python, SQL, Java, C++} = 4
        assert jaccard_similarity(set1, set2) == 0.5
    
    def test_jaccard_similarity_empty_sets(self):
        """Test Jaccard similarity with empty sets"""
        assert jaccard_similarity(set(), set()) == 1.0
    
    def test_normalize_score(self):
        """Test score normalization"""
        assert normalize_score(5.0, 0.0, 10.0) == 0.5
        assert normalize_score(0.0, 0.0, 10.0) == 0.0
        assert normalize_score(10.0, 0.0, 10.0) == 1.0
        assert normalize_score(5.0, 5.0, 5.0) == 1.0  # Same min/max
    
    def test_semantic_similarity(self):
        """Test semantic similarity (word overlap)"""
        text1 = "machine learning engineer"
        text2 = "machine learning developer"
        similarity = semantic_similarity(text1, text2)
        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.0  # Should have some overlap


# ============================================================================
# CSP CONSTRAINT SOLVER TESTS
# ============================================================================

class TestConstraintSolver:
    """Test CSP constraint solver"""
    
    def test_filter_courses_budget_constraint(
        self, sample_config, sample_course_catalog, sample_user_profile, sample_skill_gaps
    ):
        """Test budget constraint filtering"""
        solver = ConstraintSolver(sample_config)
        valid, violations = solver.filter_courses(
            sample_course_catalog, sample_user_profile, sample_skill_gaps
        )
        
        # EXPENSIVE-999 should be filtered (cost_after_subsidy 10000 > budget 3000)
        valid_ids = [c.course_id for c in valid]
        assert "EXPENSIVE-999" not in valid_ids
        assert "ML-101" in valid_ids
    
    def test_filter_courses_time_constraint(
        self, sample_config, sample_skill_gaps
    ):
        """Test time availability constraint"""
        # Create user with limited time
        user = UserProfile(
            user_id="test_user",
            current_role="Developer",
            target_role="ML Engineer",
            current_skills=["Python"],
            budget=5000.0,
            available_hours_per_week=5.0,  # Only 5 hours/week
            preferred_modality=Modality.ONLINE,
            preferred_schedule=Schedule.EVENING,
            skillsfuture_eligible=True
        )
        
        # Create course requiring more time
        courses = [
            Course(
                course_id="TIME-INTENSIVE",
                title="Time Intensive Course",
                provider="Provider",
                total_hours=120.0,  # 12 weeks × 10 hrs/week = requires 10 hrs/week
                cost=1000.0,
                cost_after_subsidy=500.0,
                modality=Modality.ONLINE,
                schedule=Schedule.EVENING,
                skills_covered="machine learning",
                prerequisites="",
                rating=4.5,
                enrollment_count=100,
                skillsfuture_eligible=True
            )
        ]
        
        solver = ConstraintSolver(sample_config)
        valid, violations = solver.filter_courses(courses, user, sample_skill_gaps)
        
        # Course should be filtered due to time constraint
        assert len(valid) == 0
        assert len(violations) > 0
    
    def test_filter_courses_skillsfuture_eligibility(
        self, sample_config, sample_skill_gaps
    ):
        """Test SkillsFuture eligibility constraint"""
        user = UserProfile(
            user_id="test_user",
            current_role="Developer",
            target_role="ML Engineer",
            current_skills=["Python"],
            budget=15000.0,  # High budget
            available_hours_per_week=20.0,  # Plenty of time
            preferred_modality=Modality.ONLINE,
            preferred_schedule=Schedule.EVENING,
            skillsfuture_eligible=True  # Requires SF eligible courses
        )
        
        courses = [
            Course(
                course_id="NON-SF",
                title="Non-SkillsFuture Course",
                provider="Provider",
                total_hours=80.0,
                cost=1000.0,
                cost_after_subsidy=1000.0,
                modality=Modality.ONLINE,
                schedule=Schedule.EVENING,
                skills_covered="machine learning",
                prerequisites="",
                rating=4.5,
                enrollment_count=100,
                skillsfuture_eligible=False  # NOT SF eligible
            )
        ]
        
        solver = ConstraintSolver(sample_config)
        valid, violations = solver.filter_courses(courses, user, sample_skill_gaps)
        
        # Course should be filtered due to SF eligibility
        assert len(valid) == 0
        assert any("SkillsFuture" in v for v in violations)
    
    def test_calculate_relevance(self, sample_config, sample_skill_gaps):
        """Test relevance calculation"""
        solver = ConstraintSolver(sample_config)
        
        # Perfect match course
        perfect_course = Course(
            course_id="PERFECT",
            title="Perfect Match",
            provider="Provider",
            total_hours=80.0,
            cost=1000.0,
            cost_after_subsidy=300.0,
            modality=Modality.ONLINE,
            schedule=Schedule.EVENING,
            skills_covered="machine learning; deep learning; statistics",
            prerequisites="",
            rating=4.5,
            enrollment_count=100,
            skillsfuture_eligible=True
        )
        
        relevance = solver.calculate_relevance(perfect_course, sample_skill_gaps)
        assert relevance > 0.9  # Should be very high
        
        # No match course
        no_match_course = Course(
            course_id="NO-MATCH",
            title="No Match",
            provider="Provider",
            total_hours=80.0,
            cost=1000.0,
            cost_after_subsidy=300.0,
            modality=Modality.ONLINE,
            schedule=Schedule.EVENING,
            skills_covered="java; c++",
            prerequisites="",
            rating=4.5,
            enrollment_count=100,
            skillsfuture_eligible=True
        )
        
        relevance = solver.calculate_relevance(no_match_course, sample_skill_gaps)
        assert relevance == 0.0


# ============================================================================
# FUZZY LOGIC SCORER TESTS
# ============================================================================

class TestFuzzyScorer:
    """Test fuzzy logic scorer"""
    
    def test_budget_membership_within_budget(self, sample_config, sample_user_profile):
        """Test budget fuzzy membership within budget"""
        scorer = FuzzyScorer(sample_config)
        
        course = Course(
            course_id="AFFORDABLE",
            title="Affordable Course",
            provider="Provider",
            total_hours=80.0,
            cost=2000.0,
            cost_after_subsidy=500.0,  # Well within 3000 budget
            modality=Modality.ONLINE,
            schedule=Schedule.EVENING,
            skills_covered="machine learning",
            prerequisites="",
            rating=4.5,
            enrollment_count=100,
            skillsfuture_eligible=True
        )
        
        fuzzy_scores = scorer.calculate_fuzzy_scores(
            course, sample_user_profile, []
        )
        
        assert fuzzy_scores.budget_fitness == 1.0
    
    def test_budget_membership_over_budget(self, sample_config, sample_user_profile):
        """Test budget fuzzy membership over budget"""
        scorer = FuzzyScorer(sample_config)
        
        course = Course(
            course_id="EXPENSIVE",
            title="Expensive Course",
            provider="Provider",
            total_hours=80.0,
            cost=5000.0,
            cost_after_subsidy=3500.0,  # Over 3000 budget but within tolerance
            modality=Modality.ONLINE,
            schedule=Schedule.EVENING,
            skills_covered="machine learning",
            prerequisites="",
            rating=4.5,
            enrollment_count=100,
            skillsfuture_eligible=True
        )
        
        fuzzy_scores = scorer.calculate_fuzzy_scores(
            course, sample_user_profile, []
        )
        
        # Should have partial fitness (between 0 and 1)
        assert 0.0 <= fuzzy_scores.budget_fitness <= 1.0
    
    def test_modality_membership(self, sample_config, sample_user_profile, sample_skill_gaps):
        """Test modality preference matching"""
        scorer = FuzzyScorer(sample_config)
        
        # Matching modality
        online_course = Course(
            course_id="ONLINE",
            title="Online Course",
            provider="Provider",
            total_hours=80.0,
            cost=1000.0,
            cost_after_subsidy=300.0,
            modality=Modality.ONLINE,  # Matches user preference
            schedule=Schedule.EVENING,
            skills_covered="machine learning",
            prerequisites="",
            rating=4.5,
            enrollment_count=100,
            skillsfuture_eligible=True
        )
        
        fuzzy_scores = scorer.calculate_fuzzy_scores(
            online_course, sample_user_profile, sample_skill_gaps
        )
        
        assert fuzzy_scores.modality_match == 1.0


# ============================================================================
# CBR CASE LIBRARY TESTS
# ============================================================================

class TestCaseLibrary:
    """Test case-based reasoning library"""
    
    def test_add_case(self, sample_config, sample_historical_cases):
        """Test adding historical cases"""
        library = CaseLibrary(sample_config)
        
        for case in sample_historical_cases:
            library.add_case(case)
        
        assert len(library.cases) == len(sample_historical_cases)
    
    def test_find_similar_cases(
        self, sample_config, sample_user_profile, sample_skill_gaps, sample_historical_cases
    ):
        """Test finding similar cases"""
        library = CaseLibrary(sample_config)
        
        for case in sample_historical_cases:
            library.add_case(case)
        
        similar_cases = library.find_similar_cases(
            sample_user_profile, sample_skill_gaps, top_k=5
        )
        
        assert len(similar_cases) > 0
        # Check structure: list of (case, similarity) tuples
        for case, similarity in similar_cases:
            assert isinstance(case, HistoricalCase)
            assert 0.0 <= similarity <= 1.0


# ============================================================================
# SCORE FUSION TESTS
# ============================================================================

class TestScoreFusion:
    """Test score fusion component"""
    
    def test_fuse_scores_all_components(self, sample_config, sample_course_catalog):
        """Test score fusion with all components"""
        fusion = ScoreFusion(sample_config)
        
        # Create sample score dictionaries
        relevance_scores = {course.course_id: 0.8 for course in sample_course_catalog[:2]}
        cbr_scores = {course.course_id: 0.7 for course in sample_course_catalog[:2]}
        soft_constraint_scores = {course.course_id: 1.0 for course in sample_course_catalog[:2]}
        
        # Create fuzzy scores
        from recommender.models import FuzzyScores
        fuzzy_scores_map = {
            course.course_id: FuzzyScores(
                budget_score=1.0,
                time_score=0.9,
                modality_score=1.0,
                schedule_score=0.8,
                total_fuzzy_score=0.9
            )
            for course in sample_course_catalog[:2]
        }
        
        results = fusion.calculate_final_scores(
            courses=sample_course_catalog[:2],
            relevance_scores=relevance_scores,
            cbr_scores=cbr_scores,
            fuzzy_scores_map=fuzzy_scores_map,
            soft_constraint_scores=soft_constraint_scores
        )
        
        assert len(results) == 2
        for course, final_score, breakdown, fuzzy in results:
            assert 0.0 <= final_score <= 1.0
            assert breakdown.relevance >= 0.0
            assert breakdown.cbr >= 0.0

# ============================================================================
# COURSE SEQUENCER TESTS
# ============================================================================

class TestCourseSequencer:
    """Test course sequencer"""
    
    def test_sequence_courses_with_prerequisites(self, sample_config, sample_course_catalog):
        """Test course sequencing"""
        sequencer = CourseSequencer()  # No config argument
        
        # Create sample ranked courses (course, score, breakdown, fuzzy)
        from recommender.models import FuzzyScores, ScoreBreakdown
        
        ranked_courses = []
        for i, course in enumerate(sample_course_catalog[:3]):
            breakdown = ScoreBreakdown(
                relevance=0.8,
                rating=0.9,
                constraint_fit=1.0,
                cbr=0.7,
                popularity=0.6
            )
            fuzzy = FuzzyScores(
                budget_fitness=1.0,
                time_fitness=0.9,
                modality_match=1.0,
                schedule_match=0.8,
                provider_match=0.5
            )
            ranked_courses.append((course, 0.85 - i*0.1, breakdown, fuzzy))
        
        sequenced = sequencer.sequence_courses(ranked_courses, max_courses=3)
        
        assert len(sequenced) == 3
        # Check sequence positions are assigned
        for rec_course in sequenced:
            assert rec_course.sequence_position is not None
            assert len(rec_course.sequence_position) > 0

# ============================================================================
# END-TO-END RECOMMENDER TESTS
# ============================================================================

class TestCourseRecommender:
    """Test end-to-end recommender system"""
    
    def test_recommend_basic(
        self, sample_user_profile, sample_skill_gaps, sample_course_catalog
    ):
        """Test basic recommendation flow"""
        recommender = CourseRecommender()
        
        learning_path = recommender.recommend(
            sample_user_profile, sample_skill_gaps, sample_course_catalog
        )
        
        assert isinstance(learning_path, LearningPath)
        assert learning_path.user_id == sample_user_profile.user_id
        assert learning_path.total_courses >= 0
        assert learning_path.total_cost >= 0
        assert learning_path.total_cost_after_subsidy >= 0
    
    def test_recommend_filters_expensive_courses(
        self, sample_user_profile, sample_skill_gaps, sample_course_catalog
    ):
        """Test that expensive courses are filtered"""
        recommender = CourseRecommender()
        
        learning_path = recommender.recommend(
            sample_user_profile, sample_skill_gaps, sample_course_catalog
        )
        
        # EXPENSIVE-999 should not be recommended (exceeds budget)
        recommended_ids = [rc.course.course_id for rc in learning_path.courses]
        assert "EXPENSIVE-999" not in recommended_ids
    
    def test_recommend_returns_sorted_courses(
        self, sample_user_profile, sample_skill_gaps, sample_course_catalog
    ):
        """Test that courses are sorted by score"""
        recommender = CourseRecommender()
        
        learning_path = recommender.recommend(
            sample_user_profile, sample_skill_gaps, sample_course_catalog
        )
        
        if len(learning_path.courses) > 1:
            # Check that ranks are sequential
            ranks = [rc.rank for rc in learning_path.courses]
            assert ranks == list(range(1, len(ranks) + 1))
            
            # Check that scores are descending
            scores = [rc.final_score for rc in learning_path.courses]
            assert scores == sorted(scores, reverse=True)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestStage2Integration:
    """Test Stage 2 integration functions"""
    
    def test_parse_stage2_json_basic(self):
        """Test parsing basic Stage 2 JSON"""
        stage2_output = {
            "skill_gaps": {
                "target_role": "Machine Learning Engineer",
                "gaps": [
                    {
                        "skill": "deep learning",
                        "priority": "critical",
                        "gap_weight": 0.75,
                        "user_skill_proficiency": 0.25
                    }
                ],
                "candidate_courses": [
                    {"course_id": "DL-101", "covers_skills": ["deep learning"]}
                ]
            }
        }
        
        target_role, skill_gaps, candidate_ids = parse_stage2_json(stage2_output)
        
        assert target_role == "Machine Learning Engineer"
        assert len(skill_gaps) == 1
        assert skill_gaps[0].skill == "deep learning"
        assert len(candidate_ids) == 1
        assert "DL-101" in candidate_ids
    
    def test_parse_stage2_multi_role_json(self):
        """Test parsing multi-role Stage 2 JSON"""
        all_role_results = [
            {
                "skill_gaps": {
                    "target_role": "Data Engineer",
                    "gaps": [{"skill": "spark", "priority": "high", "gap_weight": 0.8, "user_skill_proficiency": 0.2}],
                    "candidate_courses": [{"course_id": "SPARK-101"}]
                }
            },
            {
                "skill_gaps": {
                    "target_role": "ML Engineer",
                    "gaps": [{"skill": "tensorflow", "priority": "critical", "gap_weight": 0.9, "user_skill_proficiency": 0.1}],
                    "candidate_courses": [{"course_id": "TF-201"}]
                }
            }
        ]
        
        role_data_map = parse_stage2_multi_role_json(all_role_results)
        
        assert len(role_data_map) == 2
        assert "Data Engineer" in role_data_map
        assert "ML Engineer" in role_data_map


# ============================================================================
# SERIALIZATION TESTS
# ============================================================================

class TestSerialization:
    """Test JSON serialization"""
    
    def test_serialize_learning_path(
        self, sample_user_profile, sample_skill_gaps, sample_course_catalog
    ):
        """Test learning path serialization"""
        recommender = CourseRecommender()
        learning_path = recommender.recommend(
            sample_user_profile, sample_skill_gaps, sample_course_catalog
        )
        
        json_output = serialize_learning_path_to_json(learning_path)
        
        assert "user_id" in json_output
        assert "generated_at" in json_output
        assert "summary" in json_output
        assert "recommended_courses" in json_output
        assert json_output["user_id"] == sample_user_profile.user_id
    
    def test_serialize_handles_enum_objects(
        self, sample_user_profile, sample_skill_gaps, sample_course_catalog
    ):
        """Test that enum objects are properly serialized to strings"""
        recommender = CourseRecommender()
        learning_path = recommender.recommend(
            sample_user_profile, sample_skill_gaps, sample_course_catalog
        )
        
        json_output = serialize_learning_path_to_json(learning_path)
        
        # Check that modality and schedule are strings
        if json_output["recommended_courses"]:
            course = json_output["recommended_courses"][0]["course"]
            assert isinstance(course["modality"], str)
            assert isinstance(course["schedule"], str)


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
