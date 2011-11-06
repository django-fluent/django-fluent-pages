"""
Comments area plugin.

This plugin package is not called "comments" as that conflicts
with the `django.contrib.comments` appname. Hence, "commentsarea" it is.

The plugin displays the form and messagelist that ``django.contrib.comments`` renders.
Hence, it depends on a properly configured contrib module.
The least you need to do, is:

  * providing a ``comments/base.html`` template.
   * include a ``title`` block that is displayed in the ``<head>`` of the base template.
   * include a ``content`` block that is displayed in the ``<body>`` of the base template.
  * provide a ``comments/posted.html`` template for the success page.
   * It could contains links to the blog page.
   * It could redirect automatically back to the blog in a few seconds.
"""
from __future__ import absolute_import
from ecms.extensions import EcmsPlugin, plugin_pool
from ecms_plugins.commentsarea.models import CmsCommentsAreaItem
from ecms_plugins.commentsarea import appsettings


class EcmsCommentsAreaPlugin(EcmsPlugin):
    model = CmsCommentsAreaItem
    category = 'interactivity'
    admin_form_template = "admin/ecms_plugins/commentsarea/admin_form.html"
    render_template = "ecms_plugins/commentsarea/commentsarea.html"


plugin_pool.register(EcmsCommentsAreaPlugin)
