from django.contrib import admin
from ecms.models import CmsSite, CmsObject, CmsLayout, CmsRegion
from ecms.admin.cmsobject import CmsObjectAdmin
from ecms.admin.cmslayout import CmsLayoutAdmin

__all__ = ['CmsObjectAdmin', 'CmsLayoutAdmin', 'CmsRegionAdmin']


# -------- Model registration --------

# Register the models with the admin site
admin.site.register(CmsSite)
admin.site.register(CmsObject, admin_class=CmsObjectAdmin)
admin.site.register(CmsLayout, admin_class=CmsLayoutAdmin)
