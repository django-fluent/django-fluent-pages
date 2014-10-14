import warnings
from fluent_pages.adminui.utils import get_page_admin_url, get_current_edited_page

warnings.warn(
    "Please use `fluent_pages.adminui.utils` instead, the `fluent_pages.admin.utils` module is deprecated for Django 1.7 compatibility.",
    DeprecationWarning
)
