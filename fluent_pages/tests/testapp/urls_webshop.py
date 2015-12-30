from django.conf.urls import url
from django.http import HttpResponse


def webshop_index(request):
    return HttpResponse("test_webshop: index_page")


def webshop_article(request, slug):
    return HttpResponse("test_webshop: article: " + slug)


urlpatterns = [
    url(r'^$', webshop_index, name='webshop_index'),
    url(r'^(?P<slug>[^/]+)/$', webshop_article, name='webshop_article'),
]
