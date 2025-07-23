from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Permission to only allow participants of a conversation to access it.
    Works for both Conversation and Message objects.
    """
    message = 'You must be a participant of this conversation.'
    
    def has_permission(self, request, view):
        # This permission is only checked at the object level
        return True
    
    def has_object_permission(self, request, view, obj):
        # For Conversation objects
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        
        # For Message objects
        if hasattr(obj, 'conversation') and hasattr(obj.conversation, 'participants'):
            return request.user in obj.conversation.participants.all()
        
        return False

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an 'owner' attribute.
    """
    message = 'You must be the owner to perform this action.'

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to the owner
        return obj.owner == request.user

class IsMessageSenderOrReadOnly(permissions.BasePermission):
    """
    Permission to only allow the sender of a message to edit or delete it.
    Read-only access is allowed for conversation participants.
    """
    message = 'You must be the sender of this message to modify it.'
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            # Verify user is a participant of the conversation
            return request.user in obj.conversation.participants.all()
            
        # Write permissions are only allowed to the message sender
        return obj.sender == request.user

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allows read-only access to any request, but write access only to admin users.
    """
    message = 'Admin privileges required to perform this action.'
    
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to admin users
        return request.user and request.user.is_staff
