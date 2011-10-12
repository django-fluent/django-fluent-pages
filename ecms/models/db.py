"""
Database model for the CMS

It defines the following classes:

* CmsSite
  The Site object, with additional properties

* CmsObject
  A item node. Can be an HTML page, image, symlink, etc..

* CmsLayout
  The layout of a page, which has regions and a template.

* CmsRegion
  The region in a template

The page items are derived from ``CmsPageItem``, which
is an abstract model defined in ``ecms.models.pluginmodel``.
"""
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import models
from django.db.transaction import commit_on_success
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _
from ecms.models.fields import TemplateFilePathField

from ecms.models.managers import CmsSiteManager, CmsObjectManager
from ecms.models.modeldata import CmsObjectRegionDict, CmsPageItemList
from ecms import appsettings
from mptt.models import MPTTModel


def _get_current_site():
    return CmsSite.objects.get_current()


# -------- Site structure --------


class CmsSite(Site):
    """
    A wrapper for the standard Site object, to include all global settings for a site (e.g. Google Analytics ID).
    This provides a clean interface for template designers.
    """

    # Template properties
    def _get_title(self):
        """
        Return the title of the site.
        """
        return self.name

    def _get_url(self):
        """
        Return the root/home URL of the site.
        """
        return '/'

    title = property(_get_title)
    url = property(_get_url)


    # Django stuff
    objects = CmsSiteManager()

    class Meta:
        app_label = 'ecms'
        verbose_name = _('Site Settings')
        verbose_name_plural = _('Site Settings')



