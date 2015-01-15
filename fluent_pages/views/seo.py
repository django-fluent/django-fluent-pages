from django.views.generic import TemplateView
from fluent_pages import appsettings


class RobotsTxtView(TemplateView):
    """
    Exposing a ``robots.txt`` template in the Django project.

    Add this view to the ``urls.py``:

    .. code-block:: python

        from fluent_pages.views import RobotsTxtView

        urlpatterns = [
            # ...

            url(r'^robots.txt$', RobotsTxtView.as_view()),
        ]

    Naturally, this pattern should not be included
    inside :func:`~django.conf.urls.i18n.i18n_patterns` as it should appear at the top level.

    A ``robots.txt`` template is included by default, which you have override in your own project.
    """
    #: The content_type to return.
    content_type = 'text/plain'
    #: The template to render.  You can override this template.
    template_name = 'robots.txt'

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['content_type'] = self.content_type  # standard TemplateView does not offer this!
        context['ROOT_URL'] = self.request.build_absolute_uri('/')
        context['ROBOTS_TXT_DISALLOW_ALL'] = appsettings.ROBOTS_TXT_DISALLOW_ALL
        return super(RobotsTxtView, self).render_to_response(context, **response_kwargs)
