from django.forms.widgets import Select


class LayoutSelector(Select):

    def render(self, name, value, attrs=None, choices=()):  # Django 1.10: choices is no longer used.
        attrs['data-original-value'] = value
        return super(LayoutSelector, self).render(name, value, attrs)
