"""
Database model for django-enterprise-cms
"""
from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

# Util functions
from django.core.validators import validate_slug
from django.core.exceptions import ObjectDoesNotExist
from django.db.transaction import commit_on_success
from django.template.defaultfilters import truncatewords
from django.utils.encoding import smart_str
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _

from ecms.managers import CmsSiteManager, CmsObjectManager
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


# -------- Models --------


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
        verbose_name = _('CMS Site Settings')
        verbose_name_plural = _('CMS Site Settings')



class CmsObject(MPTTModel):
    """
    A ```CmsObject``` represents one tree node (e.g. HTML page) of the site.
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
    slug = models.SlugField(_('slug'), validators=[validate_slug], help_text=_("The slug is used in the URL of the page"))
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children', verbose_name=_('parent'))  # related_name created a 'children' property.
    parent_site = models.ForeignKey(CmsSite, editable=False, default=_get_current_site)

    # SEO fields, misc
    keywords = models.CharField(_('keywords'), max_length=255, blank=True)
    description = models.CharField(_('description'), max_length=255, blank=True)
    sort_order = models.IntegerField(editable=False, default=1)

    # Publication information
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
        verbose_name = _('CMS Page')
        verbose_name_plural = _('CMS Pages')

    class MPTTMeta:
        order_insertion_by = 'title'

    def __unicode__(self):
        return self.title


    def __repr__(self):
        """
        Overwritten representation, so Django still displays short representations
        while subclasses may display the full text with __unicode__
        """
        return '<%s#%d: %s; %s>' % (self.__class__.__name__, self.id, self._cached_url, smart_str(self.title))


    # ---- Extra properties ----


    def __init__(self, *args, **kwargs):
        super(CmsObject, self).__init__(*args, **kwargs)
        # Cache a copy of the loaded _cached_url value so we can reliably
        # determine whether it has been changed in the save handler:
        self._original_cached_url = self._cached_url
        self._cached_main_item = None
        self._cached_ancestors = None
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


    def _get_page_items(self, subtypes=None, region=None):
        """
        Return all page items which are associated with the page.
        """
        objects = []
        for ItemType in (subtypes or self.supported_page_item_types):
            # Get all items per type.
            query = ItemType.objects.filter(parent=self.id)
            if region:
                query = query.filter(region=region)

            # Execute query
            objects.extend(query)

        objects.sort(key=lambda x: x.sort_order)
        return objects


    def _get_main_page_item(self):
        """
        Return the main page items.
        """
        if self._cached_main_item:
            return self._cached_main_item

        # Get item
        items = self._get_page_items(region='__main__')
        if not items:
            raise CmsPageItem.DoesNotExist("No CmsPageItem deriative found with region '__main__'.")

        self._cached_main_item = items[0]
        return items[0]


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
    main_page_item = property(_get_main_page_item)
    breadcrumb = property(_get_breadcrumb)
    url = property(get_absolute_url)
    is_published = property(_is_published)


    # ---- Custom behavior ----

    # This code runs in a transaction since it's potentially editing a lot of records.
    @commit_on_success
    def save(self, *args, **kwargs):
        """
        Save the model, and update caches.
        """
        # Check for duplicate slugs at the same level
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

        # Update the URLs
        # This block of code is largely inspired and based on FeinCMS
        # (c) Matthias Kestenholz, BSD licensed

        cached_page_urls = {}

        # determine own URL
        if self.override_url:
            self._cached_url = self.override_url
        elif self.is_root_node():
            self._cached_url = u'/%s/' % self.slug
        else:
            self._cached_url = u'%s%s/' % (self.parent._cached_url, self.slug)

        # And store this object
        super(CmsObject, self).save(*args, **kwargs)
        cached_page_urls[self.id] = self._cached_url

        # Okay, we changed the URL -- remove the old stale entry from the cache
#        if settings.FEINCMS_USE_CACHE:
#            ck = 'PAGE-FOR-URL-' + self._original_cached_url.strip('/')
#            django_cache.delete(ck)

        # Performance optimisation: avoid traversing and updating many records
        # when nothing changed in the URL.
        if self._cached_url == self._original_cached_url:
            return

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

        return super(CmsObject, self).save(*args, **kwargs)



class CmsPageItem(models.Model):
    """
    A ```PageItem``` is a content part which is displayed at the page.
    """

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
        return '<%s: #%d, region=%s, content=%s>' % (self.__class__.__name__, self.id, self.region, smart_str(truncatewords(strip_tags(unicode(self)), 10)))


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

    class Meta:
        verbose_name = _('Text item')
        verbose_name_plural = _('Text items')

    def __unicode__(self):
        # No wrapping, but return the full text.
        # works nicer for templates (e.g. mark_safe(main_page_item).
        return self.text



# -------- Legacy mptt support --------

if hasattr(mptt, 'register'):
    # MPTT 0.3 legacy support
    mptt.register(CmsObject)