# SkillUP Test Suite

Comprehensive test coverage for the SkillUP intelligent reasoning system.

---

## 📁 Test Structure

```
tests/
├── conftest.py                     # Shared fixtures and configuration
├── pytest.ini                      # Pytest configuration
├── unit/                           # Fast, isolated unit tests
│   ├── knowledgegraph/
│   │   └── test_knowledgegraph.py # Neo4j operations tests
│   ├── skillgap/
│   │   └── test_skillgap.py       # Skill gap analysis tests
│   ├── recommender/
│   │   └── test_recommender.py    # Course recommendation tests (35 tests)
│   └── app/
│       └── test_app.py            # Application logic tests
├── integration/
│   └── test_end_to_end.py         # Pipeline integration tests
└── fixtures/                       # Test data and mock objects
```

---

## 🚀 Running Tests

### Run All Tests

```bash
cd skillup
uv run pytest tests/
```

### Run Specific Test Categories

```bash
# Unit tests only (fast, no external dependencies)
uv run pytest tests/ -m unit

# Integration tests (requires services)
uv run pytest tests/ -m integration

# Smoke tests (quick critical checks)
uv run pytest tests/ -m smoke

# Tests for specific module
uv run pytest tests/unit/knowledgegraph/
uv run pytest tests/unit/skillgap/
uv run pytest tests/unit/recommender/
uv run pytest tests/unit/app/
```

### Run with Coverage Report

```bash
# Generate coverage report
uv run pytest tests/ --cov=. --cov-report=html

# View coverage in browser
open htmlcov/index.html
```

### Run Specific Test Classes or Functions

```bash
# Run a specific test class
uv run pytest tests/unit/knowledgegraph/test_knowledgegraph.py::TestGetSkillsFromJob

# Run a specific test function
uv run pytest tests/unit/skillgap/test_skillgap.py::TestEmbedding::test_get_embedding_generates_new

# Run tests matching a pattern
uv run pytest tests/ -k "test_cv"
```

---

## 📓 Running Tests via Databricks Notebooks

For users who prefer the notebook interface, test runner notebooks are available in the `notebooks/` folder. These notebooks provide an interactive way to run tests with visual feedback.

### Available Test Notebooks

**🧪 [Test_Runner](../notebooks/Test_Runner.ipynb)** - Comprehensive test suite runner
* Run all unit tests with detailed output
* Run tests by module (Knowledge Graph, Skill Gap, Recommender, App)
* Execute smoke tests for quick validation
* Generate HTML coverage reports
* Run integration tests (when services are available)
* Custom test selection using patterns

**⚡ [Quick_Smoke_Tests](../notebooks/Quick_Smoke_Tests.ipynb)** - Fast validation (< 30 seconds)
* Verify critical functionality across all modules
* Perfect for quick system health checks
* Uses mocked dependencies (no credentials required)
* Time tracking for performance monitoring

**📊 [Coverage_Analysis](../notebooks/Coverage_Analysis.ipynb)** - Detailed coverage reporting
* Generate HTML, XML, and terminal coverage reports
* Module-by-module coverage breakdown
* Identify missing coverage and untested code
* Export coverage data for CI/CD integration
* Coverage threshold validation

### How to Use Test Notebooks

1. **Navigate** to `skillup/notebooks/` in your Databricks workspace
2. **Open** the desired test notebook
3. **Attach** to a cluster (or use serverless compute)
4. **Run cells** sequentially - dependencies are auto-installed

**Benefits:**
* ✅ Visual test execution with rich output
* ✅ No local setup required - runs in Databricks
* ✅ Automatic dependency installation
* ✅ Easy to share with team members
* ✅ Integrated with Databricks workspace

**Example: Quick Smoke Test**
```python
# In Quick_Smoke_Tests notebook
# Just run the cells - no setup needed!
%pip install pytest pytest-mock --quiet
!python -m pytest tests/ -m smoke -v
# ✅ All smoke tests passed in 15 seconds!
```

**PowerShell Script Usage:**
```powershell
# On Windows, use the PowerShell script instead
.\run_tests.ps1 smoke      # Quick smoke tests
.\run_tests.ps1 unit       # All unit tests
.\run_tests.ps1 coverage   # With coverage report
```

---

## 🏷️ Test Markers

Tests are marked for categorization:

 Marker | Description | Usage |
--------|-------------|-------|
 `@pytest.mark.unit` | Fast, isolated unit tests | Default for most tests |
 `@pytest.mark.integration` | Tests requiring external services | Run explicitly |
 `@pytest.mark.slow` | Tests taking significant time | Skip for quick runs |
 `@pytest.mark.requires_neo4j` | Requires Neo4j connection | Skip unless configured |
 `@pytest.mark.requires_databricks` | Requires Databricks | Skip unless configured |
 `@pytest.mark.requires_openai` | Requires OpenAI API | Skip unless configured |
 `@pytest.mark.smoke` | Critical functionality checks | Run first |

