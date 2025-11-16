# chats/urls.py
from django.urls import path, include
from rest_framework import routers
from rest_framework_nested import routers as nested_routers  # ← "NestedDefaultRouter"
from .views import ConversationViewSet, MessageViewSet

# Top-level router
router = routers.DefaultRouter()  # ← "routers.DefaultRouter()"
router.register(r'conversations', ConversationViewSet, basename='conversation')

# Nested router for messages under conversations
conversation_router = nested_routers.NestedDefaultRouter(  # ← "NestedDefaultRouter"
    router, r'conversations', lookup='conversation'
)
conversation_router.register(r'messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversation_router.urls)),  # ← nested routes
]