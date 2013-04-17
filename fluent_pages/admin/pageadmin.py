import copy
from django.contrib.admin.widgets import ForeignKeyRawIdWidget, AdminTextareaWidget, AdminTextInputWidget
from django.utils.translation import ugettext_lazy as _
from fluent_pages.admin.urlnodeadmin import UrlNodeAdmin, UrlNodeAdminForm
from fluent_pages.models import Page, HtmlPage


class PageAdminForm(UrlNodeAdminForm):
    """
    The base class for all admin forms.

    This form validates the "Slug" and "Override URL" fields.
    """
    pass


class PageAdmin(UrlNodeAdmin):
    """
    The base class for administrating pages.
    When a custom page type implements a custom admin, use this class as its base.
    See the code in ``fluent_pages/pagetypes/*/admin.py`` for examples.
    To deal with model inheritence, define the fieldsets using the :attr:`base_fieldsets` option.
    For example:

    .. code-block:: python

        base_fieldsets = (
            PageAdmin.FIELDSET_GENERAL,
            PageAdmin.FIELDSET_MENU,
            PageAdmin.FIELDSET_PUBLICATION,
        )

    By using :attr:`base_fieldsets` instead of the :attr:`ModelAdmin.fieldsets <django.contrib.admin.ModelAdmin.fieldsets>` attribute,
    any additional fields from a derived model will be displayed in a separate fieldset automatically.
    The title of the fieldset is configurable with the :attr:`extra_fieldset_title` attribute.
    It's "Contents" by default.
    """
    base_model = Page
    base_form = PageAdminForm

    #: The default template name, which is available in the template context.
    #: Use ``{% extend base_change_form_template %}`` in templates to inherit from it.
    base_change_form_template = "admin/fluent_pages/page/change_form.html"


    class Media:
        js = ('fluent_pages/admin/django13_fk_raw_id_fix.js',)


    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(PageAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if field is None:
            return None

        # Hack the ForeignKeyRawIdWidget in Django 1.4 to display a selector for the base model too.
        # It correctly detects that the parent field actually points to an UrlNode, instead of Page.
        # Since UrlNode is not registered in the admin, it won't display the selector. Overriding that here.
        # It also partially fixes Django 1.3, which would wrongly point the url to ../../../fluent_pages/urlnode/ otherwise.
        if db_field.name == 'parent' and isinstance(field.widget, ForeignKeyRawIdWidget):
            field.widget.rel = copy.copy(field.widget.rel)
            field.widget.rel.to = Page

        return field


    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        # Include a 'base_change_form_template' in the context, make it easier to extend
        context.update({
            'base_change_form_template': self.base_change_form_template,
        })
        return super(PageAdmin, self).render_change_form(request, context, add=add, change=change, form_url=form_url, obj=obj)



class HtmlPageAdmin(PageAdmin):
    """
    The modeladmin configured to display :class:`~fluent_pages.models.HtmlPage` models.
    The :class:`~fluent_pages.models.HtmlPage` also displays a ``keywords`` and ``description`` field.

    This admin class defines another fieldset: :attr:`FIELDSET_SEO`.
    The default fieldset layout is:

    .. code-block:: python

        base_fieldsets = (
            HtmlPageAdmin.FIELDSET_GENERAL,
            HtmlPageAdmin.FIELDSET_SEO,
            HtmlPageAdmin.FIELDSET_MENU,
            HtmlPageAdmin.FIELDSET_PUBLICATION,
        )
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

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'keywords':
            kwargs.setdefault('widget', AdminTextInputWidget(attrs={'class': 'vLargeTextField'}))
        if db_field.name == 'description':
            kwargs.setdefault('widget', AdminTextareaWidget(attrs={'rows': 3}))

        return super(HtmlPageAdmin, self).formfield_for_dbfield(db_field, **kwargs)
