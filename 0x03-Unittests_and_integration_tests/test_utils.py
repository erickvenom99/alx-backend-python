#!/usr/bin/env python3
"""
checks the result  of access_nested_map function
"""
import unittest
import requests
from parameterized import parameterized
from unittest.mock import patch
from utils import access_nested_map,  get_json, memoize


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

    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(self, nested_map, path, expect):
        """This method tests access_nested_map function for exception"""
        with self.assertRaises(KeyError) as cfx:
            access_nested_map(nested_map, path)
        self.assertEqual(f"'{expect}'", str(cfx.exception))


class TestGetJson(unittest.TestCase):
    """This class test the get_json function """
    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
        ])
    def test_get_json(self, test_url, test_payload):
        """ Test return the expected payload
            Args:
                url: str, contains the request address
                payload: boolean returns the objcet  true or false
        """
        with patch('requests.get') as test_get:
            test_get.return_value.json.return_value = test_payload
            result = get_json(test_url)
            self.assertEqual(result, test_payload)
            test_get.assert_called_once_with(test_url)


class TestMemoize(unittest.TestCase):
    """Test the decorator memoize"""
    def test_memoize(self):
        """Test that memoize caches result and calls method only once."""
        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()
        with patch.object(
            TestClass,
            'a_method',
            return_value=42
        )as mock_method:
            obj = TestClass()
            first_result = obj.a_property
            second_result = obj.a_property
            self.assertEqual(first_result, 42)
            self.assertEqual(second_result, 42)
            mock_method.assert_called_once()
