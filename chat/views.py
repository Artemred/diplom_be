from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ChatSerializer
from .models import Chat
from django.db.models import Q
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class ChatsAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, key):
        chat = Chat.objects.get(chat_key=key)
        serializer = ChatSerializer(chat)
        return Response(serializer.data)
        