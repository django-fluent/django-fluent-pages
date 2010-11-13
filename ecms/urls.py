from django.conf.urls.defaults import *

urlpatterns = patterns('ecms.views',
    url(r'^$|^(.*)$', 'content.cmspage', name='ecms-page')
)
