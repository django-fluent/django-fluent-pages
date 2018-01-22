from django.conf.urls import include, url
from django.contrib import admin
import fluent_pages.urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^pages/', include(fluent_pages.urls)),
]
