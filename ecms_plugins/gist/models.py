from django.db import models
from django.utils.translation import ugettext_lazy as _
from ecms.models import CmsPageItem

class GistItem(CmsPageItem):
    """
    A reference to a gist item (gist.github.com) that is rendered as source code.
    """
    gist_id = models.IntegerField(_("Gist number"))
    filename = models.CharField(_("Gist filename"), max_length=128, blank=True, help_text=_('Leave the filename empty to display all files in the Gist'))

    class Meta:
        verbose_name = _('Gist')
        verbose_name_plural = _('Gists')
