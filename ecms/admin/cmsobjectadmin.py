from django.contrib import admin
from django import forms
from django.conf import settings
from django.conf.urls.defaults import patterns

# Core objects
from django.contrib.admin.options import StackedInline

# Many small imports
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

# Other libs
from mptt.admin import MPTTModelAdmin   # mptt 0.4
from ecms.models import CmsObject, CmsLayout
from ecms import extensions
from ecms.admin.utils import get_pageitem_categories
from ecms.extensions  import PLUGIN_CATEGORIES
from ecms.utils.ajax import JsonResponse

csrf_protect_m = method_decorator(csrf_protect)


class CmsObjectAdminForm(forms.ModelForm):
    """
    The admin form for the main fields (the ``CmsObject`` object).
    """
    class Meta:
        model = CmsObject

    def clean(self):
        """
        Extend valiation of the form, checking whether the URL is unique.
        Returns all fields which are valid.
        """
        # As of Django 1.3, only valid fields are passed in cleaned_data.
        cleaned_data = super(CmsObjectAdminForm, self).clean()

        # See if the current
        other_objects = CmsObject.objects.all()

        if self.instance and self.instance.id:
            # Editing an existing page
            current_id = self.instance.id
            other_objects = other_objects.exclude(id=current_id)
            parent = CmsObject.objects.get(pk=current_id).parent
        else:
            # Creating new page!
            parent = cleaned_data['parent']

        # If fields are filled in, and still valid, check for unique URL.
        # Determine new URL (note: also done in CmsObject model..)
        if cleaned_data.get('override_url'):
            new_url = cleaned_data['override_url']

            if other_objects.filter(_cached_url=new_url).count():
                self._errors['override_url'] = self.error_class([_('This URL is already taken by an other page.')])
                del cleaned_data['override_url']

        elif cleaned_data.get('slug'):
            new_slug = cleaned_data['slug']
            if parent:
                new_url = '%s%s/' % (parent._cached_url, new_slug)
            else:
                new_url = '/%s/' % new_slug

            if other_objects.filter(_cached_url=new_url).count():
                self._errors['slug'] = self.error_class([_('This slug is already used by an other page at the same level.')])
                del cleaned_data['slug']

        return cleaned_data


def get_pageitem_inlines():
    """
    Dynamically generate genuine django inlines for registered content types.
    """
    inlines = []
    for PluginType in extensions.plugin_pool.get_plugin_classes():  # self.model._supported_...()
        plugin = PluginType()
        PageItemType = plugin.model

        # Create a new Type that inherits CmsPageItemInline
        # Read the static fields of the ItemType to override default appearance.
        # This code is based on FeinCMS, (c) Simon Meers, BSD licensed
        base = (CmsPageItemInline,)
        name = '%s_AutoInline' %  PageItemType.__name__
        attrs = {
            '__module__': PluginType.__module__,
            'model': PageItemType,
            'type_name': plugin.type_name,
            'form': PluginType.admin_form or extensions.CmsPageItemForm,
            'name': plugin.verbose_name,
            'plugin': plugin,
            'ecms_admin_form_template': PluginType.admin_form_template
        }

        inlines.append(type(name, base, attrs))
    return inlines


class CmsPageItemInline(StackedInline):
    """
    Custom ``InlineModelAdmin`` subclass used for content types.
    """

    # inline settings
    extra = 0
    fk_name = 'parent'
    template = 'admin/ecms/cmsobject/cmspageitem_inline.html'
    ordering = ('sort_order',)

    # overwritten by subtype
    name = None
    plugin = None
    type_name = None
    ecms_admin_form_template = None


    def __init__(self, *args, **kwargs):
        super(CmsPageItemInline, self).__init__(*args, **kwargs)
        self.verbose_name_plural = u'---- CMS Inline: %s' % (self.verbose_name_plural,)

    @property
    def media(self):
        media = super(CmsPageItemInline, self).media
        if self.plugin:
            media += self.plugin.media  # form fields first, plugin afterwards
        return media


