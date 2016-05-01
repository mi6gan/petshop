from oscar.apps.catalogue.abstract_models import AbstractProduct

from easy_thumbnails.alias import aliases
from easy_thumbnails.templatetags.thumbnail import thumbnail_url

from django.db.models import Q


class Product(AbstractProduct):

    def thumb(self, image, alias_name):
        if image:
            thumb=thumbnail_url(image.original, alias_name)
        else:
            alias = aliases.get(alias_name)
            thumb = ('http://placehold.it/%sx%s' % 
                            (alias.get('size', (32,32))))
        return thumb

    def primary_thumb(self, alias_name):
        if self.images.exists():
            return self.thumb(self.primary_image(), alias_name)

    def tiny_thumb(self):
        return self.primary_thumb('product_tiny')

    def small_thumb(self):
        return self.primary_thumb('product_small')

    def medium_thumb(self):
        return self.primary_thumb('product_medium')

    def large_thumb(self):
        return self.primary_thumb('product_large')

    def thumbs(self, alias_name):
        for image in ProductImage.objects.filter(
                Q(product=self)|Q(product__parent=self)).distinct():
            yield self.thumb(image, alias_name)

    def tiny_thumbs(self):
        return self.thumbs('product_tiny')

    def small_thumbs(self):
        return self.thumbs('product_small')

    def medium_thumbs(self):
        return self.thumbs('product_medium')

    def large_thumbs(self):
        return self.thumbs('product_large')


from oscar.apps.catalogue.models import *  # noqa
