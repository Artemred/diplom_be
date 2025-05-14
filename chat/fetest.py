from .models import Chat
from cauth.models import User

def fill_users():
    User.objects.create(username="qqq")


def test_creation():
    u1  =User.objects.get(username="qq")
    u2  =User.objects.get(username="qqq")

    c = Chat.objects.create(user1=u1, user2=u2, chat_key="qwe")

def test_deletion():
    c = Chat.objects.get(chat_key="qwe")
    c.delete()   

def test_add_message(msg="msg"):
    c = Chat.objects.first()
    u = User.objects.get(username="qq") 
    c.store_message(sender_pk=u.pk, content=msg)