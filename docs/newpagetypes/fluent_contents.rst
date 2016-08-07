.. _newplugins-fluent-contents:

Integration with fluent-contents
================================

The bundled :ref:`fluent page type <fluentpage>` provides a page type
where parts of the page can be filled with flexible content blocks.
This feature can be used in your custom page types as well.
The :mod:`fluent_pages.integration.fluent_contents` package provides
all classes to make this integration painless.

.. note::

    The support for those flexible blocks is provided by
    the stand-alone django-fluent-contents_ package, which is an optional dependency.
    Both *fluent-pages* and *fluent-contents* are stand-alone packages,
    which you can mix and match freely with other software.

Example case: donation page
---------------------------

In some pages, the user is guided through several steps.
At each step, staff members have to be able to enter CMS page content.

This can be handled in a smart way by exposing all situations through a single page.

In this simple example, a "Donation Page" was created as custom page type.
This allowed editing the opening view, and "thank you view" as 2 separate area's.

``models.py``
~~~~~~~~~~~~~

.. code-block:: python

    from fluent_pages.integration.fluent_contents.models import FluentContentsPage

    class DonationPage(FluentContentsPage):
        """
        It has a fixed template, which can be used to enter the contents for all wizard steps.
        """
        class Meta:
            verbose_name = _("Donation Page")
            verbose_name_plural = _("Donation Pages")


``admin.py``
~~~~~~~~~~~~

.. code-block:: python

    from fluent_pages.integration.fluent_contents.admin import FluentContentsPageAdmin

    class DonationPageAdmin(FluentContentsPageAdmin):
        """
        Admin for "Donation Page" in the CMS.
        """
        # This template is read to fetch the placeholder data, which displays the tabs.
        placeholder_layout_template = 'pages/donation.html'


``page_type_plugins.py``
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from django.conf.urls import url
    from fluent_pages.extensions import page_type_pool
    from fluent_pages.integration.fluent_contents.page_type_plugins import FluentContentsPagePlugin
    from .admin import DonationPageAdmin
    from .models import DonationPage
    from .views import DonationSuccessView


    @page_type_pool.register
    class DonationPagePlugin(FluentContentsPagePlugin):
        """
        Custom page type for the donation page

        This page type can be inserted somewhere within the page tree,
        and all it's wizard sub-pages will be read from it.
        """
        model_admin = DonationPageAdmin
        model = DonationPage

        urls = [
            # root = donation starting page (handled as standard page)
            url(r'^step1/', DonationStep1View.as_view(), name='donation-step1'),
            url(r'^step2/', DonationStep2View.as_view(), name='donation-step2'),
            url(r'^thank-you/', DonationSuccessView.as_view(), name='donation-success'),
        ]

``views.py``
~~~~~~~~~~~~

.. code-block:: python

    from django.views.generic import TemplateView
    from fluent_pages.views import CurrentPageTemplateMixin


    class DonationViewBase(CurrentPageTemplateMixin):
        # There is no need to redeclare the template here,
        # it's auto selected from the plugin/admin by CurrentPageTemplateMixin.
        #template_name = 'pages/donation.html'
        render_tab = ''

        def get_context_data(self, **kwargs):
            context = super(DonationViewBase, self).get_context_data(**kwargs)
            context['render_tab'] = self.render_tab
            return context

    class DonationStep1(DonationViewBase, FormView):
        """
        Success page
        """
        view_url_name = 'donation-step1'   # for django-parler's {% get_translated_url %}
        render_tab = 'step1'               # for the template
        template_name = ""

        # ...

    class DonationSuccessView(DonationViewBase, TemplateView):
        """
        Success page
        """
        view_url_name = 'donation-success'
        render_tab = 'success'
        template_name = ""

``templates/pages/donation.html``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: html+django

    {% extends "pages/base.html" %}{% load fluent_contents_tags %}
    {% comment %}
      This template implements a sort-of "wizard" like view.
      By exposing all variations in the placeholders,
      the CMS view will display tabs for each option.
    {% endcomment %}

    {% block main %}
        <div class="constrained-subtle">
            <div class="container">

                {% if not render_tab %}
                  {% page_placeholder "donation-intro" title="Donation intro" role="m" fallback=True %}
                {% elif render_tab == 'step1' %}
                  {% page_placeholder "donation-step1" title="Step 1" role="s" fallback=True %}
                {% elif render_tab == 'success' %}
                  {% page_placeholder "donation-success" title="Success page" role="s" fallback=True %}
                {% endif %}

              </div>
            </div>
        </div>
    {% endblock %}


This template leverages the features of django-fluent-contents_.
Each step can now be filled in by an staff member with CMS content.
Even the form can now be added as a "Content plugin".
By using :ref:`fluentcontents:FLUENT_CONTENTS_PLACEHOLDER_CONFIG`,
the allowed plugin types can be limited per step. For example:

.. code-block:: python

    FLUENT_CONTENTS_PLACEHOLDER_CONFIG = {
        # ...

        # The 'pages/donation.html' template:
        'donation-intro': {
            'plugins': (
                'DonateButtonPlugin', 'TextPlugin',
            ),
        },
        'donation-step1': {
            'plugins': (
                'DonationForm1Plugin', 'TextPlugin',
            ),
        },
        'giveone-success': {
            'plugins': (
                'ThankYouPlugin',
                'TextPlugin',
                'RawHtmlPlugin',  # For social media embed codes
            ),
        },
    })


.. _django-fluent-contents: https://github.com/django-fluent/django-fluent-contents
