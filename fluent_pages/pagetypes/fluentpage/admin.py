from django.conf.urls.defaults import patterns
from fluent_pages.admin import HtmlPageAdmin
from fluent_pages.forms.widgets import LayoutSelector
from fluent_pages.models import PageLayout
from fluent_pages.utils.ajax import JsonResponse
from fluent_contents.admin.placeholdereditor import PlaceholderEditorAdmin
from fluent_contents.analyzer import get_template_placeholder_data


class FluentPageAdminBase(PlaceholderEditorAdmin, HtmlPageAdmin):
    """
    The base admin that works with the :class:`~fluent_pages.pagetypes.fluentpage.models.FluentPageBase` model;
    it defines the connection to *django-fluent-pages*, but doesn't yet specify how the layout and templates
    are associated with the page. The :func:`get_placeholder_data` function still needs to be implemented.
    """
    pass


class FluentPageAdmin(FluentPageAdminBase):
    # By using base_fieldsets, the parent PageAdmin will
    # add an extra fieldset for all derived fields automatically.
    base_fieldsets = (
        (None, {
            'fields': HtmlPageAdmin.FIELDSET_GENERAL[1]['fields'][:-1] + ('layout',) + HtmlPageAdmin.FIELDSET_GENERAL[1]['fields'][-1:],
        }),
        HtmlPageAdmin.FIELDSET_SEO,
        HtmlPageAdmin.FIELDSET_MENU,
        HtmlPageAdmin.FIELDSET_PUBLICATION,
    )

    change_form_template = ["admin/fluent_pages/page/page_editor.html",
                            "admin/fluent_pages/page.html",
                            ]

    class Media:
        js = ('fluent_pages/fluentpage/fluent_layouts.js',)


    # ---- fluent-contents integration ----


    def get_placeholder_data(self, request, obj):
        template = self.get_page_template(obj)
        if not template:
            return []
        else:
            return get_template_placeholder_data(template)


    def get_page_template(self, page):
        if not page:
            # Add page. start with default template.
            try:
                return PageLayout.objects.all()[0].get_template()
            except IndexError:
                return None
        else:
            # Change page, honor template of object.
            return page.layout.get_template()


    # ---- Extra Ajax views ----


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'layout':
            kwargs['widget'] = LayoutSelector
        return super(FluentPageAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


    def get_urls(self):
        """
        Introduce more urls
        """
        urls = super(FluentPageAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^get_layout/(?P<id>\d+)/$', self.admin_site.admin_view(self.get_layout_view))
        )
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
