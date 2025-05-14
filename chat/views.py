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

    def get(self, request):
        chats = Chat.objects.filter(Q(user1=request.user)|Q(user2=request.user))
        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data)
