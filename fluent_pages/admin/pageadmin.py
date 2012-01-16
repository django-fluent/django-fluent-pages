from fluent_pages.admin.urlnodeadmin import UrlNodeAdmin, UrlNodeAdminForm
from fluent_pages.models import Page


class PageAdminForm(UrlNodeAdminForm):
    pass


class PageAdmin(UrlNodeAdmin):
    """
    The base class for pages
    """
    base_model = Page
    base_form = PageAdminForm

    class Media:
        js = ('fluent_pages/fk_raw_id_fix.js',)

    # This class may be extended in the future.
    # Currently it's a tagging placeholder
    # to have a clear Page <-> PageAdmin combo.
