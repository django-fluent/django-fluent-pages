from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.base import ModelBase
from django.template.defaultfilters import truncatewords
from django.utils.encoding import smart_str
from django.utils.html import strip_tags
from ecms.models.db import CmsObject
from django.utils.translation import ugettext_lazy as _
import types


class CmsPageItemMetaClass(ModelBase):
    """
    Metaclass for all plugins.

    Set db_table if it has not been customized.
    """
    # Inspired by from Django-CMS, (c) , BSD licensed.

    def __new__(cls, name, bases, attrs):
        new_class = super(CmsPageItemMetaClass, cls).__new__(cls, name, bases, attrs)
        db_table  = new_class._meta.db_table
        app_label = new_class._meta.app_label

        if db_table.startswith(app_label + '_') and name != 'CmsPageItem':
            model_name = db_table[len(app_label)+1:]
            new_class._meta.db_table = "ecmsplugin_%s_%s" % (app_label, model_name)

        return new_class


class CmsPageItem(models.Model):
    """
    A ```PageItem``` is a content part which is displayed at the page.

    The item renders itself by overriding ``render``.
    """
    __metaclass__ = CmsPageItemMetaClass

    # Note the validation settings defined here are not reflected automatically
    # in the ecms admin interface because it uses a custom ModelForm to handle these fields.
    parent = models.ForeignKey(CmsObject)
    sort_order = models.IntegerField(default=1)
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
        return unicode(_(u"{No rendering defined for class '%s'}" % self.__class__.__name__))


    def __unicode__(self):
        # No snippet, but return the full text.
        # works nicer for templates (e.g. mark_safe(main_page_item).
        try:
            return unicode(self.render())
        except Exception, e:
            return '<exception in render(): %s>' % e


    class Meta:
        ordering = ('parent', 'sort_order')
        verbose_name = _('CMS Page item')
        verbose_name_plural = _('CMS Page items')
        abstract = True

    # While being abstract, still have the DoesNotExist object:
    DoesNotExist = types.ClassType('DoesNotExist', (ObjectDoesNotExist,), {})
