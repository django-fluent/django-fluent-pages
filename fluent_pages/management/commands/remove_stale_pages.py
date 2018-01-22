from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db.models import Model
from fluent_pages.extensions import PageTypeNotFound
from fluent_pages.models import UrlNode


class Command(BaseCommand):
    help = "Remove UrlNodes which are stale, because their model is removed."

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '-p', '--dry-run', action='store_true', dest='dry_run',
            help="Only list what will change, don't make the actual changes."
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        stale_cts = self.get_stale_content_types()
        self.remove_stale_pages(stale_cts)

    def get_stale_content_types(self):
        stale_cts = {}
        for ct in ContentType.objects.all():
            if ct.model_class() is None:
                stale_cts[ct.pk] = ct
        return stale_cts

    def remove_stale_pages(self, stale_cts):
        """
        See if there are items that point to a removed model.
        """
        stale_ct_ids = list(stale_cts.keys())
        pages = (UrlNode.objects
                 .non_polymorphic()  # very important, or polymorphic skips them on fetching derived data
                 .filter(polymorphic_ctype__in=stale_ct_ids)
                 .order_by('polymorphic_ctype', 'pk')
                 )
        if not pages:
            self.stdout.write("No stale pages found.")
            return

        if self.dry_run:
            self.stdout.write("The following pages are stale:")
        else:
            self.stdout.write("The following pages were stale:")

        removed_pages = 0
        for page in pages:
            ct = stale_cts[page.polymorphic_ctype_id]
            self.stdout.write("- #{id} points to removed {app_label}.{model}".format(
                id=page.pk, app_label=ct.app_label, model=ct.model
            ))

            if not self.dry_run:
                try:
                    page.delete()
                    removed_pages += 1
                except PageTypeNotFound:
                    Model.delete(page)

        if removed_pages:
            self.stdout.write("Note, when the removed pages contain content items, "
                              "also call `manage.py remove_stale_contentitems --remove-unreferenced")
