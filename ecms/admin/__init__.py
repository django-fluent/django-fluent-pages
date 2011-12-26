from django.contrib import admin
from ecms.models import CmsSite, CmsObject, CmsLayout
from ecms.admin.cmsobjectadmin import CmsObjectAdmin
from ecms.admin.cmslayoutadmin import CmsLayoutAdmin

__all__ = ['CmsObjectAdmin', 'CmsLayoutAdmin']


# -------- Model registration --------

# Register the models with the admin site
admin.site.register(CmsSite)
admin.site.register(CmsObject, admin_class=CmsObjectAdmin)
admin.site.register(CmsLayout, admin_class=CmsLayoutAdmin)
