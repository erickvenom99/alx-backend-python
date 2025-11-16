# chats/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Conversation, Message, ConversationParticipant
from .serializers import (
    ConversationSerializer,
    ConversationCreateSerializer,
    MessageSerializer,
    UserSerializer,
)


# ------------------------------------------------------------------
# 1. CONVERSATION VIEWSET
# ------------------------------------------------------------------
class ConversationViewSet(viewsets.ViewSet):
    """
    API endpoints:
    - GET    /api/v1/conversations/           → list user's conversations
    - POST   /api/v1/conversations/           → create new conversation
    - GET    /api/v1/conversations/{id}/      → retrieve one conversation
    """
    permission_classes = [IsAuthenticated]

    # ------------------------------------------------------------------
    # LIST: GET /api/v1/conversations/
    # ------------------------------------------------------------------
    def list(self, request):
        """
        Return all conversations the authenticated user is part of.
        """
        user = request.user
        conversations = Conversation.objects.filter(
            participants=user
        ).prefetch_related('participants', 'messages__sender').order_by('-created_at')

        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)

    # ------------------------------------------------------------------
    # CREATE: POST /api/v1/conversations/
    # ------------------------------------------------------------------
    def create(self, request):
        """
        Create a new conversation with participant_ids (including self).
        """
        serializer = ConversationCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            conversation = serializer.save()
            # Ensure creator is added
            if request.user not in conversation.participants.all():
                ConversationParticipant.objects.create(
                    conversation=conversation,
                    user=request.user
                )
            return Response(
                ConversationSerializer(conversation).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------
    # RETRIEVE: GET /api/v1/conversations/{id}/
    # ------------------------------------------------------------------
    def retrieve(self, request, pk=None):
        """
        Get a single conversation if user is a participant.
        """
        conversation = get_object_or_404(Conversation, conversation_id=pk)
        if not conversation.participants.filter(user_id=request.user.user_id).exists():
            return Response(
                {"detail": "You are not a participant in this conversation."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data)


# ------------------------------------------------------------------
# 2. MESSAGE VIEWSET (Nested under Conversation)
# ------------------------------------------------------------------
class MessageViewSet(viewsets.ViewSet):
    """
    API endpoints:
    - POST   /api/v1/conversations/{conv_id}/messages/  → send message
    - GET    /api/v1/conversations/{conv_id}/messages/  → list messages
    """
    permission_classes = [IsAuthenticated]

    # ------------------------------------------------------------------
    # LIST: GET /conversations/{conv_id}/messages/
    # ------------------------------------------------------------------
    def list(self, request, conversation_id=None):
        """
        List all messages in a conversation (user must be participant).
        """
        conversation = get_object_or_404(Conversation, conversation_id=conversation_id)
        if not conversation.participants.filter(user_id=request.user.user_id).exists():
            return Response(
                {"detail": "Not authorized."},
                status=status.HTTP_403_FORBIDDEN
            )

        messages = conversation.messages.select_related('sender').order_by('sent_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    # ------------------------------------------------------------------
    # CREATE: POST /conversations/{conv_id}/messages/
    # ------------------------------------------------------------------
    def create(self, request, conversation_id=None):
        """
        Send a message to a conversation.
        """
        conversation = get_object_or_404(Conversation, conversation_id=conversation_id)
        if not conversation.participants.filter(user_id=request.user.user_id).exists():
            return Response(
                {"detail": "You are not in this conversation."},
                status=status.HTTP_403_FORBIDDEN
            )

        data = request.data.copy()
        data['conversation'] = conversation_id
        data['sender_id'] = request.user.user_id

        serializer = MessageSerializer(
            data=data,
            context={
                'request': request,
                'conversation_id': conversation_id
            }
        )
        if serializer.is_valid():
            message = serializer.save()
            return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)