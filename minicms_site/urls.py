from django.conf.urls.defaults import *
from django.conf import settings

# All the default stuff
urlpatterns = patterns('',
#    (r'^', include('ecms.urls'))
    )

handler500 = 'ecms.views.errors.my_500'


# Extra features for debugging mode
# Serve media in case Apache is not configured to do it
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )

# Enable admin panel if requested
if settings.ENABLE_ADMIN:
    from django.contrib import admin
    admin.autodiscover()

    urlpatterns += patterns('',
        (r'^admin/doc/', include('django.contrib.admindocs.urls')),
        (r'^admin/', include(admin.site.urls)),
    )


