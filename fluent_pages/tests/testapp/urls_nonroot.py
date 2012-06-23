from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('',
    url(r'^pages/', include('fluent_pages.urls')),
)