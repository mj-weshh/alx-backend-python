#!/usr/bin/env python3
"""
Test module for utils.py
"""
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized

# Import the functions to test
from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """Test class for access_nested_map function"""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2)
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test access_nested_map with different inputs"""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), 'a'),
        ({"a": 1}, ("a", "b"), 'b')
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected_key):
        """Test access_nested_map raises KeyError with correct message"""
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
        self.assertEqual(str(context.exception), f"'{expected_key}'")


class TestMemoize(unittest.TestCase):
    """Test class for memoize decorator"""

    def test_memoize(self):
        """Test that the memoize decorator caches the result"""
        class TestClass:
            def __init__(self):
                self.call_count = 0

            def a_method(self):
                self.call_count += 1
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        # Create instance of TestClass
        test_obj = TestClass()

        # Patch the a_method to track calls and return 42
        with patch.object(TestClass, 'a_method',
                         return_value=42) as mock_method:
            # First call to a_property
            self.assertEqual(test_obj.a_property, 42)

            # Second call to a_property - should use cached result
            self.assertEqual(test_obj.a_property, 42)

            # Verify a_method was only called once due to memoization
            mock_method.assert_called_once()

            # Verify the method was only called once
            self.assertEqual(mock_method.call_count, 1)

            # Verify the return value is correct
            self.assertEqual(mock_method.return_value, 42)


class TestGetJson(unittest.TestCase):
    """Test class for get_json function"""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False})
    ])
    @patch('requests.get')
    def test_get_json(self, test_url, test_payload, mock_get):
        """Test get_json returns the expected result.

        Args:
            test_url: URL to test
            test_payload: Expected JSON payload
            mock_get: Mock for requests.get
        """
        # Create a mock response object with a json method
        mock_response = unittest.mock.Mock()
        mock_response.json.return_value = test_payload

        # Configure the mock to return the mock response
        mock_get.return_value = mock_response

        # Call the function under test
        result = get_json(test_url)

        # Assert that requests.get was called exactly once
        mock_get.assert_called_once_with(test_url)

        # Assert that the function returns the expected payload
        self.assertEqual(result, test_payload)


if __name__ == '__main__':
    unittest.main()
