from decimal import Decimal as D

from oscar.apps.partner import availability, prices
from oscar.apps.partner.strategy import Default


class LowestParentPrice(Default):

    def parent_pricing_policy(self, product, children_stock):
        stockrecords = [x[1] for x in children_stock if x[1] is not None]
        if not stockrecords:
            return prices.Unavailable()
        # We take price from first record
        stockrecord = reduce(
                lambda a, b: a 
                if a.price_excl_tax < b.price_excl_tax 
                else b, stockrecords)
        return prices.FixedPrice(
            currency=stockrecord.price_currency,
            excl_tax=stockrecord.price_excl_tax,
            tax=D('0.00'))


class Selector(object):
    """
    Responsible for returning the appropriate strategy class for a given
    user/session.

    This can be called in three ways:

    #) Passing a request and user.  This is for determining
       prices/availability for a normal user browsing the site.

    #) Passing just the user.  This is for offline processes that don't
       have a request instance but do know which user to determine prices for.

    #) Passing nothing.  This is for offline processes that don't
       correspond to a specific user.  Eg, determining a price to store in
       a search index.

    """

    def strategy(self, request=None, user=None, **kwargs):
        """
        Return an instanticated strategy instance
        """
        # Default to the backwards-compatible strategy of picking the first
        # stockrecord but charging zero tax.
        return LowestParentPrice(request)
