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
# 1. Import all custom permissions
from .permissions import IsMessageSender, IsParticipantOfConversation 

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
        # NOTE: This manual check is still needed here since IsParticipantOfConversation isn't applied to this ViewSet
        if not conversation.participants.filter(user=request.user).exists():
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data)


class MessageViewSet(viewsets.ViewSet):
    
    # REMOVED: Replaced with get_permissions for conditional access
    # permission_classes = [IsAuthenticated, IsMessageSender] 

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions required for the action.
        Uses IsParticipantOfConversation for all access, and adds IsMessageSender 
        specifically for the 'destroy' action.
        """
        # All message actions require the user to be a participant of the parent conversation
        permission_classes = [IsParticipantOfConversation]
        
        if self.action == 'destroy':
            # Only the sender can delete the message
            permission_classes.append(IsMessageSender)
        
        # Only check if the user is authenticated globally (via settings.py), 
        # IsParticipantOfConversation covers the rest.
        
        return [permission() for permission in permission_classes]

    def get_conversation(self):
        """
        Retrieves the conversation based on the URL argument (conversation_pk).
        NOTE: The explicit check for user participation has been REMOVED here, 
        as it is now handled by IsParticipantOfConversation in get_permissions.
        """
        conversation_pk = self.kwargs.get('conversation_pk')
        try:
            conversation = Conversation.objects.get(pk=conversation_pk)
        except Conversation.DoesNotExist:
            raise exceptions.NotFound(detail="Conversation not found.")
        
        return conversation

    # Helper method to get the message instance needed for IsMessageSender permission
    def get_object(self):
        """Retrieves the specific message instance."""
        message_pk = self.kwargs.get('pk')
        message = get_object_or_404(Message, pk=message_pk)
        
        # Apply permission check here (this triggers IsMessageSender for the destroy action)
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
        # Access is checked by IsParticipantOfConversation before this method runs
        conversation = self.get_conversation() 
        messages = conversation.messages.select_related('sender').order_by('timestamp')
        messages = self.filter_queryset(messages)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    # CREATE: Send a new message
    def create(self, request, conversation_pk=None):
        # Access is checked by IsParticipantOfConversation before this method runs
        conversation = self.get_conversation() 
        
        serializer = MessageSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            message = serializer.save(sender=request.user, conversation=conversation)
            return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # RETRIEVE: Get a single message
    def retrieve(self, request, pk=None, conversation_pk=None):
        # NOTE: get_object() automatically triggers the object permissions check
        message = self.get_object() 
        serializer = MessageSerializer(message)
        return Response(serializer.data)

    # UPDATE: Update a message (must be sender)
    def update(self, request, pk=None, conversation_pk=None):
        # NOTE: get_object() automatically triggers the object permissions check (IsMessageSender)
        message = self.get_object() 
        serializer = MessageSerializer(message, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DESTROY: Delete a message (must be sender)
    def destroy(self, request, pk=None, conversation_pk=None):
        # NOTE: get_object() automatically triggers the object permissions check (IsMessageSender)
        message = self.get_object() 
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)