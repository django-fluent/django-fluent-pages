from contextlib import contextmanager
from django.conf import settings
from django.core.urlresolvers import get_script_prefix, set_script_prefix

@contextmanager
def script_name(newpath):
    """
    Simulate that the application has a different root folder, expressed by the ``SCRIPT_NAME`` variable.
    This can happen for example, by using ``WSGIScriptAlias /subfolder`` for the Django site.
    It causes ``request.path`` and ``request.path_info`` to differ, making it important to use the right one.
    """
    if newpath[0] != '/' or newpath[-1] != '/':
        raise ValueError("Path needs to have slashes at both ends.")

    newpath_noslash = newpath.rstrip('/')
    oldprefix = get_script_prefix()
    oldname = settings.FORCE_SCRIPT_NAME
    oldmedia = settings.MEDIA_URL
    oldstatic = settings.STATIC_URL

    # Auto adjust MEDIA_URL if it's not set already.
    if settings.MEDIA_URL and settings.MEDIA_URL[0] == '/' and not settings.MEDIA_URL.startswith(newpath):
        settings.MEDIA_URL = newpath_noslash + settings.MEDIA_URL
    if settings.STATIC_URL and settings.STATIC_URL[0] == '/' and not settings.STATIC_URL.startswith(newpath):
        settings.STATIC_URL = newpath_noslash + settings.STATIC_URL

    settings.FORCE_SCRIPT_NAME = newpath
    set_script_prefix(newpath)
    try:
        yield  # call code inside 'with'
    finally:
        settings.FORCE_SCRIPT_NAME = oldname
        settings.STATIC_URL = oldstatic
        settings.MEDIA_URL = oldmedia
        set_script_prefix(oldprefix)
