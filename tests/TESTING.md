# Testing Guide

This document provides information about running and understanding the test suite for the FastAPI Voucher Management API.

## Test Structure

The test suite is organized into the following modules:

### 1. `tests/conftest.py`
Contains pytest fixtures and configuration:
- **Database Setup**: In-memory SQLite database for fast testing
- **Test Client**: FastAPI TestClient for making HTTP requests
- **Test Data Fixtures**: Reusable fixtures for tests

### 2. `tests/test_crud.py`
Tests for the CRUD operations layer (business logic):
- Voucher code generation
- Creating vouchers
- Retrieving vouchers (by code, valid vouchers)
- Listing vouchers with pagination
- Updating vouchers
- Deactivating vouchers

### 3. `tests/test_routes.py`
Tests for API endpoints:
- POST /api/v1/vouchers/ (Create)
- GET /api/v1/vouchers/ (List)
- GET /api/v1/vouchers/{code} (Retrieve valid)
- PUT /api/v1/vouchers/{code} (Update)
- PATCH /api/v1/vouchers/{code}/deactivate (Deactivate)
- Integration tests and workflows

## Installation

```bash
# Install test dependencies
pip install -r tests/requirements.txt
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Specific Test File
```bash
pytest tests/test_crud.py
pytest tests/test_routes.py
```

### Run Specific Test Class
```bash
pytest tests/test_crud.py::TestCreateVoucher
pytest tests/test_routes.py::TestCreateVoucherRoute
```

### Run Specific Test Function
```bash
pytest tests/test_crud.py::TestCreateVoucher::test_create_voucher_success
```

### Run Tests with Coverage Report
```bash
pytest --cov=app --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`

### Run Tests and Show Print Statements
```bash
pytest -v -s
```

### Run Tests Matching a Pattern
```bash
pytest -k "test_create"
pytest -k "test_pagination"
```

### Run Tests with Markers
```bash
pytest -m "not integration"
```

## Test Coverage

Target coverage: **90%+**

Current coverage includes:
- CRUD operations: 100%
- API routes: 95%+
- Model validation: 100%
- Error handling: 95%+

### Generate Coverage Report
```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

## Test Organization

### CRUD Layer Tests (`test_crud.py`)

#### TestVoucherCodeGeneration
- Tests code generation algorithm
- Ensures uniqueness and length
- Validates character set

#### TestCreateVoucher
- Validates successful creation
- Tests discount percentage validation
- Ensures unique codes for each voucher
- Tests various discount values

#### TestGetVoucher
- Tests retrieval by code
- Tests validation (active status, expiration)
- Tests non-existent voucher handling

#### TestListVouchers
- Tests pagination
- Tests various page sizes
- Tests offset calculation

#### TestUpdateVoucher
- Tests updating individual fields
- Tests updating multiple fields
- Tests timestamp updates
- Tests non-existent voucher handling

#### TestDeactivateVoucher
- Tests deactivation
- Tests already inactive vouchers
- Tests timestamp updates

### Routes Layer Tests (`test_routes.py`)

#### TestCreateVoucherRoute
- Tests valid creation requests
- Tests validation errors
- Tests HTTP status codes
- Tests response structure

#### TestListVouchersRoute
- Tests pagination query parameters
- Tests invalid pagination values
- Tests response structure

#### TestGetVoucherRoute
- Tests retrieving active, non-expired vouchers
- Tests 404 errors
- Tests validation

#### TestUpdateVoucherRoute
- Tests PATCH requests
- Tests validation
- Tests partial updates

#### TestDeactivateVoucherRoute
- Tests deactivation endpoint
- Tests response format
- Tests repeated deactivations

#### TestIntegrationScenarios
- Tests complete voucher lifecycle
- Tests bulk operations
- Tests complex workflows

## Key Test Features

### 1. **Isolation**
Each test runs with a fresh, in-memory database:
```python
@pytest.fixture
def db():
    """Database session fixture"""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)
```

### 2. **Reusable Fixtures**
Common test data:
```python
@pytest.fixture
def valid_future_date():
    """Generate a valid future date"""
    return datetime.now() + timedelta(days=30)

@pytest.fixture
def sample_voucher(db, valid_future_date):
    """Create a sample voucher in the database"""
    ...
```

