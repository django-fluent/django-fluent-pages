from django import forms
from django.core.cache import cache
from fluent_pages.forms.fields import PageChoiceField
from fluent_pages.models.fields import PageTreeForeignKey
from fluent_pages.tests.testapp.models import SimpleTextPage
from fluent_pages.tests.utils import AppTestCase


class ModelDataTests(AppTestCase):
    """
    Tests for URL resolving.
    """

    def setUp(self):
        # Need to make sure that django-parler's cache isn't reused,
        # because the transaction is rolled back on each test method.
        cache.clear()

    @classmethod
    def setUpTree(cls):
        cls.root = SimpleTextPage.objects.create(title="Home", slug="home", status=SimpleTextPage.PUBLISHED, author=cls.user, override_url='/')
        cls.draft1 = SimpleTextPage.objects.create(title="Draft1", slug="draft1", parent=cls.root, status=SimpleTextPage.DRAFT, author=cls.user)

    def test_pagechooserfield_success(self):
        class TestForm(forms.Form):
            page = PageChoiceField()

        form = TestForm(data={
            'page': str(self.root.pk)
        })

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['page'].pk, self.root.pk)

    def test_pagechooserfield_invalid(self):
        class TestForm(forms.Form):
            page = PageChoiceField()

        form = TestForm(data={
            'page': '99999'
        })

        self.assertFalse(form.is_valid())
        self.assertNotIn('not published', str(form.errors['page'][0]))
        self.assertIn('Select a valid choice. That choice is not one of the available choices.', str(form.errors['page'][0]))

    def test_pagechooserfield_draft(self):
        class TestForm(forms.Form):
            page = PageChoiceField()

        form = TestForm(data={
            'page': str(self.draft1.pk)
        })

        self.assertFalse(form.is_valid())
        self.assertIn('not published', str(form.errors['page'][0]))
