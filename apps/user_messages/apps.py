from django.apps import AppConfig


class UserMessagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.user_messages'
    
    def ready(self):
        import apps.user_messages.signals
