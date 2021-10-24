from django.contrib import admin
from django.http import Http404
from django.urls import include, path

import fluent_pages.admin  # Register model
import fluent_pages.urls


def simulate_404(request):
    raise Http404("Test")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("404/", simulate_404),
    path("", include(fluent_pages.urls)),
]
