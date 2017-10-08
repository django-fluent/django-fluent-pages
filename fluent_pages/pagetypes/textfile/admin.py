from django.contrib import admin

from fluent_pages.adminui import PageAdmin
from .models import TextFile


@admin.register(TextFile)
class TextFileAdmin(PageAdmin):
    pass
