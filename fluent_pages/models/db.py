"""
Database model for the CMS

It defines the following classes:

* UrlNode
  A item node. Can be an HTML page, image, symlink, etc..

* PageLayout
  The layout of a page, which has regions and a template.
"""
from django.utils.encoding import python_2_unicode_compatible
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _
from parler.models import TranslatableModel, TranslatedFieldsModel
from parler.fields import TranslatedField
from parler.utils import get_language_title, is_multilingual_project
from polymorphic_tree.models import PolymorphicMPTTModel, PolymorphicMPTTModelBase
from fluent_pages.models.fields import TemplateFilePathField, PageTreeForeignKey
from fluent_pages.models.managers import UrlNodeManager
from fluent_pages import appsettings
from fluent_pages.utils.compat import get_user_model_name, transaction_atomic
from parler.utils.context import switch_language
from future.utils import with_metaclass, itervalues, iteritems


def _get_current_site():
    return Site.objects.get_current()


class URLNodeMetaClass(PolymorphicMPTTModelBase):
    """
    Metaclass for all plugin models.

    Set db_table if it has not been customized.
    """

    def __new__(mcs, name, bases, attrs):
        new_class = super(URLNodeMetaClass, mcs).__new__(mcs, name, bases, attrs)

        # Update the table name.
        # Inspired by from Django-CMS, (c) , BSD licensed.
        if name not in ['UrlNode', 'Page']:
            meta = new_class._meta
            if meta.db_table.startswith(meta.app_label + '_'):
                model_name = meta.db_table[len(meta.app_label)+1:]
                meta.db_table = "pagetype_{0}_{1}".format(meta.app_label, model_name)

        return new_class

@python_2_unicode_compatible
class UrlNode(with_metaclass(URLNodeMetaClass, PolymorphicMPTTModel, TranslatableModel)):
    """
    The base class for all nodes; a mapping of an URL to content (e.g. a HTML page, text file, blog, etc..)
    """
    # Some publication states
    DRAFT = 'd'
    PUBLISHED = 'p'
    STATUSES = (
        (PUBLISHED, _('Published')),
        (DRAFT, _('Draft')),
    )

    title = TranslatedField(any_language=True)
    slug = TranslatedField()  # Explicitly added, but not needed
    parent = PageTreeForeignKey('self', blank=True, null=True, related_name='children', verbose_name=_('parent'), help_text=_('You can also change the parent by dragging the page in the list.'))
    parent_site = models.ForeignKey(Site, editable=False, default=_get_current_site)
    #children = a RelatedManager by 'parent'

    # Publication information
    status = models.CharField(_('status'), max_length=1, choices=STATUSES, default=DRAFT, db_index=True)
    publication_date = models.DateTimeField(_('publication date'), null=True, blank=True, db_index=True, help_text=_('''When the page should go live, status must be "Published".'''))
    publication_end_date = models.DateTimeField(_('publication end date'), null=True, blank=True, db_index=True)
    in_navigation = models.BooleanField(_('show in navigation'), default=appsettings.FLUENT_PAGES_DEFAULT_IN_NAVIGATION, db_index=True)
    in_sitemaps = models.BooleanField(_('include in search engine sitemaps'), default=True, db_index=True)
    override_url = TranslatedField()

    # For tagging nodes and locating them in code. This should be avoided if possible,
    # but can be a last resort to link to pages (e.g. a "Terms of Service" page).
    key = models.SlugField(_("page identifier"), choices=appsettings.FLUENT_PAGES_KEY_CHOICES, blank=True, null=True, help_text=_("A unique identifier that is used for linking to this page."))

    # Metadata
    author = models.ForeignKey(get_user_model_name(), verbose_name=_('author'), editable=False)
    creation_date = models.DateTimeField(_('creation date'), editable=False, auto_now_add=True)
    modification_date = models.DateTimeField(_('last modification'), editable=False, auto_now=True)

    # Caching
    _cached_url = TranslatedField()

    # Django settings
    objects = UrlNodeManager()
    _default_manager = UrlNodeManager()

    class Meta:
        app_label = 'fluent_pages'
        ordering = ('tree_id', 'lft',)
        verbose_name = _('URL Node')
        verbose_name_plural = _('URL Nodes')  # Using Urlnode here makes it's way to the admin pages too.
        unique_together = (
            ('parent_site', 'key'),
        )
        permissions = (
            ('change_shared_fields_urlnode', _("Can change Shared fields")),     # The fields shared between languages.
            ('change_override_url_urlnode', _("Can change Override URL field")), # Fpr overriding URLs (e.g. '/' for homepage).
        )

