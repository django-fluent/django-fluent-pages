from django.http import HttpResponse
from django.urls import path


def webshop_index(request):
    return HttpResponse("test_webshop: index_page")


def webshop_article(request, slug):
    return HttpResponse("test_webshop: article: " + slug)


urlpatterns = [
    path("", webshop_index, name="webshop_index"),
    path("<str:slug>/", webshop_article, name="webshop_article"),
]
