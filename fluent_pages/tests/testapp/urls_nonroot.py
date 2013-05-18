from fluent_pages.utils.compat import patterns, url, include

urlpatterns = patterns('',
    url(r'^pages/', include('fluent_pages.urls')),
)