#    class MPTTMeta:
#        order_insertion_by = 'title'

    def __str__(self):
        # This looks pretty nice on the delete page.
        # All other models derive from Page, so they get good titles in the breadcrumb.
        return u", ".join(itervalues(self.get_absolute_urls()))


    # ---- Extra properties ----


    def __init__(self, *args, **kwargs):
        super(UrlNode, self).__init__(*args, **kwargs)

        # Cache a copy of the loaded _cached_url value so we can reliably
        # determine whether it has been changed in the save handler:
        self._original_pub_date = self.publication_date if not self._deferred else None
        self._original_pub_end_date = self.publication_end_date if not self._deferred else None
        self._original_status = self.status if not self._deferred else None
        self._original_parent = self.parent_id if not self._deferred else None

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
        return self.default_url


    @property
    def default_url(self):
        """
        The internal implementation of :func:`get_absolute_url`.
        This function can be used when overriding :func:`get_absolute_url` in the settings.
        For example::

            ABSOLUTE_URL_OVERRIDES = {
                'fluent_pages.Page': lambda o: "http://example.com" + o.default_url
            }
        """
        with switch_language(self):
            try:
                root = reverse('fluent-page').rstrip('/')
            except NoReverseMatch:
                raise ImproperlyConfigured("Missing an include for 'fluent_pages.urls' in the URLConf")

            cached_url = self._cached_url  # May raise TranslationDoesNotExist
            if cached_url is None:
                # This happened with Django 1.3 projects, when .only() didn't have the 'id' field included.
                raise ImproperlyConfigured("UrlNode._cached_url is None for UrlNode!\nUrlNode = {0}".format(self.__dict__))

            return root + cached_url


    def get_absolute_urls(self):
        """
        Return all available URLs to this page.
        """
        result = {}
        for code, cached_url in self.translations.values_list('language_code', '_cached_url'):
            with switch_language(self, code):
                root = reverse('fluent-page').rstrip('/')
                result[code] = root + cached_url

        return result


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
        """
        Return whether the node is published.
        """
        return self.status == self.PUBLISHED


    @property
    def is_draft(self):
        """
        Return whether the node is still a draft.
        """
        return self.status == self.DRAFT


    @property
    def is_first_child(self):
        """
        Return ``True`` when the node is the first sibling.
        """
        return self.is_root_node() or (self.parent and (self.lft == self.parent.lft + 1))


    @property
    def is_last_child(self):
        """
        Return ``True`` when the node is the last sibling.
        """
        return self.is_root_node() or (self.parent and (self.rght + 1 == self.parent.rght))


    @property
    def is_file(self):
        """
        Return ``True`` when the node represents a file (can't have children, doesn't have a layout).
        """
        return self.plugin.is_file


    @property
    def can_have_children(self):
        """
        Return ``True`` when the node can have child nodes.
        """
        # Redefine the model constant 'can_have_children' as property
        # that access the plugin registration system,
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

    # This code runs in a transaction since it's potentially editing a lot of records (all descendant urls).
    @transaction_atomic
    def save(self, *args, **kwargs):
        """
        Save the model, and update caches.
        """
        parent_changed = self.parent_id != self._original_parent
        if parent_changed:
            self._mark_all_translations_dirty()

        super(UrlNode, self).save(*args, **kwargs)  # Already saves translated model.

        # Update state for next save (if object is persistent somewhere)
        self._original_parent = self.parent_id
        self._original_pub_date = self.publication_date
        self._original_pub_end_date = self.publication_end_date
        self._original_status = self.status


    def _mark_all_translations_dirty(self):
        # Update the cached_url of all translations.
        # This triggers _update_cached_url() in save_translation() later.

        # Find all translations that this object has,
        # both in the database, and unsaved local objects.
        # HACK: accessing _translations_cache, skipping <IsMissing> sentinel values.
        all_languages = set(self.get_available_languages()) | set(k for k,v in iteritems(self._translations_cache) if v)  # HACK!
        parent_urls = dict(UrlNode_Translation.objects.filter(master=self.parent_id).values_list('language_code', '_cached_url'))

        for language_code in all_languages:
            # Get the parent-url for the translation (fetched once to speed up)
            parent_url = parent_urls.get(language_code, None)
            if not parent_url:
                fallback = appsettings.FLUENT_PAGES_LANGUAGES.get_fallback_language(language_code)
                parent_url = parent_urls.get(fallback, None)

            translation = self._get_translated_model(language_code)
            translation._fetched_parent_url = parent_url


    def save_translation(self, translation, *args, **kwargs):
        """
        Update the fields associated with the translation.
        This also rebuilds the decedent URLs when the slug changed.
        """
        # Store this object
        self._make_slug_unique(translation)
        self._update_cached_url(translation)
        url_changed = translation.is_cached_url_modified
        super(UrlNode, self).save_translation(translation, *args, **kwargs)

        # Detect changes
        published_changed = self._original_pub_date != self.publication_date \
                         or self._original_pub_end_date != self.publication_end_date \
                         or self._original_status != self.status

        if url_changed or published_changed or translation._fetched_parent_url:
            self._expire_url_caches()

            if url_changed:
                # Performance optimisation: only traversing and updating many records when something changed in the URL.
                self._update_decendant_urls(translation)


    def delete(self, *args, **kwargs):
        super(UrlNode, self).delete(*args, **kwargs)
        self._expire_url_caches()


    # Following of the principles for "clean code"
    # the save() method is split in the 3 methods below,
    # each "do one thing, and only one thing".

    def _make_slug_unique(self, translation):
        """
        Check for duplicate slugs at the same level, and make the current object unique.
        """
        origslug = translation.slug
        dupnr = 1
        while True:
            others = UrlNode.objects.filter(
                parent=self.parent_id,
                translations__slug=translation.slug,
                translations__language_code=translation.language_code
            ).non_polymorphic()

            if appsettings.FLUENT_PAGES_FILTER_SITE_ID:
                others = others.filter(parent_site=self.parent_site_id)

            if self.pk:
                others = others.exclude(pk=self.pk)

            if not others.count():
                break

            dupnr += 1
            translation.slug = "%s-%d" % (origslug, dupnr)


    def _update_cached_url(self, translation):
        """
        Update the URLs
        """
        # This block of code is largely inspired and based on FeinCMS
        # (c) Matthias Kestenholz, BSD licensed

        # determine own URL, taking translation language into account.
        if translation.override_url:
            translation._cached_url = translation.override_url
        else:
            if self.is_root_node():
                parent_url = '/'
            else:
                parent_url = translation.get_parent_cached_url(self)

            # The following shouldn't occur, it means a direct call to Page.objects.create()
            # attempts to add a child node to a file object instead of calling model.full_clean().
            # Make sure the URL space is kept clean.
            if not parent_url[-1] == '/':
                parent_url += '/'

            if self.is_file:
                translation._cached_url = u'{0}{1}'.format(parent_url, translation.slug)
            else:
                translation._cached_url = u'{0}{1}/'.format(parent_url, translation.slug)


    def _update_decendant_urls(self, translation):
        """
        Update the URLs of all decendant pages.
        The method is only called when the URL has changed.
        """
        # This block of code is largely inspired and based on FeinCMS
        # (c) Matthias Kestenholz, BSD licensed

        # Keep cache
        current_language = translation.language_code
        fallback_language = appsettings.FLUENT_PAGES_LANGUAGES.get_fallback_language(current_language)

        cached_page_urls = {
            self.id: translation._cached_url.rstrip('/') + '/'  # ensure slash, even with is_file
        }
        fallback_url = self.safe_translation_getter('_cached_url', language_code=fallback_language)
        if not fallback_url:
            # Page only has a slug for the current language.
            # Can't generate any URLs for sub objects, if they need a fallback language.
            fallback_page_urls = {
                self.id: None,
            }
        else:
            fallback_page_urls = {
                self.id: fallback_url.rstrip('/') + '/'
            }

        # Update all sub objects.
        # even if can_have_children is false, ensure a consistent state for the URL structure
        subobjects = self.get_descendants().order_by('lft', 'tree_id')
        for subobject in subobjects:
            if subobject.has_translation(current_language):
                subobject.set_current_language(current_language)
                use_fallback_base = (subobject.parent_id not in cached_page_urls)  # not present in previous object.
            elif fallback_language:
                # Subobject only has default language.
                # Decendent URLs will be based on this default URL.
                subobject.set_current_language(fallback_language)
                use_fallback_base = True
            else:
                raise NotImplementedError("Tree node #{0} has no active ({1}) or fallback ({2}) language".format(
                    subobject.id, current_language, fallback_language
                ))

            # Set URL, using cache for parent URL.
            if subobject.override_url:
                subobject._cached_url = subobject.override_url  # reaffirms, so enforces consistency
            else:
                # Always construct the fallback URL, to revert to it when needed.
                fallback_base = fallback_page_urls[subobject.parent_id]
                if fallback_base is None:
                    # no base, no URL for sub object. (be explicit here, to detect KeyError)
                    fallback_page_urls[subobject.id] = None
                else:
                    fallback_page_urls[subobject.id] = u'{0}{1}/'.format(fallback_base, subobject.slug)

                if use_fallback_base:
                    base = fallback_base
                else:
                    base = cached_page_urls[subobject.parent_id]

                if base is None:
                    #  no base, no URL for sub object. (be explicit here, to detect KeyError)
                    subobject._cached_url = None
                else:
                    subobject._cached_url = u'{0}{1}/'.format(base, subobject.slug)

            if not use_fallback_base:
                cached_page_urls[subobject.id] = subobject._cached_url

            # call base class, do not recurse
            sub_translation = subobject._translations_cache[subobject.get_current_language()]  # HACK!
            super(UrlNode, subobject).save_translation(sub_translation)
            subobject._expire_url_caches()


    def _expire_url_caches(self):
        """
        Reset all cache keys related to this model.
        """
        cachekeys = [
            # created by _get_pages_of_type()
            'fluent_pages.instance_of.{0}.{1}'.format(self.__class__.__name__, self.parent_site_id),  # urlresolvers._get_pages_of_type()
        ]
        for cachekey in cachekeys:
            cache.delete(cachekey)


