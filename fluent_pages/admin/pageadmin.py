from fluent_pages.admin.urlnodeadmin import UrlNodeAdmin, UrlNodeAdminForm

class PageAdminForm(UrlNodeAdminForm):
    pass


class PageAdmin(UrlNodeAdmin):
    """
    The base class for pages
    """
    base_form = PageAdminForm

    # This class may be extended in the future.
    # Currently it's a tagging placeholder
    # to have a clear Page <-> PageAdmin combo.
