#!/bin/sh -x

cd `dirname $0`
manage=../manage.py

# Page structure
$manage dumpdata --natural --indent=2 simpleshop.ProductCategory simpleshop.Product > _simpleshop.json
$manage dumpdata --natural --indent=2 fluent_pages > _pages_base.json
$manage dumpdata --natural --indent=2 fluentpage simpleshop.ProductCategoryPage > _pages_models.json

# Page plugins
$manage dumpdata --natural --indent=2 fluent_contents > _page_contents_base.json
#$manage dumpdata --natural --indent=2 sharedcontent > _page_contents_shared.json
$manage dumpdata --natural --indent=2 text oembeditem picture rawhtml > _page_contents_models.json
