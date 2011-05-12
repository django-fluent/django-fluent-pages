"""
The URLs to serve the CMS.

They can be included using:

    urlpatterns += patterns('',
        url(r'', include('ecms.urls'))
    )

The following named URLs are defined:
  - ecms-admin-redirect     - An redirect to the admin.
  - ecms-page               - Display of a page.

By Appending @admin to an URL, the request will be redirected to the admin URL of the page.
"""
from django.conf.urls.defaults import *
from ecms.views.cmspageview import CmsPageView, CmsPageAdminRedirect

# The URLs of the cmspage are forced to end with a slash,
# so django will redirect /admin will redirect to /admin/.
# The same trick also needs to be used in the main site
# which includes this file. Otherwise a rule matched after all.
urlpatterns = patterns('ecms.views',
    url(r'^(?P<path>.*)@admin$', CmsPageAdminRedirect.as_view(), name='ecms-admin-redirect'),
    url(r'^$|^(?P<path>.*/)$', CmsPageView.as_view(), name='ecms-page')
)
