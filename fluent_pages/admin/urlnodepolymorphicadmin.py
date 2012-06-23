import django
from django.conf import settings
from django.conf.urls.defaults import url
from django.db import router
from django.db.models import signals
from django.http import HttpResponseNotFound, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from fluent_pages.utils.polymorphicadmin import PolymorphicBaseModelAdmin, PolymorphicModelChoiceAdminForm
from fluent_pages.models import UrlNode
from mptt.admin import MPTTModelAdmin

class PageTypeChoiceAdminForm(PolymorphicModelChoiceAdminForm):
    def __init__(self, *args, **kwargs):
        super(PageTypeChoiceAdminForm, self).__init__(*args, **kwargs)
        self.fields['ct_id'].label = _("Page type")


def _get_polymorphic_type_choices():
    from fluent_pages.extensions import page_type_pool

    priorities = {}
    choices = []
    for plugin in page_type_pool.get_plugins():
        ct = ContentType.objects.get_for_model(plugin.model)
        choices.append((ct.id, plugin.verbose_name))
        priorities[ct.id] = plugin.sort_priority

    choices.sort(key=lambda choice: (priorities[choice[0]], choice[1]))
    return choices


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
            return _get_polymorphic_type_choices()

        def queryset(self, request, queryset):
            if self.value():
                queryset = queryset.filter(polymorphic_ctype_id=self.value())
            return queryset

    extra_list_filters = (PageTypeListFilter,)


