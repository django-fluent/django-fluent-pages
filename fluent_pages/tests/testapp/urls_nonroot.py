from django.contrib import admin
from django.urls import include, path

import fluent_pages.urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("pages/", include(fluent_pages.urls)),
]
