from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('',
    url(r'', include('fluent_pages.urls')),
    url(r'^404/$', 'django.views.defaults.page_not_found'),
)