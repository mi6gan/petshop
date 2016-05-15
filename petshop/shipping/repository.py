from oscar.apps.shipping import repository
from . import methods
from oscar.apps.checkout.utils import CheckoutSessionData


class Repository(repository.Repository):

    methods = (methods.RussianPost(),)

    def get_shipping_method_by_code(self, code):
        methods = self.methods
        for method in methods:
            if method.code == code:
                return method

    def get_current_shipping_method(self, request):
        code = CheckoutSessionData(request).shipping_method_code(request.basket)
        return self.get_shipping_method_by_code(code)
