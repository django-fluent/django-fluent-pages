# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_pages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, verbose_name=b'Title')),
                ('slug', models.SlugField(verbose_name=b'Slug')),
                ('description', models.TextField(verbose_name=b'Description')),
                ('price', models.DecimalField(verbose_name=b'Price', max_digits=10, decimal_places=2)),
            ],
            options={
                'ordering': ('title',),
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, verbose_name=b'Title')),
                ('slug', models.SlugField(verbose_name=b'Slug')),
            ],
            options={
                'ordering': ('title',),
                'verbose_name': 'Productcategory',
                'verbose_name_plural': 'Productcategories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProductCategoryPage',
            fields=[
                ('urlnode_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_pages.UrlNode')),
                ('product_category', models.ForeignKey(to='simpleshop.ProductCategory')),
            ],
            options={
                'db_table': 'pagetype_simpleshop_productcategorypage',
                'verbose_name': 'Product category page',
                'verbose_name_plural': 'Product category pages',
            },
            bases=('fluent_pages.page',),
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(related_name=b'products', verbose_name=b'Category', to='simpleshop.ProductCategory'),
            preserve_default=True,
        ),
    ]
