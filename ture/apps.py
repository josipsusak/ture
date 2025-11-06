from django.apps import AppConfig

class TureConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ture'
    def ready(self):
        import ture.signals  # registriramo signal
