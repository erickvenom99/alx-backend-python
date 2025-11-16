# chats/serializers.py
from rest_framework import serializers
from .models import User, Conversation, Message, ConversationParticipant
from django.contrib.auth import get_user_model

User = get_user_model()  # Safely get custom User model


# ------------------------------------------------------------------
# 1. USER SERIALIZER
# ------------------------------------------------------------------
class UserSerializer(serializers.ModelSerializer):
    """
    Serializes User model.
    Used in Conversation.participants and Message.sender.
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'user_id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'phone_number',
            'role',
            'created_at',
        ]
        read_only_fields = ['user_id', 'created_at', 'full_name']


# ------------------------------------------------------------------
# 2. MESSAGE SERIALIZER
# ------------------------------------------------------------------
class MessageSerializer(serializers.ModelSerializer):
    """
    Serializes Message model.
    Includes sender as nested User object.
    """
    sender = UserSerializer(read_only=True)
    sender_id = serializers.UUIDField(write_only=True)  # For creating

    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender',
            'sender_id',
            'conversation',  # write-only
            'message_body',
            'sent_at',
        ]
        read_only_fields = ['message_id', 'sent_at', 'sender']
        extra_kwargs = {
            'conversation': {'write_only': True},
        }

    def validate_sender_id(self, value):
        """Ensure sender exists and is in the conversation."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")

        conversation_id = self.context.get('conversation_id')
        if not conversation_id:
            raise serializers.ValidationError("Conversation context missing.")

        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id)
        except Conversation.DoesNotExist:
            raise serializers.ValidationError("Conversation does not exist.")

        # Check if sender is participant
        if not conversation.participants.filter(user_id=value).exists():
            raise serializers.ValidationError("Sender is not in this conversation.")

        return value

    def create(self, validated_data):
        """Set sender from request.user after validation."""
        request = self.context.get('request')
        validated_data['sender'] = request.user
        return super().create(validated_data)


# ------------------------------------------------------------------
# 3. CONVERSATION SERIALIZER
# ------------------------------------------------------------------
class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializes Conversation model.
    Includes:
      - participants: list of User objects
      - messages: list of Message objects (latest first)
      - participant_count
    """
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True, source='messages')
    participant_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'participant_count',
            'messages',
            'created_at',
        ]
        read_only_fields = ['conversation_id', 'created_at']

    def get_participant_count(self, obj):
        return obj.participants.count()


# ------------------------------------------------------------------
# 4. CONVERSATION CREATE SERIALIZER (for POST /conversations/)
# ------------------------------------------------------------------
class ConversationCreateSerializer(serializers.ModelSerializer):
    """
    Used to create a new conversation.
    Accepts list of participant user_ids (including creator).
    """
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        min_length=2,
        max_length=50
    )

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participant_ids', 'created_at']
        read_only_fields = ['conversation_id', 'created_at']

    def validate_participant_ids(self, value):
        """Ensure all IDs exist and no duplicates."""
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Duplicate participant IDs.")

        users = User.objects.filter(user_id__in=value)
        if users.count() != len(value):
            raise serializers.ValidationError("One or more user IDs are invalid.")

        return value

    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids')
        request = self.context.get('request')

        # Create conversation
        conversation = Conversation.objects.create()

        # Add participants via through model
        participants_to_add = []
        for user_id in participant_ids:
            user = User.objects.get(user_id=user_id)
            participants_to_add.append(
                ConversationParticipant(conversation=conversation, user=user)
            )
        ConversationParticipant.objects.bulk_create(participants_to_add)

        return conversation