from django.apps import AppConfig


class TestBasicsDefaultsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'test_basics_defaults'