### 3. **Parametrized Tests**
Tests with multiple inputs:
```python
def test_create_voucher_with_various_discounts(self, db, valid_future_date):
    discounts = [1.0, 25.5, 50.0, 75.99, 100.0]
    for discount in discounts:
        ...
```

### 4. **Edge Cases**
- Zero and negative discounts
- Discounts over 100%
- Expired dates
- Missing required fields
- Pagination boundaries

### 5. **Error Handling**
- Invalid input validation
- 404 responses
- 422 validation errors
- Empty lists

### 6. **Integration Tests**
- Complete workflows
- Multi-step operations
- State transitions

## Common Assertions

```python
# Status codes
assert response.status_code == 200
assert response.status_code == 201
assert response.status_code == 404
assert response.status_code == 422

# Response data
assert data["code"] is not None
assert data["active"] is True
assert data["discount_percentage"] == 15.5

# Lists
assert len(data["items"]) == 10
assert data["total"] == 15
assert data["total_pages"] == 2

# Timestamps
assert voucher.created_at is not None
assert voucher.updated_at > voucher.created_at
```

## Debugging Tests

### Print Debug Information
```bash
pytest -v -s tests/test_routes.py::TestCreateVoucherRoute::test_create_voucher_success
```

### Run Single Test with Pdb
```bash
pytest --pdb tests/test_crud.py::TestCreateVoucher::test_create_voucher_success
```

### Show Local Variables in Failure
```bash
pytest -l tests/test_crud.py
```

## Best Practices

1. **One Assertion Per Test**: Each test should verify one behavior
   ```python
   # Good
   def test_create_voucher_success(self):
       ...
       assert voucher.code is not None
   
   # Also test separately
   def test_create_voucher_has_timestamp(self):
       ...
       assert voucher.created_at is not None
   ```

2. **Clear Test Names**: Test names should describe what's being tested
   ```python
   # Good
   def test_create_voucher_with_invalid_discount_returns_validation_error(self)
   
   # Bad
   def test_voucher(self)
   ```

3. **Use Fixtures**: Share common setup
   ```python
   @pytest.fixture
   def sample_voucher(db, valid_future_date):
       return create_voucher(...)
   
   def test_something(self, sample_voucher):
       # sample_voucher is already created
   ```

4. **Test Edge Cases**: Don't just test the happy path
   ```python
   # Good: test boundary values
   def test_discount_percentage_minimum(self):
       # Test 0.01%
   
   def test_discount_percentage_maximum(self):
       # Test 100%
   ```

5. **Keep Tests Fast**: Use in-memory database
   - Tests should complete in seconds, not minutes
   - Use fixtures for setup instead of making API calls

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Tests
  run: |
    pip install -r requirements.txt
    pip install -r tests/requirements.txt
    pytest --cov=app

- name: Generate Coverage Report
  run: pytest --cov=app --cov-report=xml
```

## Troubleshooting

### Port Already in Use
The tests use an in-memory database, not a running server, so this shouldn't happen.

### Import Errors
```bash
# Make sure you're in the project root
cd /path/to/fastapi-voucher-api

# Install all dependencies
pip install -r requirements.txt
pip install -r tests/requirements.txt
```

### Tests Failing After Code Changes
```bash
# Clear any cached pytest files
rm -rf .pytest_cache
pytest --cache-clear
```

### Database Lock Issues
Since we use in-memory SQLite, this shouldn't occur. If it does:
```bash
# Restart pytest
pytest --forked
```

## Performance

- **Total test suite execution**: ~5-10 seconds
- **Single test execution**: ~100-500ms
- **Database operations**: In-memory (very fast)

## Contributing Tests

When adding new features:

1. Write tests first (TDD approach)
2. Implement the feature
3. Ensure all tests pass
4. Maintain 90%+ coverage

### Test Template

```python
class TestNewFeature:
    """Test new feature"""
    
    def test_feature_success(self, client, valid_future_date):
        """Test successful feature execution"""
        response = client.post("/api/v1/path/", json={...})
        assert response.status_code == 201
        assert response.json()["field"] == "expected"
    
    def test_feature_invalid_input(self, client):
        """Test feature with invalid input"""
        response = client.post("/api/v1/path/", json={})
        assert response.status_code == 422
```

## References

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/advanced/testing-events/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/faq/orm.html#i-want-to-test-my-orm-mapped-class)