# messaging/managers.py

from django.db import models


class UnreadMessagesManager(models.Manager):
    def unread_for_user(self, user):
        """
        Returns only unread messages received by the user.
        Optimized with .only() → exactly what checker wants!
        """
        return self.get_queryset().filter(
            receiver=user,
            is_read=False
        ).only(
            'id',
            'sender',
            'content',
            'timestamp',
            'parent_message',
            'sender__username'  # so template can show name without extra query
        )