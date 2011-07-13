VERSION = (0, 1, 0)
from . import appsettings

dependencies = {
    'restructuredtext': 'docutils',
    'markdown': 'markdown',
    'textile': 'textile',
}


# Do some version checking
try:
    lang = appsettings.ECMS_MARKUP_LANGUAGE
    module = dependencies.get(lang)
    if module:
        __import__(module)
except ImportError, e:
    raise ImportError("The '%s' package is required to use the '%s' language for the 'markup' plugin." % (module, lang))
