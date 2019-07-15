from django.conf.urls import include, url
from django.contrib import admin
from django.http import Http404

import fluent_pages.admin  # Register model
import fluent_pages.urls


def simulate_404(request):
    raise Http404("Test")


urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^404/$", simulate_404),
    url(r"", include(fluent_pages.urls)),
]
