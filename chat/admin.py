from django.contrib import admin
from .models import Chat, Message

class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user1', 'user2', 'chat_key', 'vacancy')
    list_filter = ('vacancy',)
    search_fields = ('title', 'chat_key', 'user1__username', 'user2__username', 'vacancy__title')
    readonly_fields = ('chat_key',)

class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'sender', 'content_preview', 'sent_date', 'updated_date', 'status')
    list_filter = ('status', 'sent_date')
    search_fields = ('content', 'sender__username', 'chat__chat_key')
    date_hierarchy = 'sent_date'
    readonly_fields = ('sent_date',)
    
    def content_preview(self, obj):
        if len(obj.content) > 50:
            return f"{obj.content[:50]}..."
        return obj.content
    
    content_preview.short_description = 'Content'

admin.site.register(Chat, ChatAdmin)
admin.site.register(Message, MessageAdmin)
