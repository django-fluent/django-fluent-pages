"""
Database model for the CMS

It defines the following classes:

* CmsObject
  A item node. Can be an HTML page, image, symlink, etc..

* CmsLayout
  The layout of a page, which has regions and a template.
"""
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import models
from django.db.transaction import commit_on_success
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel, MPTTModelBase, TreeForeignKey
from polymorphic import PolymorphicModel
from polymorphic.base import PolymorphicModelBase
from fluent_pages.models.fields import TemplateFilePathField
from fluent_pages.models.managers import UrlNodeManager
from fluent_pages import appsettings


def _get_current_site():
    return Site.objects.get_current()


def _validate_parent(parent):
    from fluent_pages.extensions import page_type_pool
    if not parent:
        return
    elif isinstance(parent, (int, long)):
        parent = UrlNode.objects.non_polymorphic().values('polymorphic_ctype').get(pk=parent)
        if parent['polymorphic_ctype'] in page_type_pool.get_folder_types():
            return
    elif isinstance(parent, UrlNode):
        if parent.can_have_children:
            return
    else:
        raise ValueError("Unknown parent value")

    raise ValidationError(_("The selected page cannot have sub pages."))


class URLNodeMetaClass(MPTTModelBase, PolymorphicModelBase):
    """
    Metaclass for all plugin models.

    Set db_table if it has not been customized.
    """
    # Inspired by from Django-CMS, (c) , BSD licensed.

    def __new__(mcs, name, bases, attrs):
        new_class = super(URLNodeMetaClass, mcs).__new__(mcs, name, bases, attrs)

        # Update the table name.
        if name not in ['UrlNode', 'Page']:
            meta = new_class._meta
            if meta.db_table.startswith(meta.app_label + '_'):
                model_name = meta.db_table[len(meta.app_label)+1:]
                meta.db_table = "pagetype_{0}_{1}".format(meta.app_label, model_name)

        return new_class


