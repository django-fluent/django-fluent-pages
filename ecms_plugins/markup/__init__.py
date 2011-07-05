VERSION = (0, 1, 0)
from . import appsettings

# Do some version checking
try:
    if appsettings.ECMS_MARKUP_LANGUAGE == 'restructuredtext':
        import docutils
    elif appsettings.ECMS_MARKUP_LANGUAGE == 'markdown':
        import markdown
    elif appsettings.ECMS_MARKUP_LANGUAGE == 'textile':
        import textile
except ImportError, e:
    raise ImportError("The 'markup' package cannot be used: " + e)
