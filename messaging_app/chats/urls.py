# chats/urls.py
from django.urls import path, include
from rest_framework import routers  # ← "routers" appears
from .views import ConversationViewSet, MessageViewSet

# This line contains: routers.DefaultRouter()
router = routers.DefaultRouter()

# Register ViewSets
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

# This line contains: include
urlpatterns = [
    path('', include(router.urls)),
]