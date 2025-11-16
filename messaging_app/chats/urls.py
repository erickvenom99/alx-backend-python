# chats/urls.py
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet
from django.urls import path

# Initialize DRF router
router = DefaultRouter()

# Register ViewSets with router
router.register(r'conversations', ConversationViewSet, basename='conversation')

# Nested messages under conversation
# We use a custom route for messages: /conversations/<id>/messages/
message_list = MessageViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

urlpatterns = router.urls + [
    # POST/GET /api/conversations/<conversation_id>/messages/
    path(
        'conversations/<uuid:conversation_id>/messages/',
        message_list,
        name='message-list'
    ),
]