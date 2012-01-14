from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from fluent_pages.utils.polymorphicadmin import PolymorphicBaseModelAdmin, PolymorphicModelChoiceAdminForm
from fluent_pages.models import UrlNode
from mptt.admin import MPTTModelAdmin


class PageTypeChoiceAdminForm(PolymorphicModelChoiceAdminForm):
    def __init__(self, *args, **kwargs):
        super(PageTypeChoiceAdminForm, self).__init__(*args, **kwargs)
        self.fields['ct_id'].label = _("Page type")


class UrlNodePolymorphicAdmin(PolymorphicBaseModelAdmin, MPTTModelAdmin):
    """
    The main entry to the admin interface of django-fluent-pages.
    """
    base_model = UrlNode
    add_type_form = PageTypeChoiceAdminForm


    def get_admin_for_model(self, model):
        from fluent_pages.extensions import page_type_pool
        return page_type_pool.get_model_admin(model)


    def get_polymorphic_model_classes(self):
        from fluent_pages.extensions import page_type_pool
        return page_type_pool.get_model_classes()


    def get_polymorphic_type_choices(self):
        """
        Return a list of polymorphic types which can be added.
        """
        from fluent_pages.extensions import page_type_pool

        choices = []
        for plugin in page_type_pool.get_plugins():
            ct = ContentType.objects.get_for_model(plugin.model)
            choices.append((ct.id, plugin.verbose_name))
        return choices