class CmsObjectAdmin(MPTTModelAdmin):
    """
    The admin screen for the ``CmsObject`` object, with lots of customisations.
    """

    # Config list page:
    list_display = ('title', 'status_column', 'modification_date', 'actions_column')
    #list_filter = ('status', 'parent')
    search_fields = ('slug', 'title')
    actions = ['make_published']
    change_list_template = ["admin/ecms/cmsobject/change_list.html"]

    # Configure edit page:
    form = CmsObjectAdminForm
    change_form_template = ["admin/ecms/cmsobject/cmsobject_editor.html",
                            "admin/ecms/cmsobject_editor.html",
                            ]

    # Config add/edit:
    prepopulated_fields = { 'slug': ('title',), }
    raw_id_fields = ['parent']
    fieldsets = (
        (None, {
            'fields': ('title','status','layout'),
        }),
        (_('SEO settings'), {
            'fields': ('slug', 'keywords', 'description'),
            #'classes': ('collapse',),
        }),
        (_('Menu structure'), {
            'fields': ('sort_order', 'parent', 'in_navigation'),
            #'classes': ('collapse',),
        }),
        (_('Publication settings'), {
            'fields': ('publication_date', 'expire_date', 'override_url'),
            #'classes': ('collapse',),
        }),
    )
    radio_fields = {'status': admin.HORIZONTAL}

    # These files need to be loaded before the other plugin code,
    # making plugin development easy (can assume everything is present).
    class Media:
        js = (
            'ecms/admin.js',
            'ecms/ecms_data.js',
            'ecms/ecms_tabs.js',
            'ecms/ecms_layouts.js',
            'ecms/ecms_plugins.js'
        )
        css = {
            'screen': ('ecms/admin.css',)
        }



    # ---- Inline insertion ----


    def __init__(self, model, admin_site):
        super(CmsObjectAdmin, self).__init__(model, admin_site)
        self._initialized_inlines = False


    def get_form(self, request, obj=None, **kwargs):
        self._initialize_ecms_inlines()   # delayed the initialisation a bit
        return super(CmsObjectAdmin, self).get_form(request, obj, **kwargs)


    def _initialize_ecms_inlines(self):
        # Calling it too early places more stress on the Django load mechanisms.
        # e.g. load_middleware() -> import ecms.admin.utils -> processes __init__.py ->
        #      admin.site.register(CmsObjectAdmin) -> CmsObjectAdmin::__init__() -> start looking for plugins -> ImportError
        if not self._initialized_inlines:
            for InlineType in get_pageitem_inlines():
                inline_instance = InlineType(self.model, self.admin_site)
                self.inline_instances.append(inline_instance)

            self._initialized_inlines = True


    # ---- Extra Ajax views ----

    def get_urls(self):
        """
        Introduce more urls
        """
        urls = super(CmsObjectAdmin, self).get_urls()
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


    # ---- Hooking into show/save ----

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        """Include plugin meta information, in the context."""
        plugins = extensions.plugin_pool.get_plugin_classes()
        categories = get_pageitem_categories(plugins)
        categories = dict((PLUGIN_CATEGORIES[k], v) for k, v in categories.iteritems())  # replace ID with title
        context['add_plugin_categories'] = categories

        # And go with standard stuff
        return super(CmsObjectAdmin, self).render_change_form(request, context, add, change, form_url, obj)


    def save_model(self, request, obj, form, change):
        """Automatically store the user in the author field."""
        if not change:
            obj.author = request.user
        obj.save()


    # ---- list actions ----

    STATUS_ICONS = (
        (CmsObject.PUBLISHED, 'img/admin/icon-yes.gif'),
        (CmsObject.DRAFT,     'img/admin/icon-unknown.gif'),
        (CmsObject.HIDDEN,    'img/admin/icon-no.gif'),
    )

    def status_column(self, cmsobject):
        status = cmsobject.status
        title = [rec[1] for rec in CmsObject.STATUSES if rec[0] == status].pop()
        icon  = [rec[1] for rec in self.STATUS_ICONS  if rec[0] == status].pop()
        return u'<img src="%s%s" width="10" height="10" alt="%s" title="%s" />' % (settings.ADMIN_MEDIA_PREFIX, icon, title, title)

    status_column.allow_tags = True
    status_column.short_description = _('Status')


    def actions_column(self, cmsobject):
        return u' '.join(self._actions_column(cmsobject))

    actions_column.allow_tags = True
    actions_column.short_description = _('actions')

    def _actions_column(self, cmsobject):
        assets_root = settings.STATIC_URL or settings.MEDIA_URL
        actions = []
        actions.append(
            u'<a href="add/?%s=%s" title="%s"><img src="%secms/img/admin/page_new.gif" width="16" height="16" alt="%s" /></a>' % (
                self.model._mptt_meta.parent_attr, cmsobject.pk, _('Add child'), assets_root, _('Add child'))
            )

        if hasattr(cmsobject, 'get_absolute_url') and cmsobject.is_published:
            actions.append(
                u'<a href="%s" title="%s" target="_blank"><img src="%secms/img/admin/world.gif" width="16" height="16" alt="%s" /></a>' % (
                    cmsobject.get_absolute_url(), _('View on site'), assets_root, _('View on site'))
                )
        return actions


    # ---- Custom actions ----

    def make_published(self, request, queryset):
        rows_updated = queryset.update(status=CmsObject.PUBLISHED)

        if rows_updated == 1:
            message = "1 page was marked as published."
        else:
            message = "%s pages were marked as published." % rows_updated
        self.message_user(request, message)


    make_published.short_description = _("Mark selected objects as published")
