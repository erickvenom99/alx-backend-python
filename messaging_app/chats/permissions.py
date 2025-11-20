from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to allow access only to participants of the conversation 
    specified in the URL path (view kwargs). This uses the 'has_permission' 
    method because it checks access to the entire resource endpoint (e.g.,
    /conversations/{pk}/messages/) before any object instance is loaded.
    
    This is applied to the MessageViewSet's list and create actions.
    """
    def has_permission(self, request, view):
        # 1. User must be authenticated (globally enforced, but good check)
        if not request.user or not request.user.is_authenticated:
            return False

        # 2. Extract the conversation ID from the URL path
        conversation_pk = view.kwargs.get('conversation_pk')
        
        # If no conversation PK, deny access (e.g., trying to access a non-nested URL)
        if not conversation_pk:
            return False

        try:
            # 3. Check if the authenticated user is a participant
            from .models import Conversation  # Deferred import to avoid circular dependency
            conversation = Conversation.objects.prefetch_related('participants').get(pk=conversation_pk)
            
            # Returns True if the user is found in the conversation's participants
            return conversation.participants.filter(pk=request.user.pk).exists()

        except Conversation.DoesNotExist:
            # If the conversation doesn't exist, deny access.
            return False

class IsMessageSender(permissions.BasePermission):
    """
    Custom permission to only allow senders of a message to delete it.
    This uses 'has_object_permission' and is applied specifically to the 
    'destroy' action, ensuring the user only deletes *their own* message.
    """
    def has_object_permission(self, request, view, obj):
        # For deletion, the user must be the sender.
        if request.method == 'DELETE':
            return obj.sender == request.user

        # For read-only methods (GET, HEAD, OPTIONS), we rely on 
        # IsParticipantOfConversation at the view level for access.
        return True