@python_2_unicode_compatible
class UrlNode_Translation(TranslatedFieldsModel):
    """
    Translation table for UrlNode.
    This layout is identical to what *django-hvad* uses, to ease migration in the future.
    """
    # Translated fields
    title = models.CharField(_("title"), max_length=255)
    slug = models.SlugField(_("slug"), max_length=50, help_text=_("The slug is used in the URL of the page"))
    override_url = models.CharField(_('Override URL'), editable=True, max_length=300, blank=True, help_text=_('Override the target URL. Be sure to include slashes at the beginning and at the end if it is a local URL. This affects both the navigation and subpages\' URLs.'))
    _cached_url = models.CharField(max_length=300, db_index=True, null=True, blank=True, editable=False)

    # Base fields
    master = models.ForeignKey(UrlNode, related_name='translations', null=True)

    class Meta:
        app_label = 'fluent_pages'
        unique_together = (
            #('master__parent_site', '_cached_url', 'language_code'),
            ('language_code', 'master'),
        )
        verbose_name = _('URL Node translation')
        verbose_name_plural = _('URL Nodes translations')  # Using Urlnode here makes it's way to the admin pages too.

    def __str__(self):
        return u"{0}: {1}".format(get_language_title(self.language_code), self.title)

    def __repr__(self):
        return "<{0}: #{1}, {2}, {3}, master: #{4}>".format(
            self.__class__.__name__, self.pk, self._cached_url, self.language_code, self.master_id
        )

    def __init__(self, *args, **kwargs):
        super(UrlNode_Translation, self).__init__(*args, **kwargs)
        self._original_cached_url = self._cached_url
        self._fetched_parent_url = None  # Allow passing data in UrlNode.save()

    @property
    def is_cached_url_modified(self):
        return self._cached_url != self._original_cached_url

    def save(self, *args, **kwargs):
        if not self.title and not self.slug:
            # If this object gets marked as dirty somehow, avoid corruption of the page tree.
            raise RuntimeError("An UrlNode_Transaction object was created without slug or title, blocking save.")
        super(UrlNode_Translation, self).save(*args, **kwargs)
        self._original_cached_url = self._cached_url

    def get_ancestors(self, ascending=False, include_self=False):
        # For the delete page, mptt_breadcrumb filter in the django-polymorphic-tree templates.
        return self.master.get_ancestors(ascending=ascending, include_self=include_self)

    def get_parent_cached_url(self, master):
        if self._fetched_parent_url:
            return self._fetched_parent_url

        # Need the _cached_url from the parent.
        # Do this in the most efficient way possible.
        qs = UrlNode_Translation.objects.filter(master=master.parent_id).values_list('_cached_url', flat=True)
        try:
            self._fetched_parent_url = qs.filter(language_code=self.language_code)[0]
            return self._fetched_parent_url
        except IndexError:
            pass

        # Need to use fallback
        fallback_language = appsettings.FLUENT_PAGES_LANGUAGES.get_fallback_language(self.language_code)
        try:
            self._fetched_parent_url = qs.filter(language_code=fallback_language)[0]
            return self._fetched_parent_url
        except IndexError:
            pass

        raise NotImplementedError("Tree node #{0} has no active ({1}) or fallback ({2}) language".format(
            self.master_id, self.language_code, fallback_language
        ))



