from django.utils.translation import ugettext_lazy as _
from fluent_pages.admin.urlnodeadmin import UrlNodeAdmin, UrlNodeAdminForm
from fluent_pages.models import Page, HtmlPage


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


class HtmlPageAdmin(PageAdmin):
    """
    The modeladmin configured to display :class:`~fluent_pages.models.HtmlPage` objects.
    """
    FIELDSET_SEO = (_('SEO settings'), {
        'fields': ('keywords', 'description'),
        'classes': ('collapse',),
    })

    base_fieldsets = (
        PageAdmin.FIELDSET_GENERAL,
        FIELDSET_SEO,
        PageAdmin.FIELDSET_MENU,
        PageAdmin.FIELDSET_PUBLICATION,
    )