class UrlNode(MPTTModel, PolymorphicModel):
    """
    The base class for all nodes; a mapping of an URL to content (e.g. a HTML page, text file, blog, etc..)
    """
    __metaclass__ = URLNodeMetaClass

    # Some publication states
    DRAFT = 'd'
    PUBLISHED = 'p'
    STATUSES = (
        (PUBLISHED, _('Published')),
        (DRAFT, _('Draft')),
    )

    title = models.CharField(_('title'), max_length=255)
    slug = models.SlugField(_('slug'), help_text=_("The slug is used in the URL of the page"))
    parent = TreeForeignKey('self', blank=True, null=True, related_name='children', verbose_name=_('parent'), validators=[_validate_parent])
    parent_site = models.ForeignKey(Site, editable=False, default=_get_current_site)
    #children = a RelatedManager by 'parent'

    # Publication information
    status = models.CharField(_('status'), max_length=1, choices=STATUSES, default=DRAFT)
    publication_date = models.DateTimeField(_('publication date'), null=True, blank=True, help_text=_('''When the page should go live, status must be "Published".'''))
    expire_date = models.DateTimeField(_('publication end date'), null=True, blank=True)
    in_navigation = models.BooleanField(_('show in navigation'), default=True)
    sort_order = models.IntegerField(default=1)   # TODO: affect mptt sort ordering.
    override_url = models.CharField(_('Override URL'), editable=True, max_length=300, blank=True, help_text=_('Override the target URL. Be sure to include slashes at the beginning and at the end if it is a local URL. This affects both the navigation and subpages\' URLs.'))

    # Metadata
    author = models.ForeignKey(User, verbose_name=_('author'), editable=False)
    creation_date = models.DateTimeField(_('creation date'), editable=False, auto_now_add=True)
    modification_date = models.DateTimeField(_('last modification'), editable=False, auto_now=True)

    # Caching
    _cached_url = models.CharField(_('Cached URL'), max_length=300, blank=True, editable=False, default='', db_index=True)

    # Django settings
    objects = UrlNodeManager()

    class Meta:
        app_label = 'fluent_pages'
        ordering = ('lft', 'sort_order', 'title')
        verbose_name = _('URL Node')
        verbose_name_plural = _('URL Nodes')  # Using Urlnode here makes it's way to the admin pages too.

    class MPTTMeta:
        order_insertion_by = 'title'

    def __unicode__(self):
        # This looks pretty nice on the delete page.
        # All other models derive from Page, so they get good titles in the breadcrumb.
        return unicode(self.get_absolute_url())


    # ---- Extra properties ----


    def __init__(self, *args, **kwargs):
        super(UrlNode, self).__init__(*args, **kwargs)
        # Cache a copy of the loaded _cached_url value so we can reliably
        # determine whether it has been changed in the save handler:
        self._original_cached_url = self._cached_url
        self._cached_ancestors = None
        self.is_current = None    # Can be defined by mark_current()
        self.is_onpath = None     # is an ancestor of the current node (part of the "menu trail").


    def get_absolute_url(self):
        """
        Return the URL to this page.
        """
        # cached_url always points to the URL within the URL config root.
        # when the application is mounted at a subfolder, or the 'cms.urls' config
        # is included at a sublevel, it needs to be prepended.
        try:
            root = reverse('fluent-page').rstrip('/')
        except NoReverseMatch:
            raise ImproperlyConfigured("Missing an include for 'fluent_pages.urls' in the URLConf")
        return root + self._cached_url


    @property
    def url(self):
        """
        The URL of the page, provided for template code.
        """
        # Mapped to property for templates.
        # Not done directly using url = property(get_absolute_url),
        # so get_absolute_url() can be overwritten.
        return self.get_absolute_url()


    @property
    def last_modified(self):
        """
        Return the last modification date of the page.
        Currently this is the last time the page was saved.
        This is implemented as separate property,
        to be extended to page content in the future.
        """
        return self.modification_date


    @property
    def breadcrumb(self):
        """
        Return the breadcrumb; all parent pages leading to the current page, including current page itself.
        """
        # Cache ancestors, we need them more often
        if not self._cached_ancestors:
            self._cached_ancestors = list(self.get_ancestors())

        nodes = self._cached_ancestors[:]
        nodes.append(self)
        return nodes


    @property
    def is_published(self):
        return self.status == self.PUBLISHED


    @property
    def is_draft(self):
        return self.status == self.DRAFT


    @property
    def is_first_child(self):
        return self.is_root_node() or (self.parent and (self.lft == self.parent.lft + 1))


    @property
    def is_last_child(self):
        return self.is_root_node() or (self.parent and (self.rght + 1 == self.parent.rght))


    @property
    def is_file(self):
        return self.plugin.is_file


    @property
    def can_have_children(self):
        plugin = self.plugin
        return plugin.can_have_children and not plugin.is_file


    @property
    def plugin(self):
        """
        Access the parent plugin which renders this model.
        """
        from fluent_pages.extensions import page_type_pool
        if self.__class__ in (UrlNode, Page):
            # Also allow a non_polymorphic() queryset to resolve the plugin.
            # Corresponding page_type_pool method is still private on purpose.
            # Not sure the utility method should be public, or how it should be named.
            return page_type_pool._get_plugin_by_content_type(self.polymorphic_ctype_id)
        else:
            return page_type_pool.get_plugin_by_model(self.__class__)


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
        super(UrlNode, self).save(*args, **kwargs)

        # Update others
        self._update_decendant_urls()
        return super(UrlNode, self).save(*args, **kwargs)


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
            others = UrlNode.objects.filter(parent=self.parent, slug=self.slug).non_polymorphic()
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
        elif self.is_file:
            self._cached_url = u'/%s' % self.slug
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
        cached_page_urls = {
            self.id: self._cached_url.rstrip('/') + '/'  # ensure slash, even with is_file
        }

        # Update all sub objects.
        # even if can_have_children is false, ensure a consistent state for the URL structure
        subobjects = self.get_descendants().order_by('lft')
        for subobject in subobjects:
            # Set URL, using cache for parent URL.
            if subobject.override_url:
                subobject._cached_url = subobject.override_url  # reaffirms, so enforces consistency
            else:
                subobject._cached_url = u'%s%s/' % (cached_page_urls[subobject.parent_id], subobject.slug)

            cached_page_urls[subobject.id] = subobject._cached_url

            # call base class, do not recurse
            super(UrlNode, subobject).save()



class Page(UrlNode):
    """
    The base class for all all :class:`UrlNode` subclasses that display pages.
    """
    class Meta:
        app_label = 'fluent_pages'
        proxy = True
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')

    def __unicode__(self):
        return self.title or self.slug



class HtmlPage(Page):
    """
    The base fields for a HTML page of the web site.
    """
    # SEO fields
    keywords = models.CharField(_('keywords'), max_length=255, blank=True)
    description = models.CharField(_('description'), max_length=255, blank=True)

#    objects = UrlNodeManager()

    class Meta:
        abstract = True
        verbose_name_plural = _('Pages')



class PageLayout(models.Model):
    """
    A ```PageLayout``` object defines a layout of a page; which content blocks are available.
    """

    key = models.SlugField(_('key'), help_text=_("A short name to identify the layout programmatically"))
    title = models.CharField(_('title'), max_length=255)
    template_path = TemplateFilePathField('template file', path=appsettings.FLUENT_PAGES_TEMPLATE_DIR)
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
        app_label = 'fluent_pages'
        ordering = ('title',)
        verbose_name = _('Layout')
        verbose_name_plural = _('Layouts')
