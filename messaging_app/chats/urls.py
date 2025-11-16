# chats/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet

# Initialize DRF router
router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')

# Register MessageViewSet with custom basename
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    # Include all router-generated URLs
    path('', include(router.urls)),

    # Optional: Keep nested messages (extra credit)
    # But router already gives /messages/ — we keep it simple
]