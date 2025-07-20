# Unit Tests and Integration Tests in Python

This directory contains Python code and tests demonstrating unit testing and integration testing practices using Python's built-in `unittest` framework and the `parameterized` package.

## 📁 Directory Structure

```
0x03-Unittests_and_integration_tests/
├── __init__.py         # Makes the directory a Python package
├── client.py           # GitHub API client implementation
├── fixtures.py         # Test fixtures and mock data
├── requirements.txt    # Project dependencies
├── run_tests.py        # Standalone test runner
├── test_import.py      # Test script for dependency verification
├── test_utils.py       # Unit tests for utility functions
└── utils.py            # Utility functions being tested
```

## 🧪 Test Files Overview

### `test_utils.py`
Contains unit tests for the utility functions in `utils.py`:

1. **TestAccessNestedMap**: Parameterized tests for the `access_nested_map` function that verify:
   - Accessing top-level keys in a nested dictionary
   - Retrieving nested dictionaries
   - Accessing deeply nested values

2. **TestMemoize**: Tests for the `memoize` decorator that verify:
   - Method results are cached after first call
   - Subsequent calls return cached result without re-execution
   - Property behavior works as expected

### `run_tests.py`
A standalone test runner that can be executed directly. This is particularly useful when there are import issues with the main test file.

### `fixtures.py`
Contains test data and fixtures used across multiple test files, including sample GitHub API responses.

## 🛠️ Dependencies

The project requires the following Python packages:
- `parameterized` (>=0.9.0) - For parameterized testing
- `requests` (>=2.31.0) - For making HTTP requests

Install dependencies using:
```bash
pip install -r requirements.txt
```

## 🚀 Running Tests

### Running All Tests
```bash
python -m unittest discover -s 0x03-Unittests_and_integration_tests -p "test_*.py" -v
```

### Running Specific Test File
```bash
python -m 0x03-Unittests_and_integration_tests.test_utils -v
```

### Using the Standalone Test Runner
```bash
python 0x03-Unittests_and_integration_tests/run_tests.py -v
```

## 🧠 Key Concepts

### Parameterized Testing
Tests are written using the `@parameterized.expand` decorator to run the same test logic with different inputs.

### Test Organization
- Tests are organized in classes that inherit from `unittest.TestCase`
- Each test method starts with `test_`
- Test methods are documented with docstrings explaining their purpose

### Fixtures
Test data is centralized in `fixtures.py` to avoid duplication and make tests more maintainable.

## 📝 Notes

- The `access_nested_map` function safely accesses nested dictionary values using a sequence of keys.
- The test suite includes edge cases and error handling scenarios.
- The project follows Python best practices for testing and code organization.

## 🧪 Testing Best Practices

1. **Isolation**: Each test should be independent
2. **Readability**: Clear test names and docstrings
3. **Coverage**: Test both happy paths and edge cases
4. **Performance**: Tests should be fast and efficient
5. **Maintainability**: Keep test code clean and well-documented