class TranslationDoesNotExist(UrlNode_Translation.DoesNotExist):
    """
    The operation can't be completed, because a translation is missing.
    """

UrlNode_Translation.DoesNotExist = TranslationDoesNotExist


@python_2_unicode_compatible
class Page(UrlNode):
    """
    The base class for all all :class:`UrlNode` subclasses that display pages.

    This is a proxy model that changes the appearance of the node in the admin.
    The :class:`UrlNode` displays the URL path, while this model displays the :attr:`title`.
    """
    class Meta:
        app_label = 'fluent_pages'
        proxy = True
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')

    def __str__(self):
        # self.title is configured with any_language=True, so always returns a value.
        return self.title or self.safe_translation_getter('slug', u"#{0}".format(self.pk), any_language=True)

    # Make PyCharm happy
    # Not reusing UrlNode.objects, as contribute_to_class will change the QuerySet.model value.
    objects = UrlNodeManager()



class SeoPageMixin(models.Model):
    """
    Mixin for adding SEO fields to a page.
    """
    # SEO fields
    meta_keywords = models.CharField(_('keywords'), max_length=255, blank=True, null=True)
    meta_description = models.CharField(_('description'), max_length=255, blank=True, null=True)
    meta_title = models.CharField(_('page title'), max_length=255, blank=True, null=True, help_text=_("When this field is not filled in, the menu title text will be used."))

    class Meta:
        abstract = True

    @property
    def meta_robots(self):
        """
        The value for the ``<meta name="robots" content=".."/>`` tag.
        It defaults to ``noindex`` when :attr:`in_sitemaps` is ``False``.
        """
        # Also exclude from crawling if removed from sitemaps.
        if not self.in_sitemaps:
            return 'noindex'
        else:
            return None



class HtmlPage(Page, SeoPageMixin):
    """
    The base fields for a HTML page of the web site.

    This is an abstract model, which adds the :attr:`meta_keyword` and :attr:`meta_description` fields.
    """

#    objects = UrlNodeManager()

    class Meta:
        abstract = True
        verbose_name_plural = _('Pages')


@python_2_unicode_compatible
class PageLayout(models.Model):
    """
    A ``PageLayout`` object defines a template that can be used by a page.
    """
    # TODO: this should become optional, either allow Database templates, or a hard-coded list in settings.py

    key = models.SlugField(_('key'), help_text=_("A short name to identify the layout programmatically"))
    title = models.CharField(_('title'), max_length=255)
    template_path = TemplateFilePathField('template file', path=appsettings.FLUENT_PAGES_TEMPLATE_DIR)
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
    def __str__(self):
        return self.title

    class Meta:
        app_label = 'fluent_pages'
        ordering = ('title',)
        verbose_name = _('Layout')
        verbose_name_plural = _('Layouts')
