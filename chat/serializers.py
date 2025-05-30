from adrf.serializers import ModelSerializer
from .models import Message, Chat
from rest_framework.serializers import SlugRelatedField

class MessageSerializer(ModelSerializer):
    sender = SlugRelatedField(slug_field="username", read_only=True)
    class Meta:
        model = Message
        fields = ["pk", "content", "sent_date", "sender", "status"] 


class ChatSerializer(ModelSerializer):
    last_message = SlugRelatedField(slug_field="content", read_only=True)
    class Meta:
        model = Chat
        fields = ["title", "chat_key", "last_message", "vacancy"]