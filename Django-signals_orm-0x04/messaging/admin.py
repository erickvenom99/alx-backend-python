from django.contrib import admin
from .models import Message, Notification, MessageHistory


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'content_preview', 'timestamp', 'is_read']
    list_filter = ['timestamp', 'is_read']
    search_fields = ['sender__username', 'receiver__username', 'content']

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message_sender', 'created_at', 'is_seen']
    list_filter = ['is_seen', 'created_at']
    search_fields = ['user__username', 'message__sender__username']

    def message_sender(self, obj):
        return obj.message.sender.username
    message_sender.short_description = 'From'

@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ['message', 'edited_by', 'edited_at', 'old_content_preview']
    list_filter = ['edited_at']
    readonly_fields = ['message', 'old_content', 'edited_at', 'edited_by']

    def old_content_preview(self, obj):
        return obj.old_content[:70] + ('...' if len(obj.old_content) > 70 else '')
    old_content_preview.short_description = 'Old Content'


