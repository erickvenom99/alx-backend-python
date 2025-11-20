# chats/permissions.py
from rest_framework import permissions


class IsParticipant(permissions.BasePermission):
    """
    Allows access only if user is a participant in the conversation.
    Works for both Conversation and Message objects.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user

        if isinstance(obj, Conversation):
            return obj.participants.filter(pk=user.pk).exists()
        
        if hasattr(obj, 'conversation'):
            return obj.conversation.participants.filter(pk=user.pk).exists()
        
        return False


class IsMessageSender(permissions.BasePermission):
    """
    Allows write actions (update/delete) only if user is the message sender.
    Read actions are allowed if IsParticipant passes.
    """
    def has_object_permission(self, request, view, obj):
        # Safe methods: rely on IsParticipant
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write methods: must be the sender
        if hasattr(obj, 'sender'):
            return obj.sender == request.user

        return False