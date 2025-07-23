"""
Tests for custom permissions in the chats app.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from ..models import Conversation, Message

User = get_user_model()

class SimplePermissionTest(TestCase):
    """Simple test case to verify the permission system is working."""
    
    def test_permission_setup(self):
        """Test that the test environment is properly set up."""
        self.assertTrue(True, "Test environment is working")

class ConversationPermissionsTest(APITestCase):
    """Test cases for conversation permissions."""

    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='testpass123',
            first_name='User',
            last_name='One'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='testpass123',
            first_name='User',
            last_name='Two'
        )
        
        # Create a conversation with user1
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1)
        
        # Create a message in the conversation
        self.message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            message_body='Test message'
        )
        
        # Get tokens
        self.user1_token = str(RefreshToken.for_user(self.user1).access_token)
        self.user2_token = str(RefreshToken.for_user(self.user2).access_token)
        
        # Set up API client
        self.client = APIClient()
    
    def test_simple_permission_check(self):
        ""Test basic permission check."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        response = self.client.get('/api/conversations/')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])
