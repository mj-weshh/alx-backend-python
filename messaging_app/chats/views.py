from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Prefetch
from .models import Conversation, Message, User
from .serializers import ConversationListSerializer, ConversationDetailSerializer, MessageSerializer


class IsParticipant(permissions.BasePermission):
    """Custom permission to only allow participants of a conversation to view it."""
    def has_object_permission(self, request, view, obj):
        return request.user in obj.participants.all()


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and managing conversations.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConversationListSerializer
    lookup_field = 'conversation_id'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['participants__email', 'participants__first_name', 'participants__last_name']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return only conversations where the current user is a participant."""
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related(
            Prefetch('participants', queryset=User.objects.only('user_id', 'email', 'first_name', 'last_name')),
            Prefetch('messages', queryset=Message.objects.select_related('sender').order_by('-sent_at'))
        ).order_by('-created_at')
    
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
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]
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
        queryset = Message.objects.select_related(
            'sender', 'conversation'
        ).filter(
            conversation__participants=self.request.user
        ).order_by('-sent_at')
        
        # Filter by conversation_id if provided
        conversation_id = self.request.query_params.get('conversation_id')
        if conversation_id:
            queryset = queryset.filter(conversation_id=conversation_id)
            
        return queryset
    
    def perform_create(self, serializer):
        """Set the sender to the current user and validate conversation participation."""
        conversation = serializer.validated_data['conversation']
        
        # Check if user is a participant in the conversation
        if not conversation.participants.filter(user_id=self.request.user.user_id).exists():
            raise permissions.PermissionDenied(
                "You are not a participant in this conversation."
            )
        
        # Save the message with the current user as sender
        serializer.save(sender=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Handle message creation with proper error handling."""
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
