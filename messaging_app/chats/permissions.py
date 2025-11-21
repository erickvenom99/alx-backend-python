from rest_framework import permissions
from chats.models import Conversation

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission class that enforces two rules:
    1. The user must be authenticated.
    2. The user must be a participant in the targeted conversation.

    This handles both list/create (has_permission via URL kwargs) and
    retrieve/update/delete (has_object_permission via the message object).
    """

    def has_permission(self, request, view):
        # 1. First, check if the user is authenticated (Rule 1)
        if not request.user or not request.user.is_authenticated:
            return False

        # 2. Check if the action is targeting a specific conversation (Rule 2 for list/create)
        conversation_id = view.kwargs.get('conversation_id')
        
        if not conversation_id:
            # If conversation_id is missing (e.g., if this viewset were used globally),
            # we deny access to prevent system-wide access.
            return False

        try:
            # Retrieve the Conversation object
            conversation = Conversation.objects.get(pk=conversation_id)
        except Conversation.DoesNotExist:
            # If the conversation doesn't exist, permission is denied.
            return False

        # Check if the authenticated user is a participant (M2M check)
        is_participant = conversation.participants.filter(pk=request.user.pk).exists()
        
        return is_participant

    def has_object_permission(self, request, view, obj):
        # The MessageViewSet applies this to individual Message objects (obj).

        # 1. First, check if the user is authenticated (Rule 1)
        if not request.user or not request.user.is_authenticated:
            return False
            
        # 2. Check if the user is a participant in the message's conversation (Rule 2)
        if not hasattr(obj, 'conversation'):
            return False

        conversation = obj.conversation
        
        # Check if the authenticated user is a participant (M2M check)
        is_participant = conversation.participants.filter(pk=request.user.pk).exists()
        
        # Allow any authenticated participant to view/send/update/delete 
        # (based on the requirement: "Allow only participants... to send, view, update and delete messages")
        return is_participant