### Running Tests by Marker

```bash
# Run only unit tests
uv run pytest tests/ -m unit

# Run smoke tests first
uv run pytest tests/ -m smoke

# Skip tests requiring external services
uv run pytest tests/ -m "not requires_neo4j and not requires_databricks"

# Run integration tests explicitly
uv run pytest tests/ -m integration --runxfail
```

---

## 📊 Test Coverage

### Current Coverage Targets

 Module | Target Coverage | Current Status |
--------|----------------|----------------|
 **knowledgegraph** | 80%+ | ✅ New tests added |
 **skillgap** | 75%+ | ✅ New tests added |
 **recommender** | 85%+ | ✅ 35 existing tests |
 **app** | 70%+ | ✅ New tests added |

### Generating Coverage Reports

```bash
# Terminal report with missing lines
uv run pytest tests/ --cov=. --cov-report=term-missing

# HTML report (interactive)
uv run pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html

# XML report (for CI/CD)
uv run pytest tests/ --cov=. --cov-report=xml
```

---

## 🧪 Writing New Tests

### Test File Naming

* **Unit tests**: `test_<module_name>.py`
* **Integration tests**: `test_<feature>_integration.py`
* Place in appropriate directory under `tests/unit/` or `tests/integration/`

### Test Function Naming

```python
def test_<function_name>_<scenario>():
    """Test that <expected behavior>."""
    pass
```

**Examples:**
* `test_get_skills_from_job_valid_input()`
* `test_load_user_profile_handles_null_values()`
* `test_extract_cv_text_unsupported_format()`

### Using Shared Fixtures

Fixtures are defined in `conftest.py`:

```python
def test_something(mock_neo4j_driver, sample_user_profile):
    """Use shared fixtures for common test data."""
    assert sample_user_profile["user_id"] == "test_user_001"
```

**Available Fixtures:**
* `mock_env_vars` - Mocked environment variables
* `mock_neo4j_driver` - Mock Neo4j driver
* `mock_openai_client` - Mock OpenAI client
* `sample_cv_text` - Sample CV text
* `sample_user_profile` - Sample user profile
* `sample_skill_gaps` - Sample skill gap data
* `sample_courses` - Sample course catalog

### Adding Test Markers

```python
import pytest

@pytest.mark.unit
def test_fast_isolated():
    """Fast test with no external dependencies."""
    pass

@pytest.mark.integration
@pytest.mark.requires_neo4j
@pytest.mark.skip(reason="Requires Neo4j - run manually")
def test_with_real_database():
    """Test requiring actual database connection."""
    pass
```

---

## 🔧 Test Configuration

### pytest.ini

Configuration in `tests/pytest.ini`:
* Test discovery patterns
* Coverage targets
* Marker definitions
* Warning filters

### conftest.py

Shared fixtures and utilities:
* Mock objects (Neo4j, OpenAI, Databricks)
* Sample data fixtures
* Environment setup
* Test utilities

---

## 🐛 Debugging Tests

### Run in Verbose Mode

```bash
uv run pytest tests/ -v
```

### Show Print Statements

```bash
uv run pytest tests/ -s
```

### Drop into Debugger on Failure

```bash
uv run pytest tests/ --pdb
```

### Run Last Failed Tests

```bash
uv run pytest tests/ --lf
```

### Run Only Failed Tests First

```bash
uv run pytest tests/ --ff
```

---

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: uv run pytest tests/ --cov=. --cov-report=xml
      - uses: codecov/codecov-action@v3
```

---

## 📝 Best Practices

### ✅ DO

* Write tests for all new functions
* Use descriptive test names
* Test both success and error cases
* Mock external dependencies
* Keep tests fast and isolated
* Use fixtures for common setup

### ❌ DON'T

* Test implementation details
* Write tests dependent on other tests
* Use real external services in unit tests
* Commit `.pytest_cache` or `htmlcov`
* Skip writing tests "to save time"

---

## 🆘 Troubleshooting

### Import Errors

```bash
# Ensure project root is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uv run pytest tests/
```

### Missing Dependencies

```bash
# Install test dependencies
uv add --dev pytest pytest-cov pytest-mock
```

### Test Discovery Issues

```bash
# Verify test discovery
uv run pytest --collect-only tests/
```

---

## 📚 Additional Resources

* [pytest Documentation](https://docs.pytest.org/)
* [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
* [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

---

**Maintained by**: SkillUP Development Team  
**Last Updated**: April 2026
