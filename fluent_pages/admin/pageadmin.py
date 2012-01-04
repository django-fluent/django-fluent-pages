from django.conf.urls.defaults import patterns
from django.utils.translation import ugettext_lazy as _
from fluent_contents.admin.placeholdereditor import PlaceholderEditorAdminMixin
from fluent_contents.analyzer import get_template_placeholder_data
from fluent_pages.admin.urlnodeadmin import UrlNodeAdmin
from fluent_pages.forms.widgets import LayoutSelector
from fluent_pages.models.db import CmsLayout, Page
from fluent_pages.utils.ajax import JsonResponse


class PageAdmin(PlaceholderEditorAdminMixin, UrlNodeAdmin):
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'status', 'layout',),
        }),
        (_('SEO settings'), {
            'fields': ('keywords', 'description'),
            'classes': ('collapse',),
        }),
        UrlNodeAdmin.fieldsets[1],
        UrlNodeAdmin.fieldsets[2],
    )

    change_form_template = ["admin/fluent_pages/page/page_editor.html",
                            "admin/fluent_pages/page.html",
                            ]

    class Media:
        js = ('fluent_pages/fluent_layouts.js',)


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
                return CmsLayout.objects.all()[0].get_template()
            except IndexError:
                return None
        else:
            # Change page, honor template of object.
            return page.layout.get_template()


    # ---- Extra Ajax views ----


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'layout':
            kwargs['widget'] = LayoutSelector
        return super(PageAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


    def get_urls(self):
        """
        Introduce more urls
        """
        urls = super(PageAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^get_layout/(?P<id>\d+)/$', self.admin_site.admin_view(self.get_layout_view))
        )
        return my_urls + urls


    def get_layout_view(self, request, id):
        """
        Return the metadata about a layout
        """
        try:
            layout = CmsLayout.objects.get(pk=id)
        except CmsLayout.DoesNotExist:
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
