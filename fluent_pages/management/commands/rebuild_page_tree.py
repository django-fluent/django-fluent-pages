from optparse import make_option

from django.core.management import BaseCommand
from django.core.management import CommandError
from django.utils.encoding import smart_text
from fluent_pages import appsettings
from fluent_pages.extensions import page_type_pool
from fluent_pages.models.db import UrlNode, UrlNode_Translation


class Command(BaseCommand):
    """
    Update the tree, rebuild the translated URL nodes.
    """
    help = "Update the cached_url for the translated URL node tree"

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '-p', '--dry-run', action='store_true', dest='dry-run', default=False,
            help="Only list what will change, don't make the actual changes."
        )
        parser.add_argument(
            '-m', '--mptt-only', action='store_true', dest='mptt-only', default=False,
            help="Only fix the MPTT fields, leave URLs unchanged."
        )

    def handle(self, *args, **options):
        if args:
            raise CommandError("Command doesn't accept any arguments")

        is_dry_run = options.get('dry-run', False)
        mptt_only = options.get('mptt-only', False)
        slugs = {}
        overrides = {}
        parents = dict(UrlNode.objects.values_list('id', 'parent_id'))

        self.stdout.write("Updated MPTT columns")
        if is_dry_run and mptt_only:
            # Can't really do anything
            return

        if not is_dry_run:
            # Fix MPTT first, that is the basis for walking through all nodes.
            UrlNode.objects.rebuild()
            self.stdout.write("Updated MPTT columns")
            if mptt_only:
                return

            self.stdout.write("Updating cached URLs")
            self.stdout.write("Page tree nodes:\n\n")

        type_len = str(max(len(plugin.type_name) for plugin in page_type_pool.get_plugins()))
        col_style = u"| {0:6} | {1:6} | {2:" + type_len + "} | {3:6} | {4}"
        header = col_style.format("Site", "Page", "Type", "Locale", "URL")
        sep = '-' * (len(header) + 40)
        self.stdout.write(sep)
        self.stdout.write(header)
        self.stdout.write(sep)

        # In a single query, walk through all objects in a logical order,
        # which traverses through the tree from parent to children.
        translations = (UrlNode_Translation.objects
                        .select_related('master')
                        .order_by('master__parent_site__id', 'master__tree_id', 'master__lft', 'language_code')
                        )

        for translation in translations:
            slugs.setdefault(translation.language_code, {})[translation.master_id] = translation.slug
            overrides.setdefault(translation.language_code, {})[translation.master_id] = translation.override_url

            page = translation.master
            if page.parent_id:
                if page.parent_id not in slugs[translation.language_code]:
                    self.stderr.write("WARNING: Parent #{0} is not translated in '{1}', while the child #{2} is.".format(
                        page.parent_id, translation.language_code, translation.master_id
                    ))

            old_url = translation._cached_url
            try:
                new_url = self._construct_url(translation.language_code, translation.master_id, parents, slugs, overrides)
            except KeyError:
                if is_dry_run:
                    # When the mptt tree is broken, some URLs can't be correctly generated yet.
                    self.stderr.write("Failed to determine new URL for {0}, please run with --mptt-only first.".format(old_url))
                    return
                raise

            if old_url != new_url:
                translation._cached_url = new_url
                if not is_dry_run:
                    translation.save()

            if old_url != new_url:
                self.stdout.write(smart_text(u"{0}  {1} {2}\n".format(
                    col_style.format(
                        page.parent_site_id, page.pk, page.plugin.type_name,
                        translation.language_code, translation._cached_url
                    ),
                    "WILL CHANGE from" if is_dry_run else "UPDATED from",
                    old_url
                )))
            else:
                self.stdout.write(smart_text(col_style.format(
                    page.parent_site_id, page.pk, page.plugin.type_name,
                    translation.language_code, translation._cached_url
                )))

    def _construct_url(self, language_code, child_id, parents, slugs, overrides):
        active_choices = appsettings.FLUENT_PAGES_LANGUAGES.get_active_choices(language_code)

        breadcrumb = []
        cur = child_id
        while cur is not None:
            breadcrumb.insert(0, cur)
            cur = parents[cur]

        url_parts = ['']
        for id in breadcrumb:
            try:
                # Resets url_parts
                override = overrides[language_code][id]
                if override:
                    url_parts = [override]
                    continue
            except KeyError:
                pass

            # Add first one found, preferably the normal language, fallback otherwise.
            for lang in active_choices:
                try:
                    url_parts.append(slugs[lang][id])
                    break
                except KeyError:
                    continue

        return (u'/'.join(url_parts) + u'/').replace('//', '/')
