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
from .permissions import IsMessageSender # 1. Import the custom permission

# Alias PermissionDenied for convenience
PermissionDenied = exceptions.PermissionDenied

class ConversationViewSet(viewsets.ViewSet):
    # This ViewSet uses the URL structure to ensure the user is a participant
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['created_at']
    search_fields = ['participants__email']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    # We implement filter_queryset to allow the use of filter_backends on a custom queryset
    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request):
        user = request.user
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
        conversation = get_object_or_404(Conversation, pk=pk) # Assuming primary key is just 'pk'
        # Explicit check for participation
        if not conversation.participants.filter(user=request.user).exists():
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data)


class MessageViewSet(viewsets.ViewSet):
    # 2. Add IsMessageSender: All actions require authentication. 
    # Write actions (PUT/DELETE) also require the user to be the sender.
    permission_classes = [IsAuthenticated, IsMessageSender] 

    def get_conversation(self):
        """
        Retrieves the conversation based on the URL argument (conversation_pk).
        """
        conversation_pk = self.kwargs.get('conversation_pk')
        try:
            conversation = Conversation.objects.get(pk=conversation_pk)
        except Conversation.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND("Conversation not found.")
        
        # CRITICAL FIX HERE: Filter by the user's ID, not a field named 'user'.
        # We are checking if the current user is a participant of this conversation.
        if not conversation.participants.filter(id=self.request.user.id).exists():
            # If the user is not a participant, raise a permission denied error
            self.permission_denied(
                self.request,
                message="You are not a participant in this conversation."
            )
        
        return conversation

    # Helper method to get the message instance needed for IsMessageSender permission
    def get_object(self):
        """Retrieves the specific message instance."""
        message_pk = self.kwargs.get('pk')
        message = get_object_or_404(Message, pk=message_pk)
        
        # Apply permission check here
        self.check_object_permissions(self.request, message)
        return message

    def perform_create(self, serializer):
        """
        Creates the message, linking it to the conversation and the sender.
        """
        conversation = self.get_conversation()
        serializer.save(sender=self.request.user, conversation=conversation)
        
    def filter_queryset(self, queryset):
        """Stub for filter_queryset required if filter_backends were used."""
        return queryset


    # LIST: Get all messages in a conversation
    def list(self, request, conversation_pk=None):
        conversation = self.get_conversation()
        # NOTE: Updated 'sent_at' to 'timestamp' in order_by to match model changes
        messages = conversation.messages.select_related('sender').order_by('timestamp')
        messages = self.filter_queryset(messages)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    # CREATE: Send a new message (FIXED)
    def create(self, request, conversation_pk=None):
        # get_conversation() already ensures participation and raises 403 if not
        conversation = self.get_conversation() 
        
        # FIX: Pass only the incoming request.data (which contains message_body)
        # The serializer now correctly handles 'conversation' not being in request.data 
        # because we set 'required=False' in serializers.py
        serializer = MessageSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # FIX: Explicitly save the message with the determined sender and conversation object
            message = serializer.save(sender=request.user, conversation=conversation)
            return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # RETRIEVE: Get a single message
    def retrieve(self, request, pk=None, conversation_pk=None):
        message = self.get_object() # Ensures IsMessageSender permission check runs
        serializer = MessageSerializer(message)
        return Response(serializer.data)

    # UPDATE: Update a message (must be sender)
    def update(self, request, pk=None, conversation_pk=None):
        message = self.get_object() # Ensures IsMessageSender permission check runs
        serializer = MessageSerializer(message, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DESTROY: Delete a message (must be sender)
    def destroy(self, request, pk=None, conversation_pk=None):
        message = self.get_object() # Ensures IsMessageSender permission check runs
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)