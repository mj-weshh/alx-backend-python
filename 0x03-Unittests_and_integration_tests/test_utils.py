#!/usr/bin/env python3
"""Test cases for access_nested_map function."""

import unittest
from parameterized import parameterized
from unittest.mock import patch, Mock
from utils import memoize
from utils import get_json
from utils import access_nested_map


class TestAccessNestedMap(unittest.TestCase):
    """This decorator takes a list of test cases and runs the
    test method for each case."""
    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test method to receive parameters from the decorator."""
        result = access_nested_map(nested_map, path)
        self.assertEqual(result, expected)

    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected_key):
        """Test that a KeyError is raised for invalid paths."""
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
        # The exception message should be the problematic key
        self.assertEqual(str(context.exception), repr(expected_key))


class TestGetJson(unittest.TestCase):
    """Test class for get_json function"""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('utils.requests.get')
    def test_get_json(self, test_url, test_payload, mock_get):
        """Test get_json function with mocked requests.get"""
        # mock_get is the fake requests.get function
        # Create a mock response object
        mock_response = Mock()
        mock_response.json.return_value = test_payload

        # Make mock_get return this mock response
        mock_get.return_value = mock_response

        # Call the actual get_json function
        result = get_json(test_url)

        # Verify requests.get was called exactly once with the right URL
        mock_get.assert_called_once_with(test_url)

        # Verify the result equals the expected payload
        self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Test Clas for the memoize decorator.
    Testing the correct result, caching behaviour and
    mock verification."""

    def test_memoize(self):
        """Test that the memoize decrator works as expected."""

        class TestClass:
            """Demostrates the memoization pattern I want to test"""
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        with patch.object(TestClass, 'a_method',
                          return_value=42) as mock_method:
            # Create an instance of the test class
            test_instance = TestClass()

            # Access the memoized property twice
            result1 = test_instance.a_property
            result2 = test_instance.a_property

            # Both calls should return the same value
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)

            # The method should only be called once
            mock_method.assert_called_once()
