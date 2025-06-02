from django.test import TestCase, Client
from channels.testing import HttpCommunicator, WebsocketCommunicator
from .consumers import ChatConsumer
from channels.routing import URLRouter
from .routing import websocket_urlpatterns
from cauth.models import User
from .models import Chat, Message
from rest_framework.authtoken.models import Token
from asgiref.sync import sync_to_async

class ChatTestCase(TestCase):
    def setUp(self):
        u1 = User.objects.create(username="u1")
        self.token = f"Token {Token.objects.get(user=u1).key}"
        u2 = User.objects.create(username="u2")
        self.token2 = f"Token {Token.objects.get(user=u2).key}"
        self.chat = Chat.objects.create(user1=u1, user2=u2, chat_key="1")
        u33 = User.objects.create(username="u33")
        self.token3 = f"Token {Token.objects.get(user=u33).key}"
    
    async def get_users(self):
        return await User.objects.aget(username="u1"), await User.objects.aget(username="u2")

    def get_communicator(self, path):
        return WebsocketCommunicator(URLRouter(websocket_urlpatterns), path)

    async def test_chat(self):
        u1 = (await self.get_users())[0]
        u3 = await User.objects.acreate(username="u3")
        communicator = self.get_communicator(f"ws/chat/1/?authorization={self.token}")
        communicator2 = self.get_communicator(f"ws/chat/1/?authorization={self.token2}")
        communicator3 = self.get_communicator(f"ws/chat/1/?authorization={self.token3}")
        connected = (await communicator.connect())
        connected2 = (await communicator2.connect())
        connected3 = (await communicator3.connect())
        self.assertEqual(connected[0], True)
        self.assertEqual(connected2[0], True)
        self.assertEqual(connected3[0], False)  # testing connection reject for user, who has not been added to chat
        self.assertEqual(connected3[1], 4001)

        await communicator.send_json_to({"type": "send.message", "message": "qwee"})
        res = await communicator.receive_json_from()
        self.assertEqual(res["content"], "qwee")  # testing same output for sender
        res2 = await communicator2.receive_json_from()
        self.assertEqual(res2["content"], "qwee")  # testing output for channel listener
        await communicator.send_json_to({"type": "get_history"})
        res = await communicator.receive_json_from()
        self.assertEqual(res["history"][0]["content"], "qwee")  # testing history from ws

        m = await Message.objects.aget(content="qwee")
        await communicator.send_json_to({"type": "edit.message", "message_pk": m.pk, "new_content": "qqqqqwwwwww"})
        res = await communicator.receive_json_from()
        await communicator2.receive_json_from()
        self.assertEqual(res["new_content"], "qqqqqwwwwww")  # test edition     
        await communicator2.send_json_to({"type": "edit.message", "message_pk": m.pk, "new_content": "qqqqqwwwwww"})
        res = await communicator2.receive_json_from()
        self.assertEqual(res["error"], "Forbidden")  # testing edition by non-owner
        with self.assertRaises(Message.DoesNotExist):
            m = await Message.objects.aget(content="qwee")
        
        m = await Message.objects.aget(content="qqqqqwwwwww")
        await communicator2.send_json_to({"type": "delete.message", "message_pk": m.pk})
        res = await communicator2.receive_json_from()
        self.assertEqual(res["error"], "Forbidden")  # testing deletion by non-owner
        await communicator.send_json_to({"type": "delete.message", "message_pk": m.pk})
        res = await communicator.receive_json_from()
        self.assertEqual(res["message_pk"], 1)
        await communicator.send_json_to({"type": "delete.message", "message_pk": m.pk})
        res = await communicator.receive_json_from()
        self.assertEqual(res["error"], "No such message")  # testing deletion of not-existing message
        with self.assertRaises(Message.DoesNotExist):
            m = await Message.objects.aget(content="qqqqqwwwwww")


    async def test_chats_list(self):
        u1, u2 = await self.get_users()
        communicator = self.get_communicator(f"ws/chats/list/?authorization={self.token}")
        communicator2 = self.get_communicator(f"ws/chats/list/?authorization={self.token2}")
        connected = await communicator.connect()
        connected2 = await communicator2.connect()
        self.assertEqual(connected[0], True)
        self.assertEqual(connected2[0], True)
        res = await communicator.receive_json_from()
        res2 = await communicator2.receive_json_from()

        self.assertEqual(len(res), 1)
        self.assertEqual(res, res2)
        ch = await Chat.objects.acreate(user1=u1, user2=u2, chat_key="2")
        res = await communicator.receive_json_from()
        res2 = await communicator2.receive_json_from()
        self.assertEqual(res["event_details"]["chat_data"]["chat_key"], "2")
        self.assertEqual(res, res2)
        await ch.adelete()
        res = await communicator.receive_json_from()

    async def test_last_message_update(self):
        u1, u2 = await self.get_users()
        communicator = self.get_communicator(f"ws/chats/list/?authorization={self.token}")
        communicator2 = self.get_communicator(f"ws/chats/list/?authorization={self.token2}")
        connected = await communicator.connect()
        connected2 = await communicator2.connect()
        self.assertEqual(connected[0], True)
        self.assertEqual(connected2[0], True)
        await communicator.receive_json_from()
        await communicator2.receive_json_from()
        await self.chat.astore_message(sender_pk=u1.pk, content="messageee")
        res = await communicator.receive_json_from()
        res2 = await communicator2.receive_json_from()
        self.assertEqual(res, res2)
        self.assertEqual(res["event_details"]["event"], "last_update")


class RESTChatsTestCase(TestCase):
    def setUp(self):
        self.u1 = User.objects.create(username="u1")
        self.token1 = f"Token {Token.objects.get(user=self.u1).key}"
        self.u2 = User.objects.create(username="u2")
        self.token2 = f"Token {Token.objects.get(user=self.u2).key}"
        Chat.objects.create(user1=self.u1, user2=self.u2, chat_key="1")
        Chat.objects.create(user1=self.u1, user2=self.u2, chat_key="2")
        Chat.objects.create(user1=self.u1, user2=self.u2, chat_key="3")
        self.cloent = Client()
