#!/usr/bin/env python3
"""
Test module for client.py
"""
import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class

# Import the client to test
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


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

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test that public_repos returns the correct list of repos"""
        # Define the test payload for get_json
        test_repos = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"}
        ]
        mock_get_json.return_value = test_repos

        # Define the test URL for _public_repos_url
        test_url = "https://mocked.url/org/repos"

        # Mock _public_repos_url to return our test URL
        with patch.object(
                GithubOrgClient, '_public_repos_url',
                new_callable=PropertyMock,
                return_value=test_url
        ) as mock_public_repos_url:
            # Create an instance of GithubOrgClient
            test_client = GithubOrgClient("test_org")

            # Call the public_repos method
            result = test_client.public_repos()

            # Verify the result is as expected
            self.assertEqual(result, ["repo1", "repo2", "repo3"])

            # Verify get_json was called once with the test URL
            mock_get_json.assert_called_once_with(test_url)

            # Verify _public_repos_url was accessed once
            mock_public_repos_url.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test that has_license correctly identifies license presence"""
        # Call the static method
        result = GithubOrgClient.has_license(repo, license_key)

        # Verify the result matches the expected value
        self.assertEqual(result, expected)


@parameterized_class([
    {
        "org_payload": TEST_PAYLOAD[0][0],
        "repos_payload": TEST_PAYLOAD[0][1],
        "expected_repos": TEST_PAYLOAD[0][2],
        "apache2_repos": TEST_PAYLOAD[0][3]
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test class for GithubOrgClient"""

    @classmethod
    def setUpClass(cls):
        """Set up class fixtures before running tests."""
        # Patch requests.get to return our mock responses
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()

        # Define side effect for the mock
        def side_effect(url):
            if url.endswith('/orgs/google'):
                return Mock(json=lambda: cls.org_payload)
            elif url.endswith('/orgs/google/repos'):
                return Mock(json=lambda: cls.repos_payload)
            raise ValueError(f"Unhandled URL: {url}")

        cls.mock_get.side_effect = side_effect

        # Initialize the client once for all tests
        cls.org_client = GithubOrgClient("google")

    @classmethod
    def tearDownClass(cls):
        """Tear down class fixtures after running tests."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test that public_repos returns the expected list of repos."""
        # Call the method under test
        repos = self.org_client.public_repos()

        # Verify the result matches the expected repositories
        self.assertEqual(repos, self.expected_repos)

        # Verify the base URL was called
        # Note: The actual implementation might not include headers and params
        self.mock_get.assert_any_call(
            'https://api.github.com/orgs/google/repos'
        )

    def test_public_repos_with_license(self):
        """Test public_repos with license filter returns expected repos."""
        # Call the method under test with license filter
        repos = self.org_client.public_repos(license="apache-2.0")

        # Verify the result matches the expected repos
        self.assertEqual(repos, self.apache2_repos)

        # Verify the base URL was called
        # Note: The actual implementation might not include headers and params
        self.mock_get.assert_any_call(
            'https://api.github.com/orgs/google/repos'
        )


if __name__ == '__main__':
    unittest.main()
