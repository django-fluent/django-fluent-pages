"""
The URLs to serve the CMS.

They can be included using:

    urlpatterns += [
        url(r'', include('fluent_pages.urls'))
    ]

The following named URLs are defined:
  - fluent-page-admin-redirect   - An redirect to the admin.
  - fluent-page                  - Display of a page.

By Appending @admin to an URL, the request will be redirected to the admin URL of the page.
"""
from fluent_pages.views import CmsPageDispatcher, CmsPageAdminRedirect
from django.conf.urls import url


# This urlpatterns acts as a catch-all, as there is no terminating slash in the pattern.
# This allows the pages to have any name, including file names such as /robots.txt
# Sadly, that circumvents the CommonMiddleware check whether a slash needs to be appended to a path.
# The APPEND_SLASH behavior is implemented in the CmsPageDispatcher so the standard behavior still works as expected.
urlpatterns = [
    url(r'^(?P<path>.*)@admin$', CmsPageAdminRedirect.as_view(), name='fluent-page-admin-redirect'),
    url(r'^(?P<path>.*)$', CmsPageDispatcher.as_view(), name='fluent-page-url'),
    url(r'^$', CmsPageDispatcher.as_view(), name='fluent-page'),
]
