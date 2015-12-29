import django

native_str = str  # no future.builtins.str, breaks default_change_form_template in Django 1.5, Python 2.7.5
from future.builtins import int
import copy
from django.utils.http import urlencode
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.contrib.contenttypes.models import ContentType
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.utils.functional import lazy
from fluent_utils.django_compat import add_preserved_filters
from fluent_pages.models import Page
from .urlnodechildadmin import UrlNodeChildAdmin, UrlNodeAdminForm
from .urlnodeparentadmin import UrlNodeParentAdmin


class PageAdminForm(UrlNodeAdminForm):
    """
    The base class for all admin forms.

    This form validates the "Slug" and "Override URL" fields.
    """
    pass


class DefaultPageParentAdmin(UrlNodeParentAdmin):
    """
    This admin class renders the *list* of the page tree.

    Since this admin displays polymorphic objects, the edit/delete pages
    are actually handled by the :class:`PageAdmin` class.

    The admin class can be extended with mixins by defining :ref:`FLUENT_PAGES_PARENT_ADMIN_MIXIN`.
    """
    pass


class DefaultPageChildAdmin(UrlNodeChildAdmin):
    """
    The base class for administrating pages.
    When a custom page type implements a custom admin, use this class as its base.
    See the code in ``fluent_pages/pagetypes/*/admin.py`` for examples.
    To deal with model inheritence, define the fieldsets using the :attr:`base_fieldsets` option.
    For example:

    .. code-block:: python

        base_fieldsets = (
            PageAdmin.FIELDSET_GENERAL,
            PageAdmin.FIELDSET_MENU,
            PageAdmin.FIELDSET_PUBLICATION,
        )

    By using :attr:`base_fieldsets` instead of the :attr:`ModelAdmin.fieldsets <django.contrib.admin.ModelAdmin.fieldsets>` attribute,
    any additional fields from a derived model will be displayed in a separate fieldset automatically.
    The title of the fieldset is configurable with the :attr:`extra_fieldset_title` attribute.
    It's "Contents" by default.

    The admin class can be extended with mixins by defining :ref:`FLUENT_PAGES_CHILD_ADMIN_MIXIN`.
    """
    base_model = Page
    base_form = PageAdminForm
    readonly_shared_fields = UrlNodeChildAdmin.readonly_shared_fields

    #: The default template name, which is available in the template context.
    #: Use ``{% extend base_change_form_template %}`` in templates to inherit from it.
    base_change_form_template = "admin/fluent_pages/page/base_change_form.html"

    class Media:
        js = ('fluent_pages/admin/django13_fk_raw_id_fix.js',)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(DefaultPageChildAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if field is None:
            return None

        # Hack the ForeignKeyRawIdWidget in Django 1.4 to display a selector for the base model too.
        # It correctly detects that the parent field actually points to an UrlNode, instead of Page.
        # Since UrlNode is not registered in the admin, it won't display the selector. Overriding that here.
        # It also partially fixes Django 1.3, which would wrongly point the url to ../../../fluent_pages/urlnode/ otherwise.
        if db_field.name == 'parent' and isinstance(field.widget, ForeignKeyRawIdWidget):
            field.widget.rel = copy.copy(field.widget.rel)
            if django.VERSION >= (1, 9):
                field.widget.rel.model = Page
            else:
                field.widget.rel.to = Page

        return field

    @property
    def change_form_template(self):
        templates = super(DefaultPageChildAdmin, self).change_form_template
        opts = self.model._meta
        app_label = opts.app_label

        return [
            "admin/fluent_pages/pagetypes/{0}/{1}/change_form.html".format(app_label, opts.object_name.lower()),
            "admin/fluent_pages/pagetypes/{0}/change_form.html".format(app_label),
        ] + templates

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        # Include a 'base_change_form_template' in the context, make it easier to extend
        context.update({
            'base_change_form_template': self.base_change_form_template,
            'default_change_form_template': _lazy_get_default_change_form_template(self),
            'ct_id': int(ContentType.objects.get_for_model(obj).pk if change else request.GET['ct_id']) # HACK for polymorphic admin
        })
        # django-parler does this, so we have to do it too, affects django>=1.6
        form_url = add_preserved_filters({'preserved_filters': urlencode({'ct_id': context['ct_id']}), 'opts': self.model._meta}, form_url)
        return super(DefaultPageChildAdmin, self).render_change_form(request, context, add=add, change=change, form_url=form_url, obj=obj)


def _get_default_change_form_template(self):
    return _select_template_name(DefaultPageChildAdmin.change_form_template.__get__(self))

_lazy_get_default_change_form_template = lazy(_get_default_change_form_template, native_str)


_cached_name_lookups = {}


def _select_template_name(template_name_list):
    """
    Given a list of template names, find the first one that exists.
    """
    if not isinstance(template_name_list, tuple):
        template_name_list = tuple(template_name_list)

    try:
        return _cached_name_lookups[template_name_list]
    except KeyError:
        # Find which template of the template_names is selected by the Django loader.
        for template_name in template_name_list:
            try:
                # TODO: For Django 1.8, add using= parameter so it only selects templates from the same engine.
                get_template(template_name)
            except TemplateDoesNotExist:
                continue
            else:
                template_name = native_str(template_name)  # consistent value for lazy() function.
                _cached_name_lookups[template_name_list] = template_name
                return template_name

        return None
