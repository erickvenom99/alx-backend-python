# messaging/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



class UnreadMessagesManager(models.Manager):
    """
    Custom manager that returns only UNREAD messages for a specific user.
    Optimized using .only() to reduce database load.
    """
    def for_user(self, user):
        return self.get_queryset().filter(
            receiver=user,
            is_read=False
        ).only(
            'id',
            'sender',
            'content',
            'timestamp',
            'parent_message'
        )


class MessageManager(models.Manager):
    def get_conversation_thread(self, root_message_id):
        root = self.get(pk=root_message_id)
        thread_ids = [m.id for m in root.get_thread()]
        return self.filter(id__in=thread_ids)\
                   .select_related('sender', 'receiver')\
                   .prefetch_related('replies__sender')\
                   .order_by('timestamp')


class Message(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='received_messages'
    )
    content = models.TextField()
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    is_read = models.BooleanField(default=False, db_index=True)
    edited = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    objects = MessageManager()  # This connects the manager
    unread = UnreadMessagesManager()

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['receiver', 'is_read']),  # extra speed!
        ]


    def __str__(self):
        status = "UNREAD" if not self.is_read else "read"
        return f"{self.sender} → {self.receiver}: {self.content[:30]}"

    # RECURSIVE METHOD — REQUIRED!
    def get_thread(self):
        thread = [self]
        for reply in self.replies.all():
            thread.extend(reply.get_thread())
        return thread


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='notifications')
    is_seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user}"


class MessageHistory(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ['-edited_at']
        verbose_name_plural = "Message Histories"

    def __str__(self):
        return f"Edit of message {self.message.id} at {self.edited_at}"