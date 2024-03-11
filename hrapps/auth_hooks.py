from django.utils.translation import gettext_lazy as _

from allianceauth import hooks
from allianceauth.menu.hooks import MenuItemHook
from allianceauth.services.hooks import UrlHook

from . import urls
from .models import Application


class ApplicationsMenu(MenuItemHook):
    def __init__(self):
        MenuItemHook.__init__(
            self,
            _('Applications2'),
            'fa-regular fa-file',
            'hrapps:index',
            navactive=['hrapps:'])

    def render(self, request):
        if request.user.has_perm("hrapps.create_new_application"):
            app_count = Application.objects.pending_requests_count_for_user(request.user)
            self.count = app_count if app_count and app_count > 0 else None
            return MenuItemHook.render(self, request)
        return ""


@hooks.register('menu_item_hook')
def register_menu():
    return ApplicationsMenu()


class ApplicationsUrls(UrlHook):
    def __init__(self):
        UrlHook.__init__(self, urls, 'hrapps', r'^hrapps/')


@hooks.register('url_hook')
def register_url():
    return ApplicationsUrls()
