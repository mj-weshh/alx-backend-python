#!/usr/bin/env python3
"""
Test module for utils.py
"""
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized

# Import the functions to test
from utils import access_nested_map, memoize


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

            @memoize
            def a_method(self):
                self.call_count += 1
                return 42

        # Create instance and test method
        test_obj = TestClass()
        
        # First call - should increment call_count
        self.assertEqual(test_obj.a_method, 42)
        self.assertEqual(test_obj.call_count, 1)
        
        # Second call - should return cached result
        self.assertEqual(test_obj.a_method, 42)
        self.assertEqual(test_obj.call_count, 1)
        
        # Third call - should still return cached result
        self.assertEqual(test_obj.a_method, 42)
        self.assertEqual(test_obj.call_count, 1)
        
        # Verify the method was only called once
        self.assertEqual(test_obj.call_count, 1)


if __name__ == '__main__':
    unittest.main()
