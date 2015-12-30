from django.conf.urls import url, patterns
from fluent_pages.admin import HtmlPageAdmin, PageAdminForm
from fluent_pages.integration.fluent_contents.admin import FluentContentsPageAdmin
from fluent_pages.models import PageLayout
from fluent_contents.analyzer import get_template_placeholder_data
from fluent_utils.ajax import JsonResponse
from .widgets import LayoutSelector


class FluentPageAdminForm(PageAdminForm):
    """
    The form for the :class:`FluentPageAdmin` code.
    """

    def __init__(self, *args, **kwargs):
        super(FluentPageAdminForm, self).__init__(*args, **kwargs)
        if 'layout' in self.fields:
            self.fields['layout'].queryset = self.get_layout_queryset(self.fields['layout'].queryset)

    def get_layout_queryset(self, base_qs):
        """
        Allow to limit the layout choices
        """
        return base_qs


class FluentPageAdmin(FluentContentsPageAdmin):
    """
    This admin is a small binding between the pagetypes of *django-fluent-pages*
    and page contents of *django-fluent-contents*.

    .. note::

        To create custom page types that combine boths apps,
        consider using :class:`fluent_pages.integration.fluent_contents.admin.FluentContentsPageAdmin` instead.
        In fact, the code in this class concerns with the layout mechanism that is specific for this implementation.

    To build a variation of this page, see the API documentation
    of `Creating a CMS system <http://django-fluent-contents.readthedocs.org/en/latest/cms.html>`_
    in the *django-fluent-contents* documentation to implement the required API's.
    """
    base_form = FluentPageAdminForm
    readonly_shared_fields = HtmlPageAdmin.readonly_shared_fields + ('layout',)

    # By using base_fieldsets, the parent PageAdmin will
    # add an extra fieldset for all derived fields automatically.
    FIELDSET_GENERAL = (None, {
        'fields': HtmlPageAdmin.FIELDSET_GENERAL[1]['fields'][:-1] + ('layout',) + HtmlPageAdmin.FIELDSET_GENERAL[1]['fields'][-1:],
    })

    base_fieldsets = (
        FIELDSET_GENERAL,
        HtmlPageAdmin.FIELDSET_SEO,
        HtmlPageAdmin.FIELDSET_MENU,
        HtmlPageAdmin.FIELDSET_PUBLICATION,
    )

    #change_form_template = [
    #  "admin/fluentpage/change_form.html",
    #  FluentContentsPageAdmin.base_change_form_template
    # ]

    class Media:
        js = ('fluent_pages/fluentpage/fluent_layouts.js',)

    # ---- fluent-contents integration ----

    def get_placeholder_data(self, request, obj=None):
        """
        Provides a list of :class:`fluent_contents.models.PlaceholderData` classes,
        that describe the contents of the template.
        """
        template = self.get_page_template(obj)
        if not template:
            return []
        else:
            return get_template_placeholder_data(template)

    def get_page_template(self, page):
        """
        Return the template that is associated with the page.
        """
        if page is None:
            # Add page. start with default template.
            try:
                return PageLayout.objects.all()[0].get_template()
            except IndexError:
                return None
        else:
            # Change page, honor template of object.
            return page.layout.get_template()

    # ---- Layout selector code ----

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'layout':
            kwargs['widget'] = LayoutSelector
        return super(FluentPageAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_urls(self):
        """
        Introduce more urls
        """
        urls = super(FluentPageAdmin, self).get_urls()
        my_urls = [
            url(r'^get_layout/(?P<id>\d+)/$', self.admin_site.admin_view(self.get_layout_view))
        ]
        return my_urls + urls

    def get_layout_view(self, request, id):
        """
        Return the metadata about a layout
        """
        try:
            layout = PageLayout.objects.get(pk=id)
        except PageLayout.DoesNotExist:
            json = {'success': False, 'error': 'Layout not found'}
            status = 404
        else:
            template = layout.get_template()
            placeholders = get_template_placeholder_data(template)

            status = 200
            json = {
                'id': layout.id,
                'key': layout.key,
                'title': layout.title,
                'placeholders': [p.as_dict() for p in placeholders],
            }

        return JsonResponse(json, status=status)

    # ---- Layout permission hooks ----

    def get_readonly_fields(self, request, obj=None):
        fields = super(FluentPageAdmin, self).get_readonly_fields(request, obj)

        if obj is not None \
        and not 'layout' in fields \
        and not self.has_change_page_layout_permission(request, obj):
            # Disable on edit page only.
            # Add page is allowed, need to be able to choose initial layout
            fields = fields + ('layout',)
        return fields

    def has_change_page_layout_permission(self, request, obj=None):
        """
        Whether the user can change the page layout.
        """
        codename = '{0}.change_page_layout'.format(obj._meta.app_label)
        return request.user.has_perm(codename, obj=obj)
