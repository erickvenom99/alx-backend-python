from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification


class MessageNotificationTestCase(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username='alice', password='123')
        self.receiver = User.objects.create_user(username='bob', password='123')

    def test_notification_created_on_new_message(self):
        """Test that a notification is created when a message is sent"""
        Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello Bob!"
        )

        # Check that one notification was created for Bob
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.receiver)
        self.assertEqual(notification.message.sender, self.sender)
        self.assertFalse(notification.is_seen)

    def test_no_notification_for_self_message(self):
        """No notification if user sends message to themselves"""
        Message.objects.create(
            sender=self.sender,
            receiver=self.sender,
            content="Note to self"
        )
        self.assertEqual(Notification.objects.count(), 0)