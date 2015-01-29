# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from fluent_pages import appsettings


class Migration(DataMigration):

    def forwards(self, orm):
        UrlNode_Translation = orm['fluent_pages.UrlNode_Translation']
        RedirectNodeTranslation = orm['redirectnode.RedirectNodeTranslation']
        default_choices = ('en', 'en-us', appsettings.FLUENT_PAGES_DEFAULT_LANGUAGE_CODE)

        for redirectnode in orm['redirectnode.RedirectNode'].objects.all():
            available_languages = list(UrlNode_Translation.objects.filter(master_id=redirectnode.id).values_list('language_code', flat=True))

            # Find the first language that is usable.
            # Move the fields to the translation of that language.
            lang = next((code for code in default_choices if code in available_languages), available_languages[0])
            RedirectNodeTranslation.objects.create(
                master_id=redirectnode.pk,
                language_code=lang,
                new_url=redirectnode.new_url,
                redirect_type=redirectnode.redirect_type
            )

    def backwards(self, orm):
        RedirectNodeTranslation = orm['redirectnode.RedirectNodeTranslation']
        # Convert all fields back to the single-language table.
        for redirectnode in orm['redirectnode.RedirectNode'].objects.all():
            translations = RedirectNodeTranslation.objects.filter(master_id=redirectnode.id)
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

            redirectnode.new_url = translation.new_url
            redirectnode.redirect_type = translation.redirect_type
            redirectnode.save()   # As intended: doesn't call UrlNode.save() but Model.save() only.

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
        'fluent_pages.page': {
            'Meta': {'ordering': "('tree_id', 'lft')", 'object_name': 'Page', 'db_table': "u'fluent_pages_urlnode'", '_ormbases': ['fluent_pages.UrlNode'], 'proxy': 'True'}
        },
        'fluent_pages.urlnode': {
            'Meta': {'ordering': "('tree_id', 'lft')", 'unique_together': "(('parent_site', 'key'),)", 'object_name': 'UrlNode'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_navigation': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'in_sitemaps': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'key': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'parent': ('fluent_pages.models.fields.PageTreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['fluent_pages.UrlNode']"}),
            'parent_site': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['sites.Site']"}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polymorphic_fluent_pages.urlnode_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
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
        u'redirectnode.redirectnode': {
            'Meta': {'ordering': "('tree_id', 'lft')", 'object_name': 'RedirectNode', 'db_table': "'pagetype_redirectnode_redirectnode'", '_ormbases': ['fluent_pages.Page']},
            'new_url': ('django.db.models.fields.URLField', [], {'max_length': '255'}),
            'redirect_type': ('django.db.models.fields.IntegerField', [], {'default': '302'}),
            u'urlnode_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['fluent_pages.UrlNode']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'redirectnode.redirectnodetranslation': {
            'Meta': {'unique_together': "[(u'language_code', u'master')]", 'object_name': 'RedirectNodeTranslation', 'db_table': "u'redirectnode_redirectnode_translation'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            u'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'redirect_translations'", 'null': 'True', 'to': u"orm['redirectnode.RedirectNode']"}),
            'new_url': ('django.db.models.fields.URLField', [], {'max_length': '255'}),
            'redirect_type': ('django.db.models.fields.IntegerField', [], {'default': '302'})
        },
        u'sites.site': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'Site', 'db_table': "u'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['redirectnode']
    symmetrical = True
