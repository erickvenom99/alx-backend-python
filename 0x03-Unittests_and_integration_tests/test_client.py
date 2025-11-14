#!/usr/bin/env python3

import unittest
from client import GithubOrgClient
from parameterized import parameterized
from unittest.mock import patch, PropertyMock

class TestGithubOrgClient(unittest.TestCase):
    """ """
    @parameterized.expand([
        ("google", {"repos_url": ""}),
        ("abc", {"repos_url": ""}),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, expected_payload, mock_get_json):
        """ """
        mock_get_json.return_value = expected_payload
        client = GithubOrgClient(org_name)
        result = client.org
        self.assertEqual(result, expected_payload)
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)
