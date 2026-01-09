from django.contrib import admin
from .models import Message, Conversation, Call

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_participants', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('participants__username',)
    
    def get_participants(self, obj):
        return ", ".join([p.username for p in obj.participants.all()])
    get_participants.short_description = 'Participants'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'conversation', 'content_preview', 'created_at', 'is_read')
    list_filter = ('created_at', 'is_read')
    search_fields = ('sender__username', 'content')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Message'

@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    list_display = ('caller', 'receiver', 'call_type', 'status', 'started_at', 'duration')
    list_filter = ('call_type', 'status', 'started_at')
    search_fields = ('caller__username', 'receiver__username')
