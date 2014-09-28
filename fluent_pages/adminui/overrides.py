from fluent_pages import appsettings
from .pageadmin import DefaultPageParentAdmin, DefaultPageChildAdmin
from fluent_utils.load import import_settings_class


# Allow to extend the admin. Note this is pretty invasive,
# and custom changes always need to be tested.
if appsettings.FLUENT_PAGES_PARENT_ADMIN_MIXIN:
    PageParentAdmin = type("PageParentAdmin", (import_settings_class('FLUENT_PAGES_PARENT_ADMIN_MIXIN'), DefaultPageParentAdmin), {})
else:
    PageParentAdmin = DefaultPageParentAdmin

if appsettings.FLUENT_PAGES_CHILD_ADMIN_MIXIN:
    PageChildAdmin = type("PageAdmin", (import_settings_class('FLUENT_PAGES_CHILD_ADMIN_MIXIN'), DefaultPageChildAdmin), {})
else:
    PageChildAdmin = DefaultPageChildAdmin


# Keep using the older import name everywhere.
# Plugins don't have to be aware of the different between parent/child admins.
PageAdmin = PageChildAdmin
