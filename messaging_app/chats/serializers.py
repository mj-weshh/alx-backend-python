from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import User, Message, Conversation


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""
    user_id = serializers.UUIDField(read_only=True)
    role = serializers.ChoiceField(choices=User.Role.choices, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    full_name = serializers.SerializerMethodField()
    phone_number = serializers.CharField(
        max_length=20, 
        required=False, 
        allow_blank=True,
        help_text="User's phone number"
    )

    class Meta:
        model = User
        fields = [
            'user_id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'role', 'created_at'
        ]
        read_only_fields = ['user_id', 'created_at']
        extra_kwargs = {
            'email': {'required': True},
            'password': {'write_only': True, 'required': False}
        }

    def get_full_name(self, obj):
        """Return the full name of the user."""
        return f"{obj.first_name} {obj.last_name}"

    def validate_phone_number(self, value):
        """Validate phone number format."""
        if value and not value.startswith('+'):
            raise serializers.ValidationError(
                "Phone number must start with a country code (e.g., +1, +44)"
            )
        return value

    def create(self, validated_data):
        """Create and return a new user with encrypted password."""
        try:
            password = validated_data.pop('password', None)
            user = User(**validated_data)
            if password:
                user.set_password(password)
            user.save()
            return user
        except DjangoValidationError as e:
            raise serializers.ValidationError(str(e))


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for the Message model."""
    message_id = serializers.UUIDField(read_only=True)
    sender = serializers.SlugRelatedField(
        slug_field='email', 
        queryset=User.objects.all()
    )
    sent_at = serializers.DateTimeField(read_only=True)
    formatted_date = serializers.SerializerMethodField()
    message_type = serializers.CharField(
        default='text',
        help_text="Type of the message (e.g., text, image, file)"
    )
    
    def get_formatted_date(self, obj):
        """Return formatted date string."""
        return obj.sent_at.strftime('%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Message
        fields = [
            'message_id', 'sender', 'message_body', 'message_type',
            'sent_at', 'formatted_date'
        ]
        read_only_fields = ['message_id', 'sent_at', 'formatted_date']


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
