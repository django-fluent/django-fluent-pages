"""
Database model for django-enterprise-cms

It defines the following classes:

* CmsSite
  The Site object, with additional properties

* CmsObject
  A item node. Can be an HTML page, image, etc..

* CmsLayout
  The layout of a page, which has regions and a template.

* CmsRegion
  The region in a template

* CmsPageItem
  An item (or "widget") which can be displayed in a region. For example

  * CmsTextItem  - HTML text

"""
from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.conf import settings

# Util functions
from django.core.validators import validate_slug
from django.core.exceptions import ObjectDoesNotExist
from django.db.transaction import commit_on_success
from django.template.defaultfilters import truncatewords
from django.utils.encoding import smart_str
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _

from ecms.managers import CmsSiteManager, CmsObjectManager
from ecms.contents import CmsObjectRegionDict, CmsPageItemList
import mptt
import types


# -------- Init code --------

# MPTT 0.3
MPTTModel = models.Model

try:
    # MPTT 0.4.
    # placed below MPTT 0.3 definition so IDE's detect the base class properly.
    from mptt.models import MPTTModel
except ImportError:
    pass

def _get_current_site():
    return CmsSite.objects.get_current()


# -------- Site structure --------


class CmsSite(Site):
    """
    A CmsSite holds all global settings for a site
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
        return self._cached_url


    def _get_supported_page_item_types(self):
        """
        Return the supported page item types which the page can display.
        The returnvalue is an array of types, all derived from CmsPageItem.
        """
        return CmsPageItem.__subclasses__()


    def _get_page_items(self):
        """
        Return all page items which are associated with the page.
        This is a list of different object types, all inheriting from ``CmsPageItem``.
        """
        if not self._cached_page_items:
            items = []
            # Get all items per object type.
            for ItemType in self.supported_page_item_types:
                query = ItemType.objects.filter(parent=self.id)
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
            all_page_items = self._get_page_items()
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

    def is_draft(self):
        return self.status == self.DRAFT


    # Map to properties (also for templates)
    supported_page_item_types = property(_get_supported_page_item_types)
    page_items = property(_get_page_items)
    regions = property(_get_regions)
    main_page_items = property(_get_main_page_items)
    breadcrumb = property(_get_breadcrumb)
    url = property(get_absolute_url)
    is_published = property(_is_published)


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
    template_path = models.FilePathField('template file', path=settings.TEMPLATE_DIRS[0], match=r'.*\.html$', recursive=True)
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


    def __unicode__(self):
        return self.key + ': ' + self.title

    class Meta:
        ordering = ('title',)
        verbose_name = _('Layout region')
        verbose_name_plural = _('Layout regions')


# -------- Page contents--------


class CmsPageItem(models.Model):
    """
    A ```PageItem``` is a content part which is displayed at the page.

    The item renders itself by overriding ``__unicode__``.
    """
    # Settings to override
    ecms_admin_form = None
    ecms_admin_form_template = "admin/ecms/cmspageitem/admin_form.html"

    # Note the validation settings defined here are not reflected automatically
    # in the ecms admin interface because it uses a custom ModelForm to handle these fields.
    parent = models.ForeignKey(CmsObject)
    sort_order = models.IntegerField(editable=False, default=1)
    region = models.CharField(max_length=128, default='__main__')


    def save(self, *args, **kwargs):
        """
        Make sure the region is set to '__main__' when nothing is filled in.
        """
        if not self.region:
            self.region = '__main__'
        super(CmsPageItem, self).save(*args, **kwargs)


    def __repr__(self):
        """
        Overwritten representation, so Django still displays short representations
        while subclasses may display the full text with __unicode__
        """
        return '<%s: #%d, region=%s, content=%s>' % (self.__class__.__name__, self.id or 0, self.region, smart_str(truncatewords(strip_tags(unicode(self)), 10)))


    def render(self):
        """
        By default, the unicode string is rendered.
        """
        return unicode(self)


    def __unicode__(self):
        return _(u"{No rendering defined for class '%s'}" % self.__class__.__name__)


    class Meta:
        ordering = ('parent', 'sort_order')
        verbose_name = _('CMS Page item')
        verbose_name_plural = _('CMS Page items')
        abstract = True

    # While being abstrct, still have the DoesNotExist object:
    DoesNotExist = types.ClassType('DoesNotExist', (ObjectDoesNotExist,), {})


class CmsTextItem(CmsPageItem):
    """A snippet of text to display on a page"""
    text = models.TextField(_('text'), blank=True)

    ecms_admin_form_template = "admin/ecms/cmstextitem/admin_form.html"

    class Meta:
        verbose_name = _('Text item')
        verbose_name_plural = _('Text items')

    def __unicode__(self):
        # No snippet, but return the full text.
        # works nicer for templates (e.g. mark_safe(main_page_item).
        # Included in a DIV, so the next item will be displayed below.
        return "<div>" + self.text + "</div>"


# -------- Legacy mptt support --------

if hasattr(mptt, 'register'):
    # MPTT 0.3 legacy support
    mptt.register(CmsObject)

