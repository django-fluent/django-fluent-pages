from django.urls import include, path
from django.contrib import admin

import fluent_pages.urls
import tinymce.urls

urlpatterns = [
    path('admin/utils/tinymce/', include(tinymce.urls)),
    path('admin/', admin.site.urls),
    path('', include(fluent_pages.urls)),
]
