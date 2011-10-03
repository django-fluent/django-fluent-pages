from django.db import models
from django.utils.translation import ugettext_lazy as _
from form_designer.models import FormDefinition
from ecms.models.pluginmodel import CmsPageItem


class FormDesignerLink(CmsPageItem):
    form_definition = models.ForeignKey(FormDefinition, verbose_name=_('Form'))

    class Meta:
        verbose_name = _('Form link')
        verbose_name_plural = _('Form links')
