import json
from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class JWTAuthenticationTests(APITestCase):
    def setUp(self):
        # Create test users
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'user'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.token_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')
        self.logout_url = reverse('auth_logout')
    
    def test_jwt_login_success(self):
        """Test successful JWT login"""
        response = self.client.post(
            self.token_url,
            {'email': 'test@example.com', 'password': 'testpass123'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'test@example.com')
    
    def test_jwt_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post(
            self.token_url,
            {'email': 'wrong@example.com', 'password': 'wrongpass'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_token_refresh(self):
        """Test token refresh"""
        # First get a token
        token_response = self.client.post(
            self.token_url,
            {'email': 'test@example.com', 'password': 'testpass123'},
            format='json'
        )
        refresh_token = token_response.data['refresh']
        
        # Now refresh the token
        response = self.client.post(
            self.refresh_url,
            {'refresh': refresh_token},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_protected_endpoint(self):
        """Test accessing a protected endpoint with JWT"""
        # Get token
        token_response = self.client.post(
            self.token_url,
            {'email': 'test@example.com', 'password': 'testpass123'},
            format='json'
        )
        access_token = token_response.data['access']
        
        # Access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(reverse('conversation-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_logout(self):
        """Test JWT logout (blacklist refresh token)"""
        # Get token
        token_response = self.client.post(
            self.token_url,
            {'email': 'test@example.com', 'password': 'testpass123'},
            format='json'
        )
        refresh_token = token_response.data['refresh']
        
        # Logout
        response = self.client.post(
            self.logout_url,
            {'refresh': refresh_token},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        
        # Try to refresh with blacklisted token
        refresh_response = self.client.post(
            self.refresh_url,
            {'refresh': refresh_token},
            format='json'
        )
        
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)
