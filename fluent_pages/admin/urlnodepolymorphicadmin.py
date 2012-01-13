from django import forms
from django.conf.urls.defaults import patterns, url
from django.contrib.admin.helpers import AdminForm, AdminErrorList
from django.contrib.admin.widgets import AdminRadioSelect
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import RegexURLResolver
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from fluent_pages.admin.urlnodeadmin import UrlNodeAdmin
from fluent_pages.models import UrlNode
import re


class PageTypeChoiceAdminForm(forms.Form):
    ct_id = forms.ChoiceField(label=_("Page type"), widget=AdminRadioSelect(attrs={'class': 'radiolist'}))


def _dummy_change_view(request, id):
    raise Http404("Dummy page for polymorphic classes")


class UrlNodePolymorphicAdmin(UrlNodeAdmin):
    """
    The polymorphic features of the UrlNode admin.
    """
    base_model = UrlNode
    add_type_template = None


    def _get_real_admin(self, object_id):
        obj = self.model.objects.non_polymorphic().values('polymorphic_ctype').get(pk=object_id)
        return self._get_real_admin_by_ct(obj['polymorphic_ctype'])


    def _get_real_admin_by_ct(self, ct_id):
        from fluent_pages.extensions import page_type_pool
        try:
            ct = ContentType.objects.get_for_id(ct_id)
        except ContentType.DoesNotExist as e:
            raise Http404(e)   # Handle invalid GET parameters

        model_class = ct.model_class()
        if not model_class:
            raise Http404("No model found for '{0}.{1}'.".format(*ct.natural_key()))  # Handle model deletion

        # The views are already checked for permissions, so ensure the model is a derived object.
        # Otherwise, it would open all admin views to users who can edit the base object.
        if not issubclass(model_class, self.base_model):
            raise PermissionDenied("Invalid model '{0}.{1}', must derive from UrlNode.".format(*ct.natural_key()))

        return page_type_pool.get_model_admin(model_class)


    def get_polymorphic_type_choices(self, request):
        """
        Return a list of polymorphic types which can be added.
        """
        from fluent_pages.extensions import page_type_pool

        choices = []
        for plugin in page_type_pool.get_plugins():
            ct = ContentType.objects.get_for_model(plugin.model)
            choices.append((ct.id, plugin.verbose_name))
        return choices


    def add_view(self, request, form_url='', extra_context=None):
        """Redirect the add view to the real admin."""
        ct_id = int(request.GET.get('ct_id', 0))
        if not ct_id:
            # Display choices
            return self.add_type_view(request)
        else:
            real_admin = self._get_real_admin_by_ct(ct_id)
            return real_admin.add_view(request, form_url, extra_context)


    def change_view(self, request, object_id, extra_context=None):
        """Redirect the change view to the real admin."""
        real_admin = self._get_real_admin(object_id)
        return real_admin.change_view(request, object_id, extra_context)


    def delete_view(self, request, object_id, extra_context=None):
        """Redirect the delete view to the real admin."""
        real_admin = self._get_real_admin(object_id)
        return real_admin.delete_view(request, object_id, extra_context)


    def get_urls(self):
        """Support forwarding URLs."""
        urls = super(UrlNodePolymorphicAdmin, self).get_urls()

        # Patch the change URL is not a big catch-all,
        # so all custom URLs can be added to the end.
        change_url = [u for u in urls if u.name.endswith('_change')][0]
        change_url.regex = re.compile(r'^(\d+)/$', re.UNICODE)

        # Define the catch-all for custom views
        custom_urls = patterns('',
            url(r'^(?P<path>.+)$', self.admin_site.admin_view(self.custom_view))
        )

        # Add reverse names for all polymorphic models, so the delete button works.
        from fluent_pages.extensions import page_type_pool
        dummy_urls = []
        for model in page_type_pool.get_model_classes():
            info = model._meta.app_label, model._meta.module_name
            dummy_urls.append(url(r'^(\d+)/$', _dummy_change_view, name='{0}_{1}_change'.format(*info)))

        return urls + custom_urls + dummy_urls


    def custom_view(self, request, path):
        """
        Forward any request to a custom view of the real admin.
        """
        ct_id = int(request.GET.get('ct_id', 0))
        if not ct_id:
            raise Http404("No ct_id parameter, unable to find admin subclass for path '{0}'.".format(path))

        real_admin = self._get_real_admin_by_ct(ct_id)
        resolver = RegexURLResolver('^', real_admin.urls)
        resolvermatch = resolver.resolve(path)
        if not resolvermatch:
            raise Http404("No match for path '{0}' in admin subclass.".format(path))

        return resolvermatch.func(request, *resolvermatch.args, **resolvermatch.kwargs)


    def add_type_view(self, request, form_url=''):
        """
        Display a choice form to select which page type to add.
        """
        choices = self.get_polymorphic_type_choices(request)
        if len(choices) == 1:
            return HttpResponseRedirect('?ct_id={0}'.format(choices[0][0]))

        # Create form
        form = PageTypeChoiceAdminForm(
            data=request.POST if request.method == 'POST' else None,
            initial={'ct_id': choices[0][0]}
        )
        form.fields['ct_id'].choices = choices

        if form.is_valid():
            return HttpResponseRedirect('?ct_id={0}'.format(form.cleaned_data['ct_id']))

        # Wrap in all admin layout
        fieldsets = ((None, {'fields': ('ct_id',)}),)
        adminForm = AdminForm(form, fieldsets, {}, model_admin=self)
        media = self.media + adminForm.media
        opts = self.model._meta

        context = {
            'title': _('Add %s') % force_unicode(opts.verbose_name),
            'adminform': adminForm,
            'is_popup': "_popup" in request.REQUEST,
            'media': mark_safe(media),
            'errors': AdminErrorList(form, ()),
            'app_label': opts.app_label,
        }
        return self.render_add_type_form(request, context)


    def render_add_type_form(self, request, context, form_url=''):
        """
        Render the page type choice form.
        """
        opts = self.model._meta
        app_label = opts.app_label
        context.update({
            'has_change_permission': self.has_change_permission(request),
            'form_url': mark_safe(form_url),
            'opts': opts,
            'root_path': self.admin_site.root_path,
        })
        context_instance = RequestContext(request, current_app=self.admin_site.name)
        return render_to_response(self.change_form_template or [
            "admin/%s/%s/add_type_form.html" % (app_label, opts.object_name.lower()),
            "admin/%s/add_type_form.html" % app_label,
            "admin/add_type_form.html"
        ], context, context_instance=context_instance)
