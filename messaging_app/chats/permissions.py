from rest_framework import permissions

class IsOwnerOrParticipant(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    For messages/conversations, participants can view but only owners can modify.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD, or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            # Check if user is a participant for conversations
            if hasattr(obj, 'participants'):
                return request.user in obj.participants.all()
            # For messages, check if user is the sender or in the conversation
            elif hasattr(obj, 'conversation') and hasattr(obj, 'sender'):
                return (request.user == obj.sender or 
                        request.user in obj.conversation.participants.all())
            return True

        # Write permissions are only allowed to the owner of the object.
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'sender'):
            return obj.sender == request.user
        return False

class IsMessageParticipant(permissions.BasePermission):
    """
    Permission to only allow participants of a conversation to view its messages.
    """
    def has_object_permission(self, request, view, obj):
        return request.user in obj.conversation.participants.all()
