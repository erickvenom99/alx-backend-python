from rest_framework import viewsets, status, filters, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from .models import Conversation, Message, ConversationParticipant
from .serializers import (
    ConversationSerializer,
    ConversationCreateSerializer,
    MessageSerializer,
)
# 1. Import the newly defined custom permission
from .permissions import IsParticipantOfConversation 

# Alias PermissionDenied for convenience
PermissionDenied = exceptions.PermissionDenied

class ConversationViewSet(viewsets.ViewSet):
    # Standard authentication check is sufficient for list/create 
    # (Global default IsAuthenticated will also be active from settings.py)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['created_at']
    search_fields = ['participants__email']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request):
        user = request.user
        # Queryset already filters to only show conversations the user participates in
        queryset = Conversation.objects.filter(participants=user)
        queryset = self.filter_queryset(queryset)
        queryset = queryset.prefetch_related('participants', 'messages__sender')
        serializer = ConversationSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = ConversationCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            conversation = serializer.save()
            # Ensure the creator is a participant
            if request.user not in conversation.participants.all():
                ConversationParticipant.objects.create(conversation=conversation, user=request.user)
            return Response(ConversationSerializer(conversation).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        conversation = get_object_or_404(Conversation, pk=pk)
        
        # Explicit M2M check for participation in this specific conversation
        if not conversation.participants.filter(pk=request.user.pk).exists():
            return Response({"detail": "Not authorized to view this conversation."}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing Message instances associated with a specific Conversation.
    
    The IsParticipantOfConversation class enforces that only authenticated participants
    can interact with the messages within the conversation specified by conversation_id.
    """
    serializer_class = MessageSerializer
    
    # Apply the custom permission to enforce access control (only participants can interact)
    permission_classes = [IsParticipantOfConversation] 

    def get_queryset(self):
        conversation_id = self.kwargs.get('conversation_id')
        
        if conversation_id:
            # Filter the Message objects to show only messages in that conversation, ordered by timestamp
            return Message.objects.filter(conversation__id=conversation_id).order_by('timestamp')
        
        # If no conversation ID is present, return an empty queryset
        return Message.objects.none()

    def perform_create(self, serializer):
        conversation_id = self.kwargs.get('conversation_id')
        
        # Retrieve the Conversation instance
        try:
            conversation = Conversation.objects.get(pk=conversation_id)
        except Conversation.DoesNotExist:
            raise serializer.ValidationError("Invalid conversation ID.")
            
        # Save the message, linking it to the conversation and the current user
        serializer.save(
            sender=self.request.user, 
            conversation=conversation
        )