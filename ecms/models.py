"""
Database model for django-enterprise-cms
"""
from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from django.conf import settings
from django.core.validators import validate_slug
from django.utils.translation import ugettext_lazy as _
from django.utils.html import strip_tags
from django.forms.models import model_to_dict
from django.template.defaultfilters import truncatewords

from ecms.managers import CmsObjectManager
import mptt


# -------- Init code --------

try:
    # MPTT 0.4
    from mptt.models import MPTTModel
except ImportError:
    # MPTT 0.3
    MPTTModel = models.Model


def _get_current_site():
    id = settings.SITE_ID
    try:
        return CmsSite.objects.get(pk=id)
    except CmsSite.DoesNotExist:
        # Create CmsSite object on demand, populate with existing site values
        # so nothing is overwritten with empty values
        site = Site.objects.get_current()
        wrapper = CmsSite(**model_to_dict(site))
        wrapper.save()
        return wrapper


# -------- Models --------


class CmsSite(Site):
    """
    A CmsSite holds all global settings for a site
    """

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
    title = models.CharField(max_length=255)
    slug = models.SlugField(validators=[validate_slug], help_text=_("The slug is used in the URL of the page"))
    parent = models.ForeignKey('self', blank=True, null=True, related_name=_('children'), verbose_name=_('parent'))
    parent_site = models.ForeignKey(CmsSite, editable=False, default=_get_current_site)

    # SEO fields, misc
    keywords = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    sort_order = models.IntegerField(editable=False, default=1)

    # Publication information
    status = models.CharField(_('status'), max_length=1, choices=STATUSES, default=DRAFT)
    publication_date = models.DateTimeField(_('publication date'), null=True, blank=True, help_text=_('''When the page should go live, status must be "Published".'''))
    expire_date = models.DateTimeField(_('publication end date'), null=True, blank=True)

    # Metadata
    author = models.ForeignKey(User, verbose_name=_('author'), editable=False)
    creation_date = models.DateTimeField(_('creation date'), editable=False, auto_now_add=True)
    modification_date = models.DateTimeField(_('last modification'), editable=False, auto_now=True)

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


    # ---- Custom behavior ----

    def save(self, *args, **kwargs):
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

        return super(CmsObject, self).save(*args, **kwargs)



class CmsPageItem(models.Model):
    """
    A ```PageItem``` is a content part which is displayed at the page.
    """

    # Note the validation settings defined here are not reflected automatically
    # in the ecms admin interface because it uses a custom ModelForm to handle these fields.
    parent = models.ForeignKey(CmsObject)
    sort_order = models.IntegerField(editable=False, default=1)
    region = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ('parent', 'sort_order')
        verbose_name = _('CMS Page item')
        verbose_name_plural = _('CMS Page items')
        abstract = True


class CmsTextItem(CmsPageItem):
    """A snippet of text to display on a page"""
    text = models.TextField(_('text'), blank=True)

    class Meta:
        verbose_name = _('Text item')
        verbose_name_plural = _('Text items')

    def __unicode__(self):
        return truncatewords(strip_tags(self.text), 10)



# -------- Legacy mptt support --------

if hasattr(mptt, 'register'):
    # MPTT 0.3 legacy support
    mptt.register(CmsObject)