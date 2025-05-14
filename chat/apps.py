from django.apps import AppConfig

class ChatAppConfig(AppConfig):
    name = 'chat'

    def ready(self):
        import chat.signals
