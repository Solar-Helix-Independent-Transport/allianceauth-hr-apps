# from typing import override
from django.apps import AppConfig


class HRAppsConfig(AppConfig):
    name = 'hrapps'
    label = 'hrapps'

    # @override
    def ready(self):
        import hrapps.signals
