from fluent_pages.utils.compat import patterns, url, include
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^pages/', include('fluent_pages.urls')),
)