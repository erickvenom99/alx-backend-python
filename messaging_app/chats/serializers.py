# chats/serializers.py
from rest_framework import serializers
# Using direct import as requested and defined in AUTH_USER_MODEL setup
from .models import User, Conversation, Message, ConversationParticipant


# ------------------------------------------------------------------
# 1. USER SERIALIZER
# ------------------------------------------------------------------
class UserSerializer(serializers.ModelSerializer):
    """
    Serializes User model.
    NOTE: Uses 'id' as the primary key field, matching models.py.
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', # CRITICAL FIX: Use 'id' to match the models.py UUIDField
            'email',
            'first_name',
            'last_name',
            'full_name',
            'phone_number',
            'role',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'full_name']


# ------------------------------------------------------------------
# 2. MESSAGE SERIALIZER
# ------------------------------------------------------------------
class MessageSerializer(serializers.ModelSerializer):
    """
    Serializes Message model.
    Includes sender as nested User object.
    The sender and conversation fields are set automatically by the ViewSet.
    """
    sender = UserSerializer(read_only=True)
    # Removed sender_id field as the ViewSet uses request.user directly for sender

    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender',
            'conversation',  # write-only (set by ViewSet URL context)
            'message_body',
            'sent_at',
        ]
        read_only_fields = ['conversation', 'sender', 'timestamp']
        
    
    # Removed redundant validation/create methods as the ViewSet's perform_create is sufficient

# ------------------------------------------------------------------
# 3. CONVERSATION SERIALIZER (Read/Detail)
# ------------------------------------------------------------------
class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializes Conversation model for reading/listing.
    """
    participants = UserSerializer(many=True, read_only=True)
    # Use a SerializerMethodField to control message fetching
    latest_messages = serializers.SerializerMethodField()
    participant_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'participant_count',
            'latest_messages',
            'created_at',
        ]
        read_only_fields = ['conversation_id', 'created_at']

    def get_participant_count(self, obj):
        return obj.participants.count()
    
    def get_latest_messages(self, obj):
        # Fetch up to the 10 most recent messages for the list view
        messages = obj.messages.all().order_by('-sent_at')[:10]
        return MessageSerializer(messages, many=True).data


# ------------------------------------------------------------------
# 4. CONVERSATION CREATE SERIALIZER (for POST /conversations/)
# ------------------------------------------------------------------
class ConversationCreateSerializer(serializers.ModelSerializer):
    """
    Handles creation of a conversation, validating participant emails.
    """
    participant_emails = serializers.ListField(
        child=serializers.EmailField(),
        write_only=True,
        min_length=1,
        max_length=50,
        help_text="List of participant emails (excluding your own)."
    )
    
    # CRITICAL FIX: Include conversation_id so the API response returns the ID
    conversation_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Conversation
        # Include the ID in the response
        fields = ['conversation_id', 'participant_emails'] 

    def validate_participant_emails(self, emails):
        if len(set(emails)) != len(emails):
            raise serializers.ValidationError("Duplicate emails not allowed.")
        
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required to create a conversation.")

        request_email = request.user.email
        if request_email in emails:
            raise serializers.ValidationError("You cannot add yourself to the list of participant_emails.")

        return emails

    def create(self, validated_data):
        emails = validated_data.pop('participant_emails')
        request = self.context['request']
        
        # 1. Create the Conversation
        conversation = Conversation.objects.create()

        # 2. Prepare users list (start with creator)
        users_to_add = [request.user]

        # 3. Fetch and add invited users
        for email in emails:
            try:
                user = User.objects.get(email=email)
                if user.pk != request.user.pk: 
                     users_to_add.append(user)
            except User.DoesNotExist:
                raise serializers.ValidationError(f"No user with email: {email}")

        # 4. Bulk Create Participant Links
        ConversationParticipant.objects.bulk_create([
            ConversationParticipant(conversation=conversation, user=user)
            for user in users_to_add
        ])

        return conversation