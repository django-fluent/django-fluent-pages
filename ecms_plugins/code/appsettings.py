"""
Settings for the code plugin.
"""
from django.conf import settings

_defaultShortlist = (
    #'as',
    'as3',
    #'aspx-cs',
    #'aspx-vb',
    'bash',
    'c',
    'cpp',
    'csharp',
    'css',
    'html',
    #'html+php',
    'java',
    'js',
    #'jsp',
    'make',
    'objective-c',
    'perl',
    'php',
    'python',
    'sql',
    'ruby',
    'vb.net',
    'xml',
    'xslt',
)

ECMS_CODE_DEFAULT_LANGUAGE = getattr(settings, "ECMS_CODE_DEFAULT_LANGUAGE", '')
ECMS_CODE_DEFAULT_STYLE = getattr(settings, 'ECMS_CODE_DEFAULT_STYLE', 'default')
ECMS_CODE_DEFAULT_LINE_NUMBERS = getattr(settings, 'ECMS_CODE_DEFAULT_LINE_NUMBERS', False)
ECMS_CODE_SHORTLIST = getattr(settings, 'ECMS_CODE_SHORTLIST', _defaultShortlist)
ECMS_CODE_SHORTLIST_ONLY = getattr(settings, 'ECMS_CODE_SHORTLIST_ONLY', False)
