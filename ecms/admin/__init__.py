from django.contrib import admin
from ecms.models import CmsSite, CmsObject, CmsTextItem
from ecms.admin.cmsobject import CmsObjectAdmin


# -------- Model registration --------

# Register the models with the admin site
admin.site.register(CmsSite)
admin.site.register(CmsObject, admin_class=CmsObjectAdmin)