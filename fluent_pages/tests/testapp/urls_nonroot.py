from django.urls import include, path
from django.contrib import admin

import fluent_pages.urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pages/', include(fluent_pages.urls)),
]
