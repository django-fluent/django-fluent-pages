from django.forms.widgets import Select


class LayoutSelector(Select):

    def render(self, name, value, attrs=None, choices=()):
        attrs['data-original-value'] = value
        return super(LayoutSelector, self).render(name, value, attrs, choices)
