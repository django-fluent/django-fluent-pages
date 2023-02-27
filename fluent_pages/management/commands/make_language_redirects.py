import sys
from optparse import make_option

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError
from django.utils import translation
from django.utils.translation import get_language_info
from parler.utils.context import switch_language

from fluent_pages.models import UrlNode


class Command(BaseCommand):
    """
    Generate rewrite/redirect rules for the web server to redirect a single unmaintained
    language to another one.
    """

    help = "Find all pages of a given language, and redirect to the canonical version."
    args = "language"

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--format",
            default="nginx",
            help='Choose the output format, defaults to "nginx"',
        ),
        parser.add_argument(
            "--site", default=int(settings.SITE_ID), help="Choose the site ID to "
        ),
        parser.add_argument("--from"),
        parser.add_argument("--host"),
        parser.add_argument("--to", default=settings.LANGUAGE_CODE),

    def handle(self, *args, **options):
        if args:
            raise CommandError("Command doesn't accept any arguments")

        site = options["site"]
        host = options["host"]
        from_lang = options["from"]
        to_lang = options["to"]

        if not from_lang:
            raise CommandError("Provide a --from=.. language to redirect for")
        if not host:
            host = Site.objects.get_current().domain

        if "://" not in host:
            host = f"http://{host}"

        from_name = get_language_info(from_lang)["name"]
        to_name = get_language_info(to_lang)["name"]

        with translation.override(from_lang):
            qs = (
                UrlNode.objects.parent_site(site)
                .non_polymorphic()
                .translated(to_lang)
                .order_by("translations___cached_url")
            )
            if not qs:
                raise CommandError(f"No URLs found for site {site} in {from_name}")

            self.stdout.write(
                f"# Redirecting all translated {from_name} URLs to the {to_name} site\n"
            )
            self.stdout.write("# Generated using {}".format(" ".join(sys.argv)))

            for page in qs:
                from_url = page.default_url
                with switch_language(page, to_lang):
                    to_url = page.get_absolute_url()

                if from_url == to_url:
                    continue

                if from_url.endswith("/"):
                    from_regexp = from_url.rstrip("/")
                    from_rule = f"~ ^{from_regexp}(/|$)"
                else:
                    from_regexp = from_url
                    from_rule = f"= {from_regexp}"

                if page.plugin.urls:
                    self.stdout.write(
                        "location {0} {{ rewrite ^{1}(.*)$  {2}{3}$1; }}\n".format(
                            from_rule, from_regexp, host, to_url.rstrip("/")
                        )
                    )
                else:
                    self.stdout.write(
                        f"location {from_rule} {{ return 301 {host}{to_url}; }}\n"
                    )

            # Final redirect for all identical URLs
            self.stdout.write("\n# Redirect all remaining and identical URls:\n")
            self.stdout.write(f"location / {{ rewrite ^/(.*)$  {host}/$1 permanent; }}\n")
