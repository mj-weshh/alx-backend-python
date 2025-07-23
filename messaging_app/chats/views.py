import logging
from datetime import datetime
from django.utils import timezone
from django.db.models import Q, Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
from .models import Conversation, Message, User
from .serializers import ConversationListSerializer, ConversationDetailSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation, IsMessageSenderOrReadOnly, IsAdminOrReadOnly

# Set up logging
logger = logging.getLogger(__name__)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and managing conversations.
    - List/Create: Available to authenticated users
    - Retrieve/Update/Delete: Only for conversation participants
    """
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]
    serializer_class = ConversationListSerializer
    lookup_field = 'conversation_id'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['participants__email', 'participants__first_name', 'participants__last_name']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Return conversations where the current user is a participant.
        Optimized with select_related and prefetch_related for performance.
        """
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related(
            Prefetch('participants', queryset=User.objects.only('user_id', 'email', 'first_name', 'last_name')),
            Prefetch('messages', queryset=Message.objects.select_related('sender').order_by('-sent_at')),
        ).order_by('-created_at').distinct()
    
    def get_serializer_class(self):
        """Use different serializers for list and retrieve actions."""
        if self.action == 'retrieve':
            return ConversationDetailSerializer
        return self.serializer_class
    
    def create(self, request, *args, **kwargs):
        """
        Create a new conversation with the specified participants.
        
        The current user is automatically added as a participant.
        """
        participants = request.data.get('participants', [])
        
        # Ensure participants is a list of user IDs
        if not isinstance(participants, list):
            return Response(
                {"participants": ["Expected a list of user IDs."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Add current user to participants if not already included
        current_user_id = str(request.user.user_id)
        if current_user_id not in participants:
            participants.append(current_user_id)
        
        # Get user objects for all participants
        try:
            participant_objs = User.objects.filter(user_id__in=participants)
            if len(participant_objs) != len(set(participants)):  # Check for invalid user IDs
                return Response(
                    {"participants": ["One or more user IDs are invalid."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create conversation
            conversation = Conversation.objects.create()
            conversation.participants.set(participant_objs)
            
            # Return the created conversation
            serializer = self.get_serializer(conversation)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
            
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and creating messages within conversations.
    - List: Messages from conversations where user is a participant
    - Create: Only allowed for conversation participants
    - Retrieve/Update/Delete: Only for message sender or conversation participants
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsMessageSenderOrReadOnly]
    lookup_field = 'message_id'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['message_body', 'sender__email']
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']
    
    def get_queryset(self):
        """
        Return messages from conversations where the current user is a participant.
        Can be filtered by conversation_id.
        """
        # Filter messages where the user is either a participant or the sender
        queryset = Message.objects.filter(
            Q(conversation__participants=self.request.user) |
            Q(sender=self.request.user)
        ).select_related('sender', 'conversation')
        
        # Filter by conversation_id if provided
        conversation_id = self.request.query_params.get('conversation_id')
        if conversation_id:
            # Verify the user is a participant of the conversation
            is_participant = Conversation.objects.filter(
                conversation_id=conversation_id,
                participants=self.request.user
            ).exists()
            
            if not is_participant:
                raise PermissionDenied("You are not a participant of this conversation.")
                
            queryset = Message.objects.filter(conversation_id=conversation_id)
            
        return queryset.distinct()
        
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrParticipant()]
        return super().get_permissions()
        
    def perform_create(self, serializer):
        """Set the sender to the current user and validate conversation participation."""
        conversation = serializer.validated_data['conversation']
        if not conversation.participants.filter(user_id=self.request.user.user_id).exists():
            raise PermissionDenied("You are not a participant of this conversation")
        serializer.save(sender=self.request.user)
        
    def create(self, request, *args, **kwargs):
        """Handle message creation with proper error handling."""
        try:
            response = super().create(request, *args, **kwargs)
            # Optionally update conversation's last_updated timestamp
            conversation_id = request.data.get('conversation')
            if conversation_id:
                Conversation.objects.filter(conversation_id=conversation_id).update(updated_at=timezone.now())
            return response
        except PermissionDenied as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            logger.error(f"Error creating message: {str(e)}")
            return Response(
                {'detail': 'An error occurred while processing your request.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    def destroy(self, request, *args, **kwargs):
        """
        Allow message deletion by sender or conversation participants.
        Implements soft delete if the model supports it.
        """
        try:
            message = self.get_object()
            if hasattr(message, 'is_deleted'):
                # Soft delete if supported
                message.is_deleted = True
                message.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error deleting message: {str(e)}")
            return Response(
                {'detail': 'An error occurred while deleting the message.'},
                status=status.HTTP_400_BAD_REQUEST
            )
