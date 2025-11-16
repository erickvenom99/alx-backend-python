#!/usr/bin/env python3

import unittest
from client import GithubOrgClient
from parameterized import parameterized, parameterized_class
from unittest.mock import Mock, patch, PropertyMock
import fixtures
import requests

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

    def test_public_repos_url(self):
        """Test that _public_repos_url returns the expected repos_url
        from the mocked org payload """
        payload = {
            "repos_url": "https://api.github.com/orgs/test-org/repos"
        }

        with patch.object(GithubOrgClient, 'org', new_callable=PropertyMock) as mock_org:
            mock_org.return_value = payload
            client = GithubOrgClient("test-org")
            result = client._public_repos_url
            self.assertEqual(result, payload["repos_url"])
    
    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected_result):
        """Test that has_license returns the expected boolean value."""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected_result)



@parameterized_class([
    {
        "org_payload": fixtures.TEST_PAYLOAD[0][0],
        "repos_payload": fixtures.TEST_PAYLOAD[0][1],
        "expected_repos": fixtures.TEST_PAYLOAD[0][2],
        "apache2_repos": fixtures.TEST_PAYLOAD[0][3],
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test for GithubOrgClient.public_repos."""

    get_patcher = None
    @classmethod
    def setUpClass(cls):
        """
        Patch requests.get to return mocked responses based on URL.
        """
        # Map URLs to their respective payloads
        route_config = {
            "https://api.github.com/orgs/google": cls.org_payload,
            "https://api.github.com/orgs/google/repos": cls.repos_payload,
        }

        def get_side_effect(url):
            """Return a mock response with .json() returning correct payload."""
            payload = route_config.get(url)
            if payload is None:
                raise ValueError(f"No fixture for URL: {url}")

            mock_resp = Mock()
            mock_resp.json.return_value = payload
            mock_resp.status_code = 200
            return mock_resp

        # Patch requests.get with side_effect based on URL
        cls.get_patcher = patch('requests.get', side_effect=get_side_effect)
        cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """Stop the patcher."""
        if cls.get_patcher:
            cls.get_patcher.stop()

@patch('client.get_json')
def test_public_repos(self, mock_get_json):
    """Test public_repos returns all repo names when no license given"""
    # 1. Payloads - must be dict/list, NOT JSON strings
    test_org_payload = {"repos_url": "https://api.github.com/orgs/testorg/repos"}
    test_repos_payload = [
        {"name": "repo1", "private": False},
        {"name": "repo2", "private": False},
        {"name": "repo3", "private": True},
    ]
    expected_repos = ["repo1", "repo2", "repo3"]

    # 2. Mock get_json to return org first, then repos list
    mock_get_json.side_effect = [test_org_payload, test_repos_payload]

    # 3. Mock the property _public_repos_url
    with patch.object(
        GithubOrgClient,
        '_public_repos_url',
        new_callable=PropertyMock,
        return_value=test_org_payload["repos_url"]
    ) as mock_public_repos_url:

        # 4. Test
        client = GithubOrgClient("testorg")
        repos = client.public_repos()

        # 5. Assert
        self.assertEqual(repos, expected_repos)
        self.assertEqual(mock_get_json.call_count, 2)
        mock_public_repos_url.assert_called_once()