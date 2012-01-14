from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from fluent_pages.utils.polymorphicadmin import PolymorphicBaseModelAdmin, PolymorphicModelChoiceAdminForm
from fluent_pages.models import UrlNode
from mptt.admin import MPTTModelAdmin


class PageTypeChoiceAdminForm(PolymorphicModelChoiceAdminForm):
    def __init__(self, *args, **kwargs):
        super(PageTypeChoiceAdminForm, self).__init__(*args, **kwargs)
        self.fields['ct_id'].label = _("Page type")


class UrlNodePolymorphicAdmin(PolymorphicBaseModelAdmin, MPTTModelAdmin):
    """
    The main entry to the admin interface of django-fluent-pages.
    """
    base_model = UrlNode
    add_type_form = PageTypeChoiceAdminForm

    # Config list page:
    list_display = ('title', 'status_column', 'modification_date', 'actions_column')
    #list_filter = ('status', 'parent')
    search_fields = ('slug', 'title')
    actions = ['make_published']
    change_list_template = None  # Restore Django's default search behavior, no admin/mptt_change_list.html


    # ---- Polymorphic code ----

    def get_admin_for_model(self, model):
        from fluent_pages.extensions import page_type_pool
        return page_type_pool.get_model_admin(model)


    def get_polymorphic_model_classes(self):
        from fluent_pages.extensions import page_type_pool
        return page_type_pool.get_model_classes()


    def get_polymorphic_type_choices(self):
        """
        Return a list of polymorphic types which can be added.
        """
        from fluent_pages.extensions import page_type_pool

        choices = []
        for plugin in page_type_pool.get_plugins():
            ct = ContentType.objects.get_for_model(plugin.model)
            choices.append((ct.id, plugin.verbose_name))
        return choices


    # ---- List code ----

    STATUS_ICONS = (
        (UrlNode.PUBLISHED, 'img/admin/icon-yes.gif'),
        (UrlNode.DRAFT,     'img/admin/icon-unknown.gif'),
    )


    def status_column(self, urlnode):
        status = urlnode.status
        title = [rec[1] for rec in UrlNode.STATUSES if rec[0] == status].pop()
        icon  = [rec[1] for rec in self.STATUS_ICONS  if rec[0] == status].pop()
        return u'<img src="{admin}{icon}" width="10" height="10" alt="{title}" title="{title}" />'.format(
            admin=settings.ADMIN_MEDIA_PREFIX, icon=icon, title=title)

    status_column.allow_tags = True
    status_column.short_description = _('Status')


    def actions_column(self, urlnode):
        return u' '.join(self._actions_column_icons(urlnode))

    actions_column.allow_tags = True
    actions_column.short_description = _('actions')


    def _actions_column_icons(self, urlnode):
        actions = [
            u'<a href="add/?{parentattr}={id}" title="{title}"><img src="{static}fluent_pages/img/admin/page_new.gif" width="16" height="16" alt="{title}" /></a>'.format(
                parentattr=self.model._mptt_meta.parent_attr, id=urlnode.pk, title=_('Add child'), static=settings.STATIC_URL)
        ]

        if hasattr(urlnode, 'get_absolute_url') and urlnode.is_published:
            actions.append(
                u'<a href="{url}" title="{title}" target="_blank"><img src="{static}fluent_pages/img/admin/world.gif" width="16" height="16" alt="{title}" /></a>'.format(
                    url=urlnode.get_absolute_url(), title=_('View on site'), static=settings.STATIC_URL)
                )
        return actions


    def make_published(self, request, queryset):
        rows_updated = queryset.update(status=UrlNode.PUBLISHED)

        if rows_updated == 1:
            message = "1 page was marked as published."
        else:
            message = "{0} pages were marked as published.".format(rows_updated)
        self.message_user(request, message)


    make_published.short_description = _("Mark selected objects as published")
