from rest_framework import serializers
from .models import User, Message, Conversation


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""
    user_id = serializers.UUIDField(read_only=True)
    role = serializers.ChoiceField(choices=User.Role.choices, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        fields = [
            'user_id', 'email', 'first_name', 'last_name', 
            'phone_number', 'role', 'created_at'
        ]
        read_only_fields = ['user_id', 'created_at']
        extra_kwargs = {
            'email': {'required': True},
            'password': {'write_only': True, 'required': False}
        }

    def create(self, validated_data):
        """Create and return a new user with encrypted password."""
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for the Message model."""
    message_id = serializers.UUIDField(read_only=True)
    sender = serializers.SlugRelatedField(
        slug_field='email', 
        queryset=User.objects.all()
    )
    sent_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'message_body', 'sent_at']
        read_only_fields = ['message_id', 'sent_at']


class ConversationListSerializer(serializers.ModelSerializer):
    """Serializer for listing conversations with basic info."""
    conversation_id = serializers.UUIDField(read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'created_at']
        read_only_fields = ['conversation_id', 'created_at']


class ConversationDetailSerializer(ConversationListSerializer):
    """Serializer for detailed conversation view including messages."""
    messages = MessageSerializer(many=True, read_only=True)

    class Meta(ConversationListSerializer.Meta):
        fields = ConversationListSerializer.Meta.fields + ['messages']
