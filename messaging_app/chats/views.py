# chats/views.py
from rest_framework import viewsets, status, filters  # ADD: filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend  # ADD
from .models import Conversation, Message, ConversationParticipant
from .serializers import (
    ConversationSerializer,
    ConversationCreateSerializer,
    MessageSerializer,
)


class ConversationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]  # "filters"
    filterset_fields = ['created_at']  # Allow filtering by date
    search_fields = ['participants__email']  # Search by participant email
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def list(self, request):
        user = request.user
        queryset = Conversation.objects.filter(participants=user)
        queryset = self.filter_queryset(queryset)  # Apply filters
        queryset = queryset.prefetch_related('participants', 'messages__sender')
        serializer = ConversationSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = ConversationCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            conversation = serializer.save()
            if request.user not in conversation.participants.all():
                ConversationParticipant.objects.create(conversation=conversation, user=request.user)
            return Response(ConversationSerializer(conversation).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        conversation = get_object_or_404(Conversation, conversation_id=pk)
        if not conversation.participants.filter(user_id=request.user.user_id).exists():
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data)


class MessageViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['sent_at', 'sender__email']
    search_fields = ['message_body']
    ordering_fields = ['sent_at']
    ordering = ['sent_at']

    def get_conversation(self, conversation_id):
        conversation = get_object_or_404(Conversation, conversation_id=conversation_id)
        if not conversation.participants.filter(user_id=self.request.user.user_id).exists():
            raise PermissionDenied("Not in conversation.")
        return conversation

    def list(self, request):
        # DefaultRouter doesn't pass conversation_id → list all messages for user
        messages = Message.objects.filter(
            conversation__participants=request.user
        ).select_related('sender', 'conversation').order_by('sent_at')
        messages = self.filter_queryset(messages)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def create(self, request):
        # Expect conversation_id in POST data
        conversation_id = request.data.get('conversation')
        if not conversation_id:
            return Response({"conversation": "This field is required."}, status=400)

        conversation = self.get_conversation(conversation_id)
        data = request.data.copy()
        data['sender_id'] = request.user.user_id

        serializer = MessageSerializer(data=data, context={
            'request': request,
            'conversation_id': conversation_id
        })
        if serializer.is_valid():
            message = serializer.save()
            return Response(MessageSerializer(message).data, status=201)
        return Response(serializer.errors, status=400)