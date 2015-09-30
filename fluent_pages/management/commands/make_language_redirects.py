from optparse import make_option
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError, NoArgsCommand
from django.utils import translation
from django.utils.translation import get_language_info
import sys
from fluent_pages.models import UrlNode
from parler.utils.context import switch_language


class Command(NoArgsCommand):
    """
    Add a prefix to the name of content items.
    This makes content items easier to spot in the permissions list.
    """
    help = "Find all pages of a given language, and redirect to the canonical version."
    args = "language"
    option_list = BaseCommand.option_list + (
        make_option('--format', default='nginx', help='Choose the output format, defaults to "nginx"'),
        make_option('--site', default=int(settings.SITE_ID), help="Choose the site ID to "),
        make_option('--from'),
        make_option('--host'),
        make_option('--to', default=settings.LANGUAGE_CODE),
    )

    def handle(self, *args, **options):
        site = options['site']
        host = options['host']
        from_lang = options['from']
        to_lang = options['to']

        if not from_lang:
            raise CommandError("Provide a --from=.. language to redirect for")
        if not host:
            host = Site.objects.get_current().domain

        if '://' not in host:
            host = "http://{0}".format(host)

        from_name = get_language_info(from_lang)['name']
        to_name = get_language_info(to_lang)['name']

        with translation.override(from_lang):
            qs = (UrlNode.objects
                  .parent_site(site)
                  .non_polymorphic()
                  .translated(to_lang)
                  .order_by('translations___cached_url'))
            if not qs:
                raise CommandError("No URLs found for site {0} in {1}".format(site, from_name))

            self.stdout.write('# Redirecting all translated {0} URLs to the {1} site\n'.format(from_name, to_name))
            self.stdout.write("# Generated using {0}".format(" ".join(sys.argv)))

            for page in qs:
                from_url = page.default_url
                with switch_language(page, to_lang):
                    to_url = page.get_absolute_url()

                if from_url == to_url:
                    continue

                if from_url.endswith('/'):
                    from_regexp = from_url.rstrip('/')
                    from_rule = "~ ^{0}(/|$)".format(from_regexp)
                else:
                    from_regexp = from_url
                    from_rule = "= {0}".format(from_regexp)

                if page.plugin.urls:
                    self.stdout.write("location {0} {{ rewrite ^{1}(.*)$  {2}{3}$1; }}\n".format(
                        from_rule, from_regexp, host, to_url.rstrip('/')
                    ))
                else:
                    self.stdout.write("location {0} {{ return 301 {1}{2}; }}\n".format(
                        from_rule, host, to_url
                    ))

            # Final redirect for all identical URLs
            self.stdout.write("\n# Redirect all remaining and identical URls:\n")
            self.stdout.write("location / {{ rewrite ^/(.*)$  {0}/$1 permanent; }}\n".format(host))
