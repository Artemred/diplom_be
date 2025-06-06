import json

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Chat, Message
from cauth.models import User
from .serializers import MessageSerializer, ChatSerializer
from urllib.parse import parse_qs
from django.db.models import Q
from cauth.serializers import WhoamiProfileSerializer


class GeneralConsumer(AsyncWebsocketConsumer):
    async def _authorize(self):
        token = parse_qs(self.scope.get("query_string", b"")).get(b"authorization", b"")
        if token:
            token = str(token[0]).split(" ")[-1][:-1]  # because of format "Token #####"
            try:
                user = await User.objects.prefetch_related("auth_token").aget(auth_token__key=token)
                if self.chat_instance.user1.pk == user.pk or self.chat_instance.user2.pk == user.pk:
                    return user
                else:
                    return False
            except User.DoesNotExist:
                return False
        else:
            return False


class ChatConsumer(GeneralConsumer):  
    async def connect(self): 
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        self.chat_instance = await Chat.objects.select_related("user1", "user2").aget(chat_key=self.room_name)
        authorized = await self._authorize()
        if authorized:
            self.user = authorized
            await self.accept()
        else:
            await self.close(code=4001, reason="Authorization error")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)  # deletes channel
        super().disconnect(close_code)

    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        msg_type = text_data_json.get("type")

        if msg_type == "send.message":
            try:
                saved_msg = await self.chat_instance.astore_message(sender_pk=self.user.pk, content=text_data_json["message"])
                serializer = MessageSerializer(saved_msg)
                msg_json = await sync_to_async(lambda: serializer.data)()
                msg_json["type"] = "send.message" 
                await self.channel_layer.group_send(self.room_group_name, msg_json)
            except ValueError as e:
                await self.send(json.dumps({"error": str(e)}))
        
        elif msg_type == "edit.message":
            mpk = text_data_json["message_pk"]
            spk = self.user.pk
            try:
                m = await Message.objects.select_related("sender").aget(pk=mpk)  # TODO remove unused fields
            except Message.DoesNotExist:
                await self.send(json.dumps({"error": "No such message"}))
                return
            if m.sender.pk != spk:
                await self.send(json.dumps({"error": "Forbidden"}))
                return
            serializer = MessageSerializer(instance=m, data={"content": text_data_json["new_content"]}, partial=True)
            if serializer.is_valid():
                await sync_to_async(serializer.save)()
                await self.channel_layer.group_send(self.room_group_name, text_data_json)
            else:
                await self.send(json.dumps({"error": serializer.errors}))
                return
            


        elif msg_type == "delete.message":
            mpk = text_data_json["message_pk"]
            spk = self.user.pk
            try:
                m = await Message.objects.select_related("sender").aget(pk=mpk)  # TODO remove unused fields
            except Message.DoesNotExist:
                await self.send(json.dumps({"error": "No such message"}))
                return
            if m.sender.pk != spk:
                await self.send(json.dumps({"error": "Forbidden"}))
                return
            await m.adelete()
            await self.channel_layer.group_send(self.room_group_name, text_data_json)


        elif msg_type == "get_history":
            chunk = text_data_json.get("chunk", 0)
            chunk_size = text_data_json.get("chunk_size", 10)
            data = await sync_to_async(self.chat_instance.get_history)(chunk=chunk, chunk_size=chunk_size)
            serializer = MessageSerializer(data, many=True)
            serialized = await sync_to_async(lambda: serializer.data)()
            
            await self.send(json.dumps({"history": serialized}))
        
        elif msg_type == "whoami":
            whs = WhoamiProfileSerializer(self.user)
            whsdata = await sync_to_async(lambda:whs.data)
            await self.send(json.dumps(whsdata))
        
        elif msg_type == "update.status":  # TODO tests
            m = await Message.objects.aget(pk=text_data_json["message_pk"])
            await m.aupdate_status(text_data_json["new_status"])
            await self.channel_layer.group_send(self.room_group_name, text_data_json)

    async def send_message(self, event): 
        await self.send(text_data=json.dumps(event)) 
    
    async def edit_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def delete_message(self,event):
        await self.send(text_data=json.dumps(event))

    async def update_status(self, event):
        await self.send(text_data=json.dumps(event))


class ChatListConsumer(AsyncWebsocketConsumer):

    async def _authorize(self):
        token = parse_qs(self.scope.get("query_string", b"")).get(b"authorization", b"")
        if token:
            token = str(token[0]).split(" ")[-1][:-1]  # because of format "Token #####"
            try:
                user = await User.objects.prefetch_related("auth_token").aget(auth_token__key=token)
                return user
            except User.DoesNotExist:
                return False
        else:
            return False

    async def connect(self): 
        user = await self._authorize()
        if not user:
            await self.close(code=4001, reason="Authorization error")
            return
        self.layer_name = "chat_list_updates_"+str(user.pk)
        await self.channel_layer.group_add(self.layer_name, self.channel_name)  
        await self.accept()
        chats = await sync_to_async(Chat.objects.filter)(Q(user1=user)|Q(user2=user))
        serializer = ChatSerializer(chats, many=True)     
        data = await sync_to_async(lambda: serializer.data)()
        for i, j in zip(data, chats): 
            i["unread"] = await sync_to_async(j.get_unread)(user)
        await self.send(text_data=json.dumps(data))
    
    async def receive(self, text_data): 
        return await super().receive(text_data)
    
    async def disconnect(self, code):
         await self.channel_layer.group_discard(
            self.layer_name,
            self.channel_name
        )
    
    async def chat_list_activity(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat_list_update",
            "event_details": event
        }))