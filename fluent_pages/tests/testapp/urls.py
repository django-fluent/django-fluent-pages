import fluent_pages.admin  # Register model
from django.conf.urls import url, include
from django.contrib import admin
from django.http import Http404


def simulate_404(request):
    raise Http404("Test")


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^404/$', simulate_404),
    url(r'', include('fluent_pages.urls')),
]
