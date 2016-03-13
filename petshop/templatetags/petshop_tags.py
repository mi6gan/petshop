from django.forms.widgets import Media
from django import template

from sekizai.helpers import get_varname

register = template.Library()

@register.assignment_tag
def get_base_media():
    media = (
        Media(
            js=(
                'vendor/js/jquery.min.js',
                'vendor/js/move-top.js',
                'vendor/js/easing.js',
                'vendor/js/startstop-slider.js',
            ),
            css={
                'all': ('css/base.css', 'vendor/css/bootstrap.css')
            }
        )
    )
    return media

@register.simple_tag(takes_context=True)
def extend_media_block(context, media_type, media, block_name=None):
    if not block_name:
        block_name = media_type
    sekizai_varname = get_varname()
    rendered_content = getattr(media, 'render_%s' % media_type)()
    rendered_content = u'\n'.join([c.strip() for c in rendered_content])
    context[sekizai_varname][block_name].append(rendered_content)
    return ''
