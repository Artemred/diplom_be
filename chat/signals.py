from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from .models import Chat, Message
from .serializers import ChatSerializer
from asgiref.sync import sync_to_async


@receiver(post_save, sender=Chat)
async def chat_room_created_or_updated_handler(sender, instance, created, **kwargs): 
    if created:
        channel_layer = get_channel_layer()
        serializer = ChatSerializer(instance)
        event_payload = await sync_to_async(lambda:serializer.data)()
        await channel_layer.group_send(
            "chat_list_updates_"+str(instance.user1.pk),
            {
                "type": "chat.list.activity",
                "event": "chat_created",
                "chat_data": event_payload,
            },
        )
        await channel_layer.group_send(
            "chat_list_updates_"+str(instance.user2.pk),
            {
                "type": "chat.list.activity",
                "event": "chat_created",
                "chat_data": event_payload,
            },
        )
    else:  # TODO rename handler
        pass

@receiver(pre_delete, sender=Chat)
async def chat_room_deleted_handler(sender, instance, **kwargs):   
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        "chat_list_updates_"+str(instance.user1_id), 
        {
            "type": "chat.list.activity",
            "event": "chat_deleted",
            "chat_key": instance.chat_key,
        },
    )
    await channel_layer.group_send(
        "chat_list_updates_"+str(instance.user2_id),
        {
            "type": "chat.list.activity",
            "event": "chat_deleted",
            "chat_key": instance.chat_key,
        },
    )

@receiver(post_save, sender=Message)
async def chat_list_last_message_update(sender, instance, **kwargs):
    message = instance.content
    chat = await sync_to_async(lambda:instance.chat)()
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        "chat_list_updates_"+str(chat.user1_id),
        {"type": "chat.list.activity",
         "event": "last_update",
         "chat_key": chat.chat_key,
         "new_message":message}
    )
    await channel_layer.group_send(
        "chat_list_updates_"+str(chat.user2_id),
        {"type": "chat.list.activity",
         "event": "last_update",
         "chat_key": chat.chat_key,
         "new_message":message}
    )