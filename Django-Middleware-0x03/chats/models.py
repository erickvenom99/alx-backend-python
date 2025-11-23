# messaging_app/chats/models.py
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MinLengthValidator


class User(AbstractUser):
    """
    Custom User with UUID primary key — THE CORRECT WAY
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    # Remove your old 'user_id' field completely
    # → Just rename it to 'id'

    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    ROLE_CHOICES = [('guest', 'Guest'), ('host', 'Host'), ('admin', 'Admin')]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='guest')
    
    created_at = models.DateTimeField(auto_now_add=True)

    # Fix related_name conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='chats_user_groups',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='chats_user_permissions',
        blank=True
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def __str__(self):
        return self.email

class Conversation(models.Model):
    """
    Represents a conversation between multiple users.
    """
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
        
    )
    participants = models.ManyToManyField(
        User,
        related_name='conversations',
        through='ConversationParticipant',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'conversation'
        indexes = [
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        participant_names = ", ".join([str(p) for p in self.participants.all()[:3]])
        return f"Conversation {self.conversation_id} ({participant_names})"


class ConversationParticipant(models.Model):
    """
    Through model for Conversation.participants (ManyToMany).
    Allows additional fields later (e.g., joined_at, is_admin).
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversation_participations')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'conversation_participant'
        unique_together = ('conversation', 'user')
        indexes = [
            models.Index(fields=['conversation', 'user']),
        ]

    def __str__(self):
        return f"{self.user.email} in {self.conversation}"


class Message(models.Model):
    """
    A single message in a conversation.
    """
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        db_index=True,
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        db_index=True
    )
    message_body = models.TextField(
        blank=False,
        null=False,
        validators=[MinLengthValidator(1)]
    )
    sent_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'message'
        indexes = [
            models.Index(fields=['conversation', 'sent_at']),
            models.Index(fields=['sender']),
        ]
        ordering = ['sent_at']

    def __str__(self):
        return f"Message {self.message_id} by {self.sender.email}"