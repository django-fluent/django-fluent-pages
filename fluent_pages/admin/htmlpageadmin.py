from django.contrib.admin.widgets import AdminTextareaWidget, AdminTextInputWidget
from django.utils.translation import ugettext_lazy as _
from fluent_pages.admin.overrides import PageAdmin


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
