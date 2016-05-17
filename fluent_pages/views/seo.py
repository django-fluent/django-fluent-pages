from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import get_language
from django.views.generic import TemplateView
from fluent_pages import appsettings
from parler.utils import is_multilingual_project


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

    Naturally, this pattern should be placed outside :func:`~django.conf.urls.i18n.i18n_patterns`
    as it should appear at the top level.

    A ``robots.txt`` template is included by default, which you have override in your own project.
    Possible templates could look like:

    Simple:

    .. code-block:: html+django

        Sitemap: {{ ROOT_URL }}sitemap.xml
        {% if ROBOTS_TXT_DISALLOW_ALL %}
        User-agent: *
        Disallow: /
        {% endif %}

    Sitemaps per language for usage with :func:`~django.conf.urls.i18n.i18n_patterns`:

    .. code-block:: html+django

        {% for language in language_codes %}Sitemap: {{ ROOT_URL }}{{ language }}/sitemap.xml
        {% endfor %}

    Alternative:

    .. code-block:: html+django

        {% for sitemap_url in sitemap_urls %}Sitemap: {{ sitemap_url }}
        {% endfor %}

    """
    #: The content_type to return.
    content_type = 'text/plain'
    #: The template to render.  You can override this template.
    template_name = 'robots.txt'

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['content_type'] = self.content_type  # standard TemplateView does not offer this!
        return super(RobotsTxtView, self).render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super(RobotsTxtView, self).get_context_data()
        is_multilingual = is_multilingual_project()

        context['ROBOTS_TXT_DISALLOW_ALL'] = appsettings.ROBOTS_TXT_DISALLOW_ALL
        context['ROOT_URL'] = root_url = self.request.build_absolute_uri('/')
        context['is_multilingual_project'] = is_multilingual
        context['language_codes'] = self.get_i18n_patterns_codes()
        context['sitemap_urls'] = self.get_sitemap_urls(root_url)
        return context

    def get_sitemap_urls(self, root_url):
        """
        Return all possible sitemap URLs, which the template can use.
        """
        if self.has_i18n_patterns_urls():
            language_codes = self.get_i18n_patterns_codes()
            return [
                "{0}{1}/sitemap.xml".format(root_url, language_code) for language_code in language_codes
            ]
        else:
            return [
                "{0}sitemap.xml".format(root_url)
            ]

    def has_i18n_patterns_urls(self):
        """
        Check whether something like :func:`~django.conf.urls.i18n.i18n_patterns` is used.
        """
        return '/{0}/'.format(get_language()) in reverse('fluent-page')

    def get_i18n_patterns_codes(self):
        """
        Return the possible values that :func:`~django.conf.urls.i18n.i18n_patterns` support.
        """
        return [code for code, title in settings.LANGUAGES]
