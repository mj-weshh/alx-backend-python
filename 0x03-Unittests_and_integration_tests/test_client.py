#!/usr/bin/env python3
"""
Test module for client.py
"""
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized

# Import the client to test
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test class for GithubOrgClient"""

    @parameterized.expand([
        ("google",),
        ("abc",)
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the correct value.

        Args:
            org_name: Name of the organization to test
            mock_get_json: Mock for the get_json function
        """
        # Create an instance of GithubOrgClient
        test_client = GithubOrgClient(org_name)
        
        # Call the org property
        test_client.org
        
        # Verify get_json was called once with the correct URL
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)

    def test_public_repos_url(self):
        """Test that _public_repos_url returns the correct value from org"""
        # Define the test payload
        test_payload = {
            "repos_url": "https://api.github.com/orgs/test_org/repos"
        }

        # Mock the org property to return our test payload
        with patch.object(
                GithubOrgClient, 'org',
                new_callable=PropertyMock,
                return_value=test_payload
        ) as mock_org:
            # Create an instance of GithubOrgClient
            test_client = GithubOrgClient("test_org")
            
            # Access the _public_repos_url property
            result = test_client._public_repos_url
            
            # Verify the result is as expected
            self.assertEqual(
                result,
                "https://api.github.com/orgs/test_org/repos"
            )
            
            # Verify the org property was accessed
            mock_org.assert_called_once()


if __name__ == '__main__':
    unittest.main()
