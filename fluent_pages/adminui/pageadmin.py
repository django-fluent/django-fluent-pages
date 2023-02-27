import copy

from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.contrib.contenttypes.models import ContentType
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.utils.functional import lazy
from django.utils.http import urlencode

from fluent_pages.models import Page

from .urlnodechildadmin import UrlNodeAdminForm, UrlNodeChildAdmin
from .urlnodeparentadmin import UrlNodeParentAdmin


class PageAdminForm(UrlNodeAdminForm):
    """
    The base class for all admin forms.

    This form validates the "Slug" and "Override URL" fields.
    """


class DefaultPageParentAdmin(UrlNodeParentAdmin):
    """
    This admin class renders the *list* of the page tree.

    Since this admin displays polymorphic objects, the edit/delete pages
    are actually handled by the :class:`PageAdmin` class.

    The admin class can be extended with mixins by defining :ref:`FLUENT_PAGES_PARENT_ADMIN_MIXIN`.
    """


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

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if field is None:
            return None

        # Hack the ForeignKeyRawIdWidget to display a selector for the base model too.
        # It correctly detects that the parent field actually points to an UrlNode, instead of Page.
        # Since UrlNode is not registered in the admin, it won't display the selector. Overriding that here.
        if db_field.name == "parent" and isinstance(field.widget, ForeignKeyRawIdWidget):
            field.widget.rel = copy.copy(field.widget.rel)
            field.widget.rel.model = Page

        return field

    @property
    def change_form_template(self):
        templates = super().change_form_template
        opts = self.model._meta
        app_label = opts.app_label

        return [
            "admin/fluent_pages/pagetypes/{}/{}/change_form.html".format(
                app_label, opts.object_name.lower()
            ),
            f"admin/fluent_pages/pagetypes/{app_label}/change_form.html",
        ] + templates

    def render_change_form(self, request, context, add=False, change=False, form_url="", obj=None):
        # Include a 'base_change_form_template' in the context, make it easier to extend
        # the ct_id parameter can be skipped when the direct URL is used (instead of the proxied polymorphic add view)
        context.update(
            {
                "base_change_form_template": self.base_change_form_template,
                "default_change_form_template": _lazy_get_default_change_form_template(self),
                "ct_id": int(
                    ContentType.objects.get_for_model(obj, for_concrete_model=False).pk
                    if change
                    else request.GET.get("ct_id", 0)
                ),  # HACK for polymorphic admin
            }
        )
        # django-parler does this, so we have to do it too
        form_url = add_preserved_filters(
            {
                "preserved_filters": urlencode({"ct_id": context["ct_id"]}),
                "opts": self.model._meta,
            },
            form_url,
        )
        return super().render_change_form(
            request, context, add=add, change=change, form_url=form_url, obj=obj
        )


def _get_default_change_form_template(self):
    return _select_template_name(DefaultPageChildAdmin.change_form_template.__get__(self))


_lazy_get_default_change_form_template = lazy(_get_default_change_form_template, str)


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
                template_name = str(template_name)  # consistent value for lazy() function.
                _cached_name_lookups[template_name_list] = template_name
                return template_name

        return None
