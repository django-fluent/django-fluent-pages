# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from fluent_pages import appsettings


class Migration(SchemaMigration):

    def forwards(self, orm):
        if db.dry_run:
            return

        UrlNode_Translation = orm['fluent_pages.UrlNode_Translation']
        FluentPageTranslation = orm['fluentpage.FluentPageTranslation']

        for fluentpage in orm['fluentpage.FluentPage'].objects.all():
            available_languages = list(UrlNode_Translation.objects.filter(
                master_id=fluentpage.pk).values_list('language_code', flat=True))

            for lang in available_languages:
                FluentPageTranslation.objects.create(
                    master_id=fluentpage.pk,
                    language_code=lang,
                    layout=fluentpage.layout,
                )

    def backwards(self, orm):
        if db.dry_run:
            return

        FluentPageTranslation = orm['fluentpage.FluentPageTranslation']

        # Convert all fields back to the single-language table.
        for fluentpage in orm['fluentpage.FluentPage'].objects.all():
            translations = FluentPageTranslation.objects.filter(master_id=fluentpage.pk)
            try:
                # Try default translation
                translation = translations.get(language_code=appsettings.FLUENT_PAGES_DEFAULT_LANGUAGE_CODE)
            except ObjectDoesNotExist:
                try:
                    # Try internal fallback
                    translation = translations.get(language_code__in=('en-us', 'en'))
                except ObjectDoesNotExist:
                    # Hope there is a single translation
                    translation = translations.get()

            fluentpage.layout = translation.layout
            fluentpage.save()   # As intended: doesn't call UrlNode.save() but Model.save() only.

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'fluent_pages.pagelayout': {
            'Meta': {'ordering': "('title',)", 'object_name': 'PageLayout'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'template_path': ('fluent_pages.models.fields.TemplateFilePathField', [], {'max_length': '100', 'recursive': 'True', 'match': "'.*\\\\.html$'"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'fluent_pages.urlnode': {
            'Meta': {'ordering': "('tree_id', 'lft')", 'unique_together': "(('parent_site', 'key'),)", 'object_name': 'UrlNode'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_navigation': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'in_sitemaps': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'key': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'parent': ('fluent_pages.models.fields.PageTreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['fluent_pages.UrlNode']"}),
            'parent_site': ('django.db.models.fields.related.ForeignKey', [], {'default': '10', 'to': u"orm['sites.Site']"}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polymorphic_fluent_pages.urlnode_set+'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'publication_date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'publication_end_date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'d'", 'max_length': '1', 'db_index': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'fluent_pages.urlnode_translation': {
            'Meta': {'unique_together': "(('language_code', 'master'),)", 'object_name': 'UrlNode_Translation'},
            '_cached_url': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': "orm['fluent_pages.UrlNode']"}),
            'override_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'fluentpage.fluentpage': {
            'Meta': {'object_name': 'FluentPage', 'db_table': "'pagetype_fluentpage_fluentpage'"},
            'layout': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fluent_pages.PageLayout']", 'null': 'True'}),
            u'urlnode_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['fluent_pages.UrlNode']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'fluentpage.fluentpagetranslation': {
            'Meta': {'object_name': 'FluentPageTranslation'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'layout': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fluent_pages.PageLayout']", 'null': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fluentpage.FluentPage']"})
        },
        u'sites.site': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'Site', 'db_table': "u'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['fluentpage']
