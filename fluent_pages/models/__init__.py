"""
The data layer of the CMS, exposing all database models.

The objects can be imported from the main package.
There are several sub packages:

    db: The database models
    managers: Additional manager classes
    modeldata: Classes that expose model data in a sane way (for template designers)
    navigation: The menu navigation nodes (for template designers)
"""

# Like django.db.models, or django.forms,
# have everything split into several packages
from django.conf import settings
from fluent_pages.forms.fields import PageChoiceField
import fluent_pages.models.db
from .db import UrlNode, UrlNode_Translation, Page, HtmlPage, HtmlPageTranslation, PageLayout
from .managers import UrlNodeManager, UrlNodeQuerySet

__all__ = [
    'UrlNode',
    'UrlNode_Translation',
    'UrlNodeManager',
    'UrlNodeQuerySet',
    'Page',
    'HtmlPage',
    'HtmlPageTranslation',
    'PageLayout'
]


def _register_cmsfield_url_type():
    try:
        from any_urlfield.models import AnyUrlField
    except ImportError:
        pass
    else:
        import any_urlfield
        from django import forms
        from distutils.version import StrictVersion
        from any_urlfield.forms.widgets import SimpleRawIdWidget

        if StrictVersion(any_urlfield.__version__) >= StrictVersion('2.0a1'):
            # Allow lambda parameter for late evaluation.
            AnyUrlField.register_model(Page, form_field=lambda: PageChoiceField(widget=SimpleRawIdWidget(Page)))
        else:
            # This will run a query at import time!
            AnyUrlField.register_model(Page, form_field=PageChoiceField(widget=SimpleRawIdWidget(Page)))


if 'any_urlfield' in settings.INSTALLED_APPS:
    _register_cmsfield_url_type()
