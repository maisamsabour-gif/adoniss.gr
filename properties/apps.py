from django.apps import AppConfig


class PropertiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'properties'
    verbose_name = 'Properties'

    def ready(self):
        import properties.checks  # noqa: F401
