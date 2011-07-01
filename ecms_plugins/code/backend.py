"""
Using pygments to render the code.
"""
from pygments import highlight, styles
from pygments.lexers import get_all_lexers, get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.styles import get_all_styles

STYLE_CHOICES = map(lambda x: (x,x), get_all_styles())
STYLE_CHOICES.sort(lambda x,y: cmp(x[1].lower(), y[1].lower()))

LANGUAGE_CHOICES = map(lambda x: (x[1][0], x[0]), get_all_lexers())
LANGUAGE_CHOICES.sort(lambda x,y: cmp(x[1].lower(), y[1].lower()))


def render_code(instance):
    style = styles.get_style_by_name(instance.style)
    formatter = HtmlFormatter(linenos=instance.linenumbers, style=style)
    html = highlight(instance.code, get_lexer_by_name(instance.language), formatter)
    css = formatter.get_style_defs()

    # Included in a DIV, so the next item will be displayed below.
    return '<div><style type="text/css">' + css + '</style>\n' + html + "</div>"
