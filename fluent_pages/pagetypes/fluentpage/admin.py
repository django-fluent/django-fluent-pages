from fluent_pages.admin import HtmlPageAdmin
from fluent_pages.models import PageLayout
from fluent_pages.utils.ajax import JsonResponse
from fluent_pages.utils.compat import url, patterns
from fluent_contents.admin.placeholdereditor import PlaceholderEditorAdmin
from fluent_contents.analyzer import get_template_placeholder_data
from .widgets import LayoutSelector



class FluentPageAdmin(PlaceholderEditorAdmin, HtmlPageAdmin):
    """
    This admin is a small binding between the pagetypes of *django-fluent-pages*
    and page contents of *django-fluent-contents*. In fact, most code only concerns with the layout
    mechanism that is custom for each implementation. To build a variation of this page,
    see the API documentation of `Creating a CMS system <http://django-fluent-contents.readthedocs.org/en/latest/cms.html>`_
    in the *django-fluent-contents* documentation to implement the required API's.
    """

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

    change_form_template = ["admin/fluent_pages/page/page_editor.html",
                            "admin/fluent_pages/page.html",
                            ]

    class Media:
        js = ('fluent_pages/fluentpage/fluent_layouts.js',)


    # ---- fluent-contents integration ----


    def get_placeholder_data(self, request, obj):
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
        my_urls = patterns('',
            url(r'^get_layout/(?P<id>\d+)/$', self.admin_site.admin_view(self.get_layout_view))
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
