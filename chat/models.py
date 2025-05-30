from django.db import models
from cauth.models import User
from django.db.models import Q


class Chat(models.Model): 
    title = models.CharField(max_length=128, default="untitled")
    user1 = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="related_chats1", null=True, blank=True)
    user2 = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="related_chats2", null=True, blank=True)
    chat_key = models.CharField(max_length=128, unique=True)
    vacancy = models.ForeignKey(to="cauth.Vacancy", on_delete=models.CASCADE, related_name="related_chats", null=True, blank=True)

    def store_message(self, sender_pk: int, content:str):  # TODO sender not only pk
        sender = User.objects.get(pk=sender_pk)
        if (self.user1 != sender and self.user2 != sender):
            raise ValueError("User doesn't have access to this chat")
        return Message.objects.create(chat=self, sender=sender, content=content)
    
    async def astore_message(self, sender_pk: int, content:str, status="sent"):
        sender = await User.objects.aget(pk=sender_pk)
        if (self.user1 != sender and self.user2 != sender):
            raise ValueError("User doesn't have access to this chat")
        return await Message.objects.acreate(chat=self, sender=sender, content=content, status=status)
    
    def get_history(self, chunk:int = 0, chunk_size:int = 10):
        return Message.objects.filter(chat=self)[chunk*chunk_size:(chunk+1)*chunk_size]
    
    def last_message(self):
        return Message.objects.filter(chat=self).order_by("-sent_date").first()
    
    def get_unread(self, user):
        return Message.objects.filter(chat=self, status="sent").exclude(sender=user).count()


class Message(models.Model):
    chat = models.ForeignKey(to=Chat, on_delete=models.CASCADE, related_name="related_messages")
    sender = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="related_messages", null=True, blank=True)
    content = models.CharField(max_length=2048)
    sent_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(choices=[("created", "created"), ("sent", "sent"), ("read", "read")], max_length=16, default="created")

    async def aupdate_content(self, new_content:str):
        self.content = new_content
        await self.asave()

    async def aupdate_status(self, new_status:str):
        self.status = new_status
        await self.asave()

    class Meta:
        ordering=["-sent_date"]

