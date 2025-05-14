from django.urls import path
from .views import ChatsAPIView

urlpatterns = [
    path("list", ChatsAPIView.as_view()),
]