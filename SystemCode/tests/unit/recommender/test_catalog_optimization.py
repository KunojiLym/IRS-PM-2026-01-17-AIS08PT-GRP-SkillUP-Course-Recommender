
import pytest
import os
import pandas as pd
from unittest.mock import MagicMock, patch
from recommender.catalog import CourseCatalog, IN_DATABRICKS
from recommender.models import Course, SkillGap

@pytest.fixture
def temp_csv(tmp_path):
    csv_file = tmp_path / "test_courses.csv"
    df = pd.DataFrame([
        {
            "coursereferencenumber": "C001",
            "coursetitle": "Python for Data Science",
            "trainingprovideralias": "Provider A",
            "full_course_fee": 1000.0,
            "course_fee_after_subsidies": 300.0,
            "number_of_hours": 40.0,
            "about_this_course": "Learn Python basics",
            "what_you_learn": "Python, Pandas, NumPy",
            "training_commitment": "Part-time",
            "conducted_in": "Online"
        },
        {
            "coursereferencenumber": "C002",
            "coursetitle": "Advanced Machine Learning",
            "trainingprovideralias": "Provider B",
            "full_course_fee": 2000.0,
            "course_fee_after_subsidies": 600.0,
            "number_of_hours": 60.0,
            "about_this_course": "Deep Learning and more",
            "what_you_learn": "TensorFlow, PyTorch",
            "training_commitment": "Full-time",
            "conducted_in": "Onsite"
        }
    ])
    df.to_csv(csv_file, index=False)
    return str(csv_file)

def test_load_from_csv(temp_csv):
    """Test loading courses from a local CSV file."""
    # Ensure we are NOT in Databricks for this test
    with patch('recommender.catalog.IN_DATABRICKS', False):
        catalog = CourseCatalog(csv_path=temp_csv)
        courses = catalog.load_all_courses()
        
        assert len(courses) == 2
        assert courses[0].course_id == "C001"
        assert courses[0].title == "Python for Data Science"
        assert courses[0].cost == 1000.0
        assert courses[0].cost_after_subsidy == 300.0
        assert courses[0].modality == "online"
        assert courses[1].course_id == "C002"
        assert courses[1].modality == "onsite"

@patch('recommender.catalog.IN_DATABRICKS', True)
def test_load_from_delta_mock():
    """Test loading courses from Delta table (mocked)."""
    with patch('pyspark.sql.SparkSession') as mock_spark_session:
        mock_spark = mock_spark_session.builder.getOrCreate.return_value
        mock_df = MagicMock()
        mock_spark.table.return_value = mock_df
        
        # Mock execute_sql_query directly to avoid Spark complexity
        with patch('recommender.catalog.execute_sql_query') as mock_query:
            mock_row = {
                "coursereferencenumber": "D001",
                "coursetitle": "Delta Course",
                "trainingprovideralias": "Delta Provider",
                "full_course_fee": 500.0,
                "course_fee_after_subsidies": 100.0,
                "number_of_hours": 20.0
            }
            mock_query.return_value = pd.DataFrame([mock_row])
            
            catalog = CourseCatalog(table_name="test_table")
            courses = catalog.load_all_courses()
            
            assert len(courses) == 1
            assert courses[0].course_id == "D001"
            assert courses[0].title == "Delta Course"
            mock_query.assert_called()

@patch('recommender.catalog.IN_DATABRICKS', True)
def test_semantic_search_spark_optimized():
    """Test that semantic search in Databricks uses Spark filtering."""
    with patch('pyspark.sql.SparkSession') as mock_spark_session:
        mock_spark = mock_spark_session.builder.getOrCreate.return_value
        
        # Mock execute_sql_query directly
        with patch('recommender.catalog.execute_sql_query') as mock_query:
            mock_row = {
                "coursereferencenumber": "S001",
                "coursetitle": "Spark Course",
                "trainingprovideralias": "Spark Provider",
                "full_course_fee": 1000.0,
                "course_fee_after_subsidies": 200.0,
                "number_of_hours": 30.0,
                "what_you_learn": "PySpark optimization"
            }
            mock_query.return_value = pd.DataFrame([mock_row])
            
            catalog = CourseCatalog(table_name="prod_table")
            skill_gaps = [SkillGap(skill="Spark", priority=1.0, current_level=0.0, target_level=1.0, gap_size=1.0)]
            
            results = catalog.semantic_search(skill_gaps, top_k=1)
            
            assert len(results) == 1
            assert results[0].course_id == "S001"
            mock_query.assert_called()
                
    @patch('recommender.catalog.IN_DATABRICKS', False)
    def test_semantic_search_local_csv_optimization(self, temp_csv):
        """Test that semantic search locally uses pandas filtering without loading all courses."""
        catalog = CourseCatalog(csv_path=temp_csv)
        skill_gaps = [SkillGap(skill="Python", priority=1.0, current_level=0.0, target_level=1.0, gap_size=1.0)]
        
        # We don't want load_all_courses to be called
        with patch.object(CourseCatalog, 'load_all_courses', return_value=[]) as mock_load:
            results = catalog.semantic_search(skill_gaps, top_k=1)
            
            assert len(results) == 1
            assert results[0].course_id == "C001"
            assert "Python" in results[0].title
            
            # verify load_all_courses was NOT called
            mock_load.assert_not_called()

    @patch('recommender.catalog.IN_DATABRICKS', False)
    def test_semantic_search_local_csv_no_match(self, temp_csv):
        """Test fallback when no matches found in local CSV."""
        catalog = CourseCatalog(csv_path=temp_csv)
        skill_gaps = [SkillGap(skill="Cooking", priority=1.0, current_level=0.0, target_level=1.0, gap_size=1.0)]
        
        results = catalog.semantic_search(skill_gaps, top_k=1)
        # Should return top course as fallback
        assert len(results) == 1
        assert results[0].course_id == "C001"
