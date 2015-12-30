from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^admin/utils/tinymce/', include('tinymce.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'', include('fluent_pages.urls')),
]
