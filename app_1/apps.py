from django.apps import AppConfig


class App1Config(AppConfig):
    name = 'app_1'
    def ready(self):
        # Import signal handlers to ensure they're registered
        try:
            import app_1.signals  # noqa: F401
        except Exception:
            pass

