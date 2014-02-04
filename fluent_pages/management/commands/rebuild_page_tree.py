from django.core.management.base import NoArgsCommand
from django.utils.encoding import smart_text
from fluent_pages.models.db import UrlNode_Translation, UrlNode


class Command(NoArgsCommand):
    """
    Update the tree, rebuild the translated URL nodes.
    """
    help = "Update the cached_url for the translated URL node tree"

    def handle_noargs(self, **options):
        slugs = {}
        overrides = {}
        parents = dict(UrlNode.objects.values_list('id', 'parent_id'))

        for translation in UrlNode_Translation.objects.order_by('master__lft', 'master__tree_id'):
            slugs.setdefault(translation.language_code, {})[translation.master_id] = translation.slug
            overrides.setdefault(translation.language_code, {})[translation.master_id] = translation.override_url

            translation._cached_url = self._construct_url(translation.language_code, translation.master_id, parents, slugs, overrides)
            translation.save()
            self.stdout.write(smart_text(u"- {0}\t {1} {2}\n".format(translation.master_id, translation.language_code, translation._cached_url)))


    def _construct_url(self, language_code, child_id, parents, slugs, overrides):
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
            url_parts.append(slugs[language_code][id])

        return (u'/'.join(url_parts) + u'/').replace('//', '/')
