import django
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from fluent_pages import appsettings
from parler.admin import TranslatableAdmin
from parler.models import TranslationDoesNotExist
from parler.utils import is_multilingual_project
from polymorphic_tree.admin import PolymorphicMPTTParentModelAdmin, NodeTypeChoiceForm
from fluent_pages.models import UrlNode
from fluent_utils.dry.admin import MultiSiteAdminMixin


class PageTypeChoiceForm(NodeTypeChoiceForm):
    type_label = _("Page type")


try:
    from django.contrib.admin import SimpleListFilter
except ImportError:
    extra_list_filters = ()
else:
    # Django 1.4:
    class PageTypeListFilter(SimpleListFilter):
        parameter_name = 'ct_id'
        title = _('page type')

        def lookups(self, request, model_admin):
            return model_admin.get_child_type_choices()

        def queryset(self, request, queryset):
            if self.value():
                queryset = queryset.filter(polymorphic_ctype_id=self.value())
            return queryset

    extra_list_filters = (PageTypeListFilter,)


class UrlNodeParentAdmin(MultiSiteAdminMixin, TranslatableAdmin, PolymorphicMPTTParentModelAdmin):
    """
    The internal machinery
    The admin screen for the ``UrlNode`` objects.
    """
    filter_site = appsettings.FLUENT_PAGES_FILTER_SITE_ID
    base_model = UrlNode
    add_type_form = PageTypeChoiceForm

    # Config list page:
    if is_multilingual_project():
        list_display = ('title', 'language_column', 'status_column', 'modification_date', 'actions_column')
    else:
        list_display = ('title', 'status_column', 'modification_date', 'actions_column')
    list_filter = ('status',) + extra_list_filters
    search_fields = ('translations__slug', 'translations__title')
    actions = ['make_published']

    class Media:
        css = {
            'screen': ('fluent_pages/admin/pagetree.css',)
        }

    # ---- Polymorphic tree overrides ----

    def get_child_models(self):
        """
        Provide the available models of the page type registration system to *django-polymorphic-tree*.
        """
        from fluent_pages.extensions import page_type_pool
        child_models = []

        for plugin in page_type_pool.get_plugins():
            child_models.append((plugin.model, plugin.model_admin))
        return child_models

    def get_child_type_choices(self, request=None, action=None):
        """
        Return a list of polymorphic types which can be added.
        """
        # The arguments are made optional, to support both django-polymorphic 0.5 and 0.6
        from fluent_pages.extensions import page_type_pool

        priorities = {}
        choices = []
        for plugin in page_type_pool.get_plugins():
            ct = ContentType.objects.get_for_model(plugin.model)
            choices.append((ct.id, plugin.verbose_name))
            priorities[ct.id] = plugin.sort_priority

        choices.sort(key=lambda choice: (priorities[choice[0]], choice[1]))
        return choices

    # Provide some migration assistance for the users of the 0.8.1 alpha release:
    def get_child_model_classes(self):
        raise DeprecationWarning("Please upgrade django-polymorphic-tree to 0.8.2 to use this version of django-fluent-pages.")

    # ---- parler overrides ----

    def delete_translation(self, request, object_id, language_code):
        # Since we use django-polymorphic, the django-parler view should also be redirected to the child admin.
        # This also enables FluentContentsPageAdmin.get_translation_objects() to be called.
        real_admin = self._get_real_admin(object_id)
        return real_admin.delete_translation(request, object_id, language_code)

    # ---- List code ----

    # NOTE: the regular results table is replaced client-side with a jqTree list.
    # When making changes to the list, test both the JavaScript and non-JavaScript variant.
    # The jqTree variant still uses the server-side rendering for the colums.

    if django.VERSION >= (1, 9):
        STATUS_ICONS = (
            (UrlNode.PUBLISHED, 'admin/img/icon-yes.svg'),
            (UrlNode.DRAFT,     'admin/img/icon-unknown.svg'),
        )
    else:
        STATUS_ICONS = (
            (UrlNode.PUBLISHED, 'admin/img/icon-yes.gif'),
            (UrlNode.DRAFT,     'admin/img/icon-unknown.gif'),
        )

    def status_column(self, urlnode):
        status = urlnode.status
        title = [rec[1] for rec in UrlNode.STATUSES if rec[0] == status].pop()
        icon  = [rec[1] for rec in self.STATUS_ICONS if rec[0] == status].pop()
        return u'<img src="{static_url}{icon}" alt="{title}" title="{title}" />'.format(
            static_url=settings.STATIC_URL, icon=icon, title=title
        )

    status_column.allow_tags = True
    status_column.short_description = _('Status')

    def can_preview_object(self, urlnode):
        """ Override whether the node can be previewed. """
        if not hasattr(urlnode, 'get_absolute_url') or not urlnode.is_published:
            return False

        try:
            # Must have a translation in the currently active admin language.
            urlnode._cached_url
        except TranslationDoesNotExist:
            return False
        else:
            return True

    def get_language_short_title(self, language_code):
        """
        Turn the language code to uppercase.
        """
        return language_code.upper()

    def get_search_results(self, request, queryset, search_term):
        # HACK: make sure MPTT doesn't cause errors when finding sub-level results.
        # The list code should be fixed instead, but that is much harder.
        if search_term:
            queryset = queryset.filter(level=0)
        return super(UrlNodeParentAdmin, self).get_search_results(request, queryset, search_term)

    # ---- Bulk actions ----

    def make_published(self, request, queryset):
        rows_updated = queryset.update(status=UrlNode.PUBLISHED)

        if rows_updated == 1:
            message = "1 page was marked as published."
        else:
            message = "{0} pages were marked as published.".format(rows_updated)
        self.message_user(request, message)

    make_published.short_description = _("Mark selected objects as published")
