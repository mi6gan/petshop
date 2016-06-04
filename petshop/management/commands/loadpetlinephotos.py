from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import translation
from django.utils.encoding import force_text, smart_text

from oscar.core.loading import get_model

from petshop.core.utils import load_petline_photos


class Command(BaseCommand):

    STYLES_FOR_VERBOSITY = (
        (),
        ('',),
        ('NOTICE', 'ERROR', 'SUCCESS'),
        ('SUCCESS', 'INFO'), 
    )

    def add_arguments(self, parser):
        parser.add_argument(
                    '--clear', action='store_true',
                    help='clear exist photos')
        parser.add_argument(
                    '--width', type=int, default=1024,
                    help='resize image to width')

    def handle(self, verbosity, *args, **kwargs):
        clear = kwargs.get('clear', False)
        width = kwargs.get('width')
        allowed_styles = ()
        for styles in Command.STYLES_FOR_VERBOSITY[:verbosity+1]:
            allowed_styles += styles
        for message, style_attrname in load_petline_photos(width, clear):
            if style_attrname in allowed_styles:
                wrap_text = getattr(self.style, style_attrname, lambda s: s)
                self.stdout.write(wrap_text(smart_text(message)))
