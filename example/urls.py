import fluent_pages.urls
import tinymce.urls
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/utils/tinymce/', include(tinymce.urls)),
    url(r'^admin/', admin.site.urls),

    url(r'', include(fluent_pages.urls)),
]
