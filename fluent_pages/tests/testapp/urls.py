import fluent_pages.admin  # Register model
from fluent_pages.utils.compat import patterns, url, include
from django.contrib import admin
from django.http import HttpResponse

def login(request):
    return HttpResponse("login")

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/', login),
    url(r'^404/$', 'django.views.defaults.page_not_found'),
    url(r'', include('fluent_pages.urls')),
)