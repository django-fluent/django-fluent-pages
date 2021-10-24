from fluent_utils.load import import_settings_class

from fluent_pages import appsettings

from .pageadmin import DefaultPageChildAdmin, DefaultPageParentAdmin

# Allow to extend the admin. Note this is pretty invasive,
# and custom changes always need to be tested.
if not appsettings.FLUENT_PAGES_PARENT_ADMIN_MIXIN:
    PageParentAdmin = DefaultPageParentAdmin
else:
    _ParentMixin = import_settings_class("FLUENT_PAGES_PARENT_ADMIN_MIXIN")
    PageParentAdmin = type("PageParentAdmin", (_ParentMixin, DefaultPageParentAdmin), {})

if not appsettings.FLUENT_PAGES_CHILD_ADMIN_MIXIN:
    PageChildAdmin = DefaultPageChildAdmin
else:
    _ChildMixin = import_settings_class("FLUENT_PAGES_CHILD_ADMIN_MIXIN")
    PageChildAdmin = type("PageAdmin", (_ChildMixin, DefaultPageChildAdmin), {})


# Keep using the older import name everywhere.
# Plugins don't have to be aware of the different between parent/child admins.
PageAdmin = PageChildAdmin
