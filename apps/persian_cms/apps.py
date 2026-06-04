from django.apps import AppConfig


class PersianCmsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.persian_cms"
    label = "persian_cms"
    verbose_name = "ADONIS Persian CMS"
    
    def ready(self):
        # Import signals to register them
        from . import signals  # noqa: F401
