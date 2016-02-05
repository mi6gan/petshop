from oscar.apps.catalogue.abstract_models import AbstractProduct

from easy_thumbnails.alias import aliases
from easy_thumbnails.templatetags.thumbnail import thumbnail_url


class Product(AbstractProduct):

    def thumb(self, alias_name):
        if self.images.exists():
            image = self.primary_image()
            thumb=thumbnail_url(image.original, alias_name)
        else:
            alias = aliases.get(alias_name)
            thumb = ('http://placehold.it/%sx%s' % 
                            (alias.get('size', (32,32))))
        return thumb

    def tiny_thumb(self):
        return self.thumb('product_tiny')

    def small_thumb(self):
        return self.thumb('product_small')

    def medium_thumb(self):
        return self.thumb('product_medium')

    def large_thumb(self):
        return self.thumb('product_large')


from oscar.apps.catalogue.models import *  # noqa
