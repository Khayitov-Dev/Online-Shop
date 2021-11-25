from decimal import Decimal
from django.conf import settings
from shop.models import Product
from coupons.models import Coupon


class Cart(object):
    @property
    def coupon(self):
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass
        return None

    def get_discount(self):
        if self.coupon:
            return (self.coupon.discount / Decimal(100)) \
                * self.get_total_price()
        return Decimal(0)
    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()
    def __init__(self, request):
        """
        Cartni ishga tushiring.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # seansda bo'sh savatni saqlang
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        # joriy qo'llaniladigan kuponni saqlang
        self.coupon_id = self.session.get('coupon_id')


    
    def add(self, product, quantity=1, override_quantity=False):
        """
        Savatga mahsulot qo'shing yoki uning miqdorini yangilang.
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,'price': str(product.price)}
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()
    def save(self):
        # saqlanganligiga ishonch hosil qilish uchun sessiyani "o'zgartirilgan" deb belgilang
        self.session.modified = True

    
    def remove(self, product):
        """
        Savatdan mahsulotni olib tashlang.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products
        from the database.
        """
        product_ids = self.cart.keys()
        # mahsulot ob'ektlarini oling va ularni savatga qo'shing
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item
    


    def __len__(self):
        """
        Savatdagi barcha narsalarni hisoblang.
        """
        return sum(item['quantity'] for item in self.cart.values())


    

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())


    

    def clear(self):
        # savatni sessiyadan olib tashlash
        del self.session[settings.CART_SESSION_ID]
        self.save()
    
