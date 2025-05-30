from django.urls import path
from .views import ChatsAPIView

urlpatterns = [
    path("<str:key>", ChatsAPIView.as_view()),
]