from django.conf.urls.defaults import patterns
from django.utils.translation import ugettext_lazy as _
from fluent_contents.admin.placeholdereditor import PlaceholderEditorAdminMixin
from fluent_contents.analyzer import get_template_placeholder_data
from fluent_pages.admin.urlnodeadmin import UrlNodeAdmin
from fluent_pages.models.db import CmsLayout
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
            return JsonResponse(None)

        json = {
            'id': layout.id,
            'key': layout.key,
            'title': layout.title,
            'regions': [{ 'key': r.key, 'title': r.title, 'role': r.role} for r in layout.regions.only('key', 'title', 'role')]
        }

        return JsonResponse(json)
