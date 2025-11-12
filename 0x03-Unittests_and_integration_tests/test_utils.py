#!/usr/bin/env python3
"""
checks the result  of access_nested_map function
"""
import unittest
from parameterized import parameterized
from utils import access_nested_map


class TestAccessNestedMap(unittest.TestCase):
    """TestAccessNestedMap class to test access_nested_map function"""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """This mdthod tests access_nested_map function
        Args:
            nested_map (dict): nested map to access
            path (tuple): path to access the value
            expected (any): expected value
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)
