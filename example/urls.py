import tinymce.urls
from django.contrib import admin
from django.urls import include, path

import fluent_pages.urls

urlpatterns = [
    path("admin/utils/tinymce/", include(tinymce.urls)),
    path("admin/", admin.site.urls),
    path("", include(fluent_pages.urls)),
]