class UrlNodePolymorphicAdmin(PolymorphicBaseModelAdmin, MPTTModelAdmin):
    """
    The main entry to the admin interface of django-fluent-pages.
    """
    base_model = UrlNode
    add_type_form = PageTypeChoiceAdminForm

    # Config list page:
    list_display = ('title', 'status_column', 'modification_date', 'actions_column')
    list_filter = ('status',) + extra_list_filters
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
        return _get_polymorphic_type_choices()


    # ---- List code ----

    # NOTE: the regular results table is replaced client-side with a jqTree list.
    # When making changes to the list, test both the JavaScript and non-JavaScript variant.
    # The jqTree variant still uses the server-side rendering for the colums.

    STATUS_ICONS = (
        (UrlNode.PUBLISHED, 'icon-yes.gif'),
        (UrlNode.DRAFT,     'icon-unknown.gif'),
    )


    def status_column(self, urlnode):
        status = urlnode.status
        title = [rec[1] for rec in UrlNode.STATUSES if rec[0] == status].pop()
        icon  = [rec[1] for rec in self.STATUS_ICONS if rec[0] == status].pop()
        if django.VERSION >= (1, 4):
            admin = settings.STATIC_URL + 'admin/img/'
        else:
            admin = settings.ADMIN_MEDIA_PREFIX + 'img/admin/'
        return u'<img src="{admin}{icon}" width="10" height="10" alt="{title}" title="{title}" />'.format(admin=admin, icon=icon, title=title)

    status_column.allow_tags = True
    status_column.short_description = _('Status')


    def actions_column(self, urlnode):
        return u' '.join(self._actions_column_icons(urlnode))

    actions_column.allow_tags = True
    actions_column.short_description = _('Actions')


    def _actions_column_icons(self, urlnode):
        empty_img = u'<span><img src="{static}fluent_pages/img/admin/blank.gif" width="16" height="16" alt=""/></span>'.format(static=settings.STATIC_URL)

        actions = []
        if urlnode.can_have_children:
            actions.append(
                u'<a href="add/?{parentattr}={id}" title="{title}"><img src="{static}fluent_pages/img/admin/page_new.gif" width="16" height="16" alt="{title}" /></a>'.format(
                    parentattr=self.model._mptt_meta.parent_attr, id=urlnode.pk, title=_('Add sub page'), static=settings.STATIC_URL)
                )
        else:
            actions.append(empty_img)

        if hasattr(urlnode, 'get_absolute_url') and urlnode.is_published:
            actions.append(
                u'<a href="{url}" title="{title}" target="_blank"><img src="{static}fluent_pages/img/admin/world.gif" width="16" height="16" alt="{title}" /></a>'.format(
                    url=urlnode.get_absolute_url(), title=_('View on site'), static=settings.STATIC_URL)
                )

        # The is_first_sibling and is_last_sibling is quite heavy. Instead rely on CSS to hide the arrows.
        move_up = u'<a href="{0}/move_up/" class="move-up">\u2191</a>'.format(urlnode.pk)
        move_down = u'<a href="{0}/move_down/" class="move-down">\u2193</a>'.format(urlnode.pk)
        actions.append(u'<span class="no-js">{0}{1}</span>'.format(move_up, move_down))

        return actions


    # ---- Bulk actions ----

    def make_published(self, request, queryset):
        rows_updated = queryset.update(status=UrlNode.PUBLISHED)

        if rows_updated == 1:
            message = "1 page was marked as published."
        else:
            message = "{0} pages were marked as published.".format(rows_updated)
        self.message_user(request, message)


    make_published.short_description = _("Mark selected objects as published")


    # ---- Custom views ----

    def get_urls(self):
        base_urls = super(UrlNodePolymorphicAdmin, self).get_urls()
        info = self.model._meta.app_label, self.model._meta.module_name
        extra_urls = [
            url(r'^api/page-moved/$', self.admin_site.admin_view(self.api_page_moved_view), name='{0}_{1}_moved'.format(*info)),
            url(r'^(\d+)/move_up/$', self.admin_site.admin_view(self.move_up_view)),
            url(r'^(\d+)/move_down/$', self.admin_site.admin_view(self.move_down_view)),
        ]
        return extra_urls + base_urls


    def api_page_moved_view(self, request):
        """
        Update the position of a node, from a API request.
        """
        try:
            # Not using .non_polymorphic() so all models are upcasted to the derived model.
            # This causes the signal below to be emitted from the proper class as well.
            moved = self.model.objects.get(pk=request.POST['moved_id'])
            target = self.model.objects.get(pk=request.POST['target_id'])
            previous_parent_id = int(request.POST['previous_parent_id']) or None
            position = request.POST['position']
        except KeyError as e:
            return HttpResponseBadRequest(simplejson.dumps({'action': 'foundbug', 'error': str(e[0])}), content_type='application/json')
        except self.model.DoesNotExist as e:
            return HttpResponseNotFound(simplejson.dumps({'action': 'reload', 'error': str(e[0])}), content_type='application/json')

        if not target.can_have_children and position == 'inside':
            return HttpResponse(simplejson.dumps({'action': 'reject', 'error': 'Cannot move inside target, does not allow children!'}), content_type='application/json', status=409)  # Conflict
        if moved.parent_id != previous_parent_id:
            return HttpResponse(simplejson.dumps({'action': 'reload', 'error': 'Client seems to be out-of-sync, please reload!'}), content_type='application/json', status=409)

        # TODO: with granular user permissions, check if user is allowed to edit both pages.

        mptt_position = {
            'inside': 'first-child',
            'before': 'left',
            'after': 'right',
        }[position]
        moved.move_to(target, mptt_position)

        # Fire post_save signal manually, because django-mptt doesn't do that.
        # Allow models to be notified about a move, so django-fluent-contents can update caches.
        using = router.db_for_write(moved.__class__, instance=moved)
        signals.post_save.send(sender=moved.__class__, instance=moved, created=False, raw=False, using=using)

        # Report back to client.
        return HttpResponse(simplejson.dumps({'action': 'success', 'error': ''}), content_type='application/json')


    def move_up_view(self, request, object_id):
        page = self.model.objects.get(pk=object_id)

        if page is not None:
            previous_sibling_category = page.get_previous_sibling()
            if previous_sibling_category is not None:
                page.move_to(previous_sibling_category, position='left')

        return HttpResponseRedirect('../../')


    def move_down_view(self, request, object_id):
        page = self.model.objects.get(pk=object_id)

        if page is not None:
            next_sibling_category = page.get_next_sibling()
            if next_sibling_category is not None:
                page.move_to(next_sibling_category, position='right')

        return HttpResponseRedirect('../../')
