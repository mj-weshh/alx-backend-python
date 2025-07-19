#!/usr/bin/env python3
"""Test script to check imports"""

try:
    from parameterized import parameterized
    print("Successfully imported parameterized")
except ImportError as e:
    print(f"Failed to import parameterized: {e}")
    raise