class CmsObject(MPTTModel):
    """
    A ```CmsObject``` represents one tree node (e.g. HTML page, or blog entry) of the site.
    """

    # Some publication states
    DRAFT = 'd'
    PUBLISHED = 'p'
    EXPIRED = 'e'
    HIDDEN = 'h'
    STATUSES = (
        (PUBLISHED, _('Published')),
        (HIDDEN, _('Hidden')),
        (DRAFT, _('Draft')),
    )

    # Some content types

    # Standard metadata
    title = models.CharField(_('title'), max_length=255)
    slug = models.SlugField(_('slug'), help_text=_("The slug is used in the URL of the page"))
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children', verbose_name=_('parent'))  # related_name created a 'children' property.
    parent_site = models.ForeignKey(CmsSite, editable=False, default=_get_current_site)
    #children = a RelatedManager

    # SEO fields, misc
    keywords = models.CharField(_('keywords'), max_length=255, blank=True)
    description = models.CharField(_('description'), max_length=255, blank=True)
    sort_order = models.IntegerField(editable=True, default=1)

    # Publication information
    layout = models.ForeignKey('CmsLayout', verbose_name=_('Layout'))
    status = models.CharField(_('status'), max_length=1, choices=STATUSES, default=DRAFT)
    publication_date = models.DateTimeField(_('publication date'), null=True, blank=True, help_text=_('''When the page should go live, status must be "Published".'''))
    expire_date = models.DateTimeField(_('publication end date'), null=True, blank=True)
    in_navigation = models.BooleanField(_('show in navigation'), default=True)
    override_url = models.CharField(_('Override URL'), editable=True, max_length=300, blank=True, help_text=_('Override the target URL. Be sure to include slashes at the beginning and at the end if it is a local URL. This affects both the navigation and subpages\' URLs.'))

    # Metadata
    author = models.ForeignKey(User, verbose_name=_('author'), editable=False)
    creation_date = models.DateTimeField(_('creation date'), editable=False, auto_now_add=True)
    modification_date = models.DateTimeField(_('last modification'), editable=False, auto_now=True)

    # Caching
    _cached_url = models.CharField(_('Cached URL'), max_length=300, blank=True, editable=False, default='', db_index=True)

    # Django settings
    objects = CmsObjectManager()

    class Meta:
        app_label = 'ecms'
        ordering = ('lft', 'sort_order', 'title')
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')

    class MPTTMeta:
        order_insertion_by = 'title'

    def __unicode__(self):
        return self.title


    def __repr__(self):
        """
        Overwritten representation, so Django still displays short representations
        while subclasses may display the full text with __unicode__
        """
        return '<%s#%d: %s; %s>' % (self.__class__.__name__, (self.id or 0), self._cached_url, smart_str(self.title))


    # ---- Extra properties ----


    def __init__(self, *args, **kwargs):
        super(CmsObject, self).__init__(*args, **kwargs)
        # Cache a copy of the loaded _cached_url value so we can reliably
        # determine whether it has been changed in the save handler:
        self._original_cached_url = self._cached_url
        self._cached_page_items = None
        self._cached_main_items = None
        self._cached_ancestors = None
        self._cached_region_dict = None
        self.is_current = None    # Can be defined by mark_current()
        self.is_onpath = None     # is an ancestor of the current node (part of the "menu trail").


    def get_absolute_url(self):
        """
        Return the URL to this page.
        """
        # cached_url always points to the URL within the URL config root.
        # when the application is mounted at a subfolder, or the 'cms.urls' config
        # is included at a sublevel, it needs to be prepended.
        root = reverse('ecms-page').rstrip('/')
        return root + self._cached_url


    def _get_supported_plugin_types(self):
        """
        Return the supported page item types which the page can display.
        The returnvalue is an array of types, all derived from CmsPageItem.
        """
        # Enumerate what all regions allow, that's what this page can render.
        types = []
        for region in self.layout.regions.all():
            types += region.supported_plugin_types
        return list(set(types))


    def _get_all_page_items(self):
        """
        Return all models which are associated with the page.
        This is a list of different object types, all inheriting from ``CmsPageItem``.
        """
        if not self._cached_page_items:
            items = []
            # Get all items per object type.
            for PluginType in self.supported_plugin_types:
                query = PluginType.get_model_instances(page=self)
                items.extend(query)

            # order by region, wrap in CmsPageItemList so it can be rendered
            # directly using {{ ecms_page.page_items }}
            items.sort(key=lambda x: x.sort_order)
            self._cached_page_items = CmsPageItemList(items)

        return self._cached_page_items


    def _get_regions(self):
        """
        Access the region information.

        This allows template tags like {{ ecms_page.regions.main }}
        """
        if not self._cached_region_dict:
            # Assume all regions will be read (why else would you include regions in a layout)
            # Therefore, read them all, and construct a dict-like object which provides
            # an API to read the data through a structured interface.
            regions = self.layout.regions.only("key", "role")
            all_page_items = self._get_all_page_items()
            self._cached_region_dict = CmsObjectRegionDict(regions, all_page_items)

        return self._cached_region_dict


    def _get_main_page_items(self):
        """
        Return the main page items.
        """
        if not self._cached_main_items:
            main_keys  = [region.key for region in self.layout.regions.filter(role=CmsRegion.MAIN).only("key")] + ['__main__']
            main_items = [item for item in self.page_items if item.region in main_keys]
            self._cached_main_items = CmsPageItemList(main_items)  # should already be ordered properly

        return self._cached_main_items


    def _get_breadcrumb(self):
        """
        Return the breadcrumb; all parent pages leading to the current page, including current page itself.
        """
        # Cache ancestors, we need them more often
        if not self._cached_ancestors:
            self._cached_ancestors = list(self.get_ancestors())

        nodes = self._cached_ancestors[:]
        nodes.append(self)
        return nodes


    def _is_published(self):
        return self.status == self.PUBLISHED

    def _is_draft(self):
        return self.status == self.DRAFT

    def _is_first_child(self):
        return self.is_root_node() or (self.parent and (self.lft == self.parent.lft + 1))

    def _is_last_child(self):
        return self.is_root_node() or (self.parent and (self.rght + 1 == self.parent.rght))


    # Map to properties (also for templates)
    supported_plugin_types = property(_get_supported_plugin_types)
    all_page_items = property(_get_all_page_items)
    regions = property(_get_regions)
    main_page_items = property(_get_main_page_items)
    breadcrumb = property(_get_breadcrumb)
    url = property(get_absolute_url)
    is_published = property(_is_published)
    is_first_child = property(_is_first_child)
    is_last_child = property(_is_last_child)


    # ---- Page rendering ----


    def get_template_context(self):
        """
        Return all context variables required to render a page properly.

        This includes the ``ecms_page`` and ``ecms_site`` variables.
        """
        context = {
            'ecms_page': self,
            'ecms_site': self.parent_site
        }
        return context


    # ---- Custom behavior ----

    # This code runs in a transaction since it's potentially editing a lot of records (all decendant urls).
    @commit_on_success
    def save(self, *args, **kwargs):
        """
        Save the model, and update caches.
        """
        # Store this object
        self._make_slug_unique()
        self._update_cached_url()
        super(CmsObject, self).save(*args, **kwargs)

        # Update others
        self._update_decendant_urls()
        return super(CmsObject, self).save(*args, **kwargs)


    # Following of the principles for "clean code"
    # the save() method is split in the 3 methods below,
    # each "do one thing, and only one thing".

    def _make_slug_unique(self):
        """
        Check for duplicate slugs at the same level, and make the current object unique.
        """
        origslug = self.slug
        dupnr = 1
        while True:
            others = CmsObject.objects.filter(parent=self.parent, slug=self.slug)
            if self.pk:
                others = others.exclude(pk=self.pk)

            if not others.count():
                break

            dupnr += 1
            self.slug = "%s-%d" % (origslug, dupnr)


    def _update_cached_url(self):
        """
        Update the URLs
        """
        # This block of code is largely inspired and based on FeinCMS
        # (c) Matthias Kestenholz, BSD licensed

        # determine own URL
        if self.override_url:
            self._cached_url = self.override_url
        elif self.is_root_node():
            self._cached_url = u'/%s/' % self.slug
        else:
            self._cached_url = u'%s%s/' % (self.parent._cached_url, self.slug)


    def _update_decendant_urls(self):
        """
        Update the URLs of all decendant pages.
        """
        # This block of code is largely inspired and based on FeinCMS
        # (c) Matthias Kestenholz, BSD licensed

        # Performance optimisation: avoid traversing and updating many records
        # when nothing changed in the URL.
        if self._cached_url == self._original_cached_url:
            return

        # Keep cache
        cached_page_urls = {self.id: self._cached_url}

        # Update all sub objects
        subobjects = self.get_descendants().order_by('lft')
        for subobject in subobjects:
            # Set URL, using cache for parent URL.
            if subobject.override_url:
                subobject._cached_url = subobject.override_url  # reaffirms, so enforces consistency
            else:
                subobject._cached_url = u'%s%s/' % (cached_page_urls[subobject.parent_id], subobject.slug)

            cached_page_urls[subobject.id] = subobject._cached_url

            # call base class, do not recurse
            super(CmsObject, subobject).save()


