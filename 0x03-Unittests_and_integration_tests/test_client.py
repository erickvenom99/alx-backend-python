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


    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """
        Test GithubOrgClient.public_repos returns all repo names (no license filter).
        Mocks the public_repos_url property and the get_json function.
        """
        # 1. Payloads
        org_url = "https://api.github.com/orgs/testorg/repos"
        repos_payload = [
            {"name": "repo1", "private": False, "license": None},
            {"name": "repo2", "private": False, "license": None},
            {"name": "repo3", "private": True, "license": None},
        ]
        expected_repos = ["repo1", "repo2", "repo3"]

        # 2. get_json returns: ONLY the repos payload is needed, as the org call
        #    is implicitly avoided by mocking _public_repos_url.
        mock_get_json.return_value = repos_payload
        
        # 3. Mock _public_repos_url property (context manager)
        # We need to patch the property so that public_repos can get the URL
        # without calling client.org.
        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=PropertyMock,
            return_value=org_url
        ) as mock_prop:

            client = GithubOrgClient("testorg")
            result = client.public_repos()

            # 4. Assertions
            self.assertEqual(result, expected_repos)
            
            # get_json is called once by client.repos_payload()
            mock_get_json.assert_called_once_with(org_url)
            
            # _public_repos_url property is accessed once
            mock_prop.assert_called_once()