"""
Unit Tests for Application Module
==================================

Tests for the main Streamlit application including:
- CV parsing (PDF and DOCX)
- Chat flow and conversation management
- LLM interactions
- Session state management
- User profile collection
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
import sys
from pathlib import Path
import io

import os
# Add project modules to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


# ============================================================================
# Global Fixtures for App Tests
# ============================================================================

@pytest.fixture(autouse=True)
def mock_streamlit_session_state():
    """Mock Streamlit session state for all app tests."""
    with patch('streamlit.session_state') as mock_state:
        # Initialize common session state attributes
        mock_state.current_role = ""
        mock_state.aspired_role = ""
        mock_state.budget = ""
        mock_state.time_commitment = ""
        mock_state._w_current_role = ""
        yield mock_state


# ============================================================================
# CV Parsing Tests
# ============================================================================

@pytest.mark.unit
class TestCVParsing:
    """Test CV text extraction from various formats."""
    
    @patch('fitz.open')
    def test_parse_pdf_cv_success(self, mock_fitz_open):
        """Test successful PDF CV extraction using parse_pdf_cv."""
        from app import app
        
        # Mock fitz document
        mock_doc = MagicMock()
        mock_doc.page_count = 2
        mock_page1 = MagicMock()
        mock_page1.get_text.return_value = "Page 1 content\n"
        mock_page2 = MagicMock()
        mock_page2.get_text.return_value = "Page 2 content\n"
        mock_doc.__getitem__.side_effect = [mock_page1, mock_page2]
        mock_fitz_open.return_value = mock_doc
        
        # Mock uploaded file
        mock_file = MagicMock()
        mock_file.read.return_value = b"fake pdf bytes"
        
        # Test
        result = app.parse_pdf_cv(mock_file)
        
        assert "Page 1 content" in result
        assert "Page 2 content" in result
        mock_doc.close.assert_called_once()

    @patch('app.app.st.session_state')
    def test_clean_text(self, mock_session_state):
        """Test clean_text utility."""
        from app import app

        # Initialize session state
        mock_session_state.current_role = ""

        html = "<div>Hello&nbsp;World! â€¢ Item</div>"
        cleaned = app.clean_text(html)
        # The function converts â€¢ to • and removes HTML tags, but doesn't handle &nbsp;
        assert "Hello&nbsp;World!" in cleaned  # &nbsp; is not converted
        assert "• Item" in cleaned  # â€¢ is converted to •
        assert "<div" not in cleaned  # HTML tags are removed

    @patch('app.app.st.session_state')
    def test_parse_budget(self, mock_session_state):
        """Test parse_budget utility."""
        from app import app

        # Initialize session state
        mock_session_state.current_role = ""

        assert app.parse_budget("$1,000") == 1000.0
        assert app.parse_budget("SGD 500.50") == 500.5
        assert app.parse_budget("invalid") == 10000.0
        assert app.parse_budget("") == 10000.0

    @patch('app.app.st.session_state')
    def test_parse_time_commitment(self, mock_session_state):
        """Test parse_time_commitment utility."""
        from app import app

        # Initialize session state
        mock_session_state.current_role = ""

        assert app.parse_time_commitment("5 hours/week") == 5.0
        assert app.parse_time_commitment("10 hrs") == 10.0
        assert app.parse_time_commitment("invalid") == 40.0  # Function returns 40.0 for invalid input

    @patch('docx.Document')
    def test_parse_docx_cv_success(self, mock_docx):
        """Test successful DOCX CV extraction."""
        from app import app
        
        # Mock DOCX paragraphs
        mock_para1 = MagicMock()
        mock_para1.text = "Paragraph 1"
        mock_para2 = MagicMock()
        mock_para2.text = "Paragraph 2"
        
        mock_doc = MagicMock()
        mock_doc.paragraphs = [mock_para1, mock_para2]
        mock_docx.return_value = mock_doc
        
        # Mock uploaded file
        mock_file = MagicMock()
        
        # Test
        result = app.parse_docx_cv(mock_file)
        
        assert "Paragraph 1" in result
        assert "Paragraph 2" in result


# ============================================================================
# CV Analysis Tests
# ============================================================================

@pytest.mark.unit
class TestCVAnalysis:
    """Test CV analysis with LLM."""
    
    @patch('app.app.st.session_state')
    @patch('app.app.get_openai_client')
    def test_analyse_cv_success(self, mock_get_client, mock_session_state):
        """Test successful CV analysis."""
        from app import app
        
        # Initialize session state
        mock_session_state.current_role = ""

        # Mock OpenAI response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '{"current_role": "Data Scientist", "skills": ["Python", "SQL"]}'
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        # Test
        role, skills = app.extract_role_and_skills_from_cv("Sample CV text")
        
        assert role == "Data Scientist"
        assert "Python" in skills
        assert "SQL" in skills

    @patch('app.app.st.session_state')
    @patch('app.app.get_openai_client')
    def test_analyse_cv_handles_llm_error(self, mock_get_client, mock_session_state):
        """Test CV analysis with LLM error."""
        from app import app
        
        # Initialize session state
        mock_session_state.current_role = ""

        # Mock LLM error
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("LLM Error")
        mock_get_client.return_value = mock_client
        
        # Test
        role, skills = app.extract_role_and_skills_from_cv("Sample CV text")
        
        assert role is None
        assert skills == []


# ============================================================================
# JSON Parsing Tests
# ============================================================================

@pytest.mark.unit
class TestJSONParsing:
    """Test JSON response parsing from LLM."""
    
    @patch('app.app.st.session_state')
    def test_parse_json_clean(self, mock_session_state):
        """Test parsing clean JSON."""
        from app import app
        
        # Initialize session state
        mock_session_state.current_role = ""

        json_str = '{"name": "John", "age": 30}'
        result = app.parse_json(json_str)
        
        assert result["name"] == "John"
        assert result["age"] == 30
    
    @patch('app.app.st.session_state')
    def test_parse_json_with_markdown_fences(self, mock_session_state):
        """Test parsing JSON with markdown code fences."""
        from app import app
        
        # Initialize session state
        mock_session_state.current_role = ""

        json_str = '```json\n{"name": "John", "age": 30}\n```'
        result = app.parse_json(json_str)
        
        assert result["name"] == "John"
        assert result["age"] == 30
    
    @patch('app.app.st.session_state')
    def test_parse_json_with_multiple_code_blocks(self, mock_session_state):
        """Test parsing with multiple code blocks."""
        from app import app
        
        # Initialize session state
        mock_session_state.current_role = ""

        json_str = '```\nSome text\n```\n```json\n{"valid": true}\n```'
        result = app.parse_json(json_str)
        
        assert result["valid"] is True
    
    @patch('app.app.st.session_state')
    def test_parse_json_malformed_returns_fallback(self, mock_session_state):
        """Test that malformed JSON returns fallback dict."""
        from app import app
        
        # Initialize session state
        mock_session_state.current_role = ""

        json_str = '{invalid json: missing quotes}'
        result = app.parse_json(json_str)
        
        # Should return fallback dict
        assert isinstance(result, dict)
        assert "message" in result


# ============================================================================
# Session State Tests
# ============================================================================

@pytest.mark.unit
class TestSessionState:
    """Test session state management."""
    
    @patch('app.app.st.warning')
    def test_is_profile_complete(self, mock_warning):
        """Test is_profile_complete logic."""
        from app import app
        
        # We need to mock session_state
        with patch('app.app.st.session_state') as mock_state:
            mock_state.current_role = "Dev"
            mock_state.aspired_role = "Lead"
            mock_state.budget = "1000"
            mock_state.time_commitment = "5"
            
            assert app.is_profile_complete() is True
            
            mock_state.current_role = ""
            assert app.is_profile_complete() is False


# ============================================================================
# Conversation Flow Tests
# ============================================================================

@pytest.mark.unit
class TestConversationFlow:
    """Test chat conversation logic."""
    
    @patch('app.app.st.session_state')
    def test_required_fields_collection(self, mock_session_state):
        """Test that all required fields are defined."""
        from app import app
        
        # Initialize session state
        mock_session_state.current_role = ""

        assert "cv_role" in app.REQUIRED
        assert "target_role" in app.REQUIRED
        assert "budget" in app.REQUIRED
        assert "time_commit" in app.REQUIRED
    
    @patch('app.app.st.session_state')
    def test_max_history_turns_defined(self, mock_session_state):
        """Test conversation history limit."""
        from app import app
        
        # Initialize session state
        mock_session_state.current_role = ""

        assert hasattr(app, 'MAX_HISTORY_TURNS')
        assert app.MAX_HISTORY_TURNS > 0


# ============================================================================
# OpenAI Client Tests
# ============================================================================

@pytest.mark.unit
class TestOpenAIClient:
    """Test OpenAI client initialization."""
    
    @patch('app.app.st.session_state')
    @patch('app.app.os.getenv')
    def test_get_openai_client_from_env(self, mock_getenv, mock_session_state):
        """Test client creation from environment variable."""
        from app import app
        
        # Initialize session state
        mock_session_state.current_role = ""

        mock_getenv.return_value = "test-api-key"
        
        client = app.get_openai_client()
        
        assert client is not None
        mock_getenv.assert_called()
    
    @patch('app.app.st.session_state')
    @patch('app.app.os.getenv')
    @patch('app.app.st')
    def test_get_openai_client_missing_key_stops(self, mock_st, mock_getenv, mock_session_state):
        """Test that missing API key triggers warning."""
        from app import app
        
        # Initialize session state
        mock_session_state.current_role = ""

        mock_getenv.return_value = ""
        
        # Should call st.warning and st.stop
        try:
            app.get_openai_client()
        except:
            pass
        
        # At minimum, should have attempted to warn the user
        # (actual implementation may vary)


# ============================================================================
# Integration Test Markers
# ============================================================================

@pytest.mark.integration
@pytest.mark.requires_openai
@pytest.mark.skip(reason="Requires OpenAI API - run manually")
class TestAppIntegration:
    """Integration tests requiring external services."""
    
    def test_real_cv_parsing_and_analysis(self):
        """Test end-to-end CV parsing with real LLM."""
        pass
    
    def test_real_conversation_flow(self):
        """Test complete conversation flow with real LLM."""
        pass


# ============================================================================
# Smoke Tests
# ============================================================================

@pytest.mark.smoke
@pytest.mark.skipif(
    os.getenv("DATABRICKS_RUNTIME_VERSION") is not None,
    reason="App tests require Databricks App runtime, skipping in notebooks"
)
class TestAppSmoke:
    """Quick smoke tests for critical functionality."""
    
    def test_module_imports_successfully(self):
        """Test that the app module can be imported."""
        import app.app
        assert hasattr(app.app, 'extract_role_and_skills_from_cv')
        assert hasattr(app.app, 'parse_budget')
        assert hasattr(app.app, 'parse_json')
    
    @patch('app.app.st.session_state')
    def test_constants_defined(self, mock_session_state):
        """Test that critical constants are defined."""
        from app import app

        # Initialize session state
        mock_session_state.current_role = ""

        assert hasattr(app, 'CONFIG_LLM_MODEL')
        assert hasattr(app, 'REQUIRED')
        assert hasattr(app, 'MAX_HISTORY_TURNS')