# -------- Page layout models --------


class CmsLayout(models.Model):
    """
    A ```CmsLayout``` object defines a layout of a page; which content blocks are available.
    """

    key = models.SlugField(_('key'), help_text=_("A short name to identify the layout programmatically"))
    title = models.CharField(_('title'), max_length=255)
    template_path = TemplateFilePathField('template file', path=appsettings.ECMS_TEMPLATE_DIR)
    #regions = a RelatedManager
    #no children
    #unique
    #allowed_children


    def get_template(self):
        """
        Return the template to render this layout.
        """
        from django.template.loader import get_template
        return get_template(self.template_path)


    # Django stuff
    def __unicode__(self):
        return self.title

    class Meta:
        app_label = 'ecms'
        ordering = ('title',)
        verbose_name = _('Layout')
        verbose_name_plural = _('Layouts')


class CmsRegion(models.Model):
    """
    A ```CmsRegion``` is a part of a ```CmsLayout```.
    It defines a specific area of the page where content can be entered.
    """

    # The 'role' field is useful for migrations,
    # e.g. moving from a 2-col layout to a 3-col layout.
    # Based on the role of a pageitem, meaningful conversions can be made.
    MAIN = 'm'
    SIDEBAR = 's'
    RELATED = 'r'
    ROLES = (
        (MAIN, _('Main content')),
        (SIDEBAR, _('Sidebar content')),
        (RELATED, _('Related content'))
    )

    layout = models.ForeignKey(CmsLayout, related_name='regions', verbose_name=_('Layout'))
    key = models.SlugField(_('Template key'), help_text=_("A short name to identify the region in the template code"))
    title = models.CharField(_('tab title'), max_length=255)
    inherited = models.BooleanField(_('use parent contents by default'), editable=False, blank=True)
    role = models.CharField(_('role'), max_length=1, choices=ROLES, default=MAIN)


    @property
    def supported_plugin_types(self):
        """
        Return which plugins this region can render.
        """
        from ecms.extensions import plugin_pool
        all_classes = plugin_pool.get_plugin_classes()
        return all_classes


    def __unicode__(self):
        return self.key + ': ' + self.title

    class Meta:
        app_label = 'ecms'
        ordering = ('title',)
        verbose_name = _('Layout region')
        verbose_name_plural = _('Layout regions')

