from django.core.management import BaseCommand

from shopapp.models import Order

from shopapp.models import Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        order = Order.objects.first()
        if not order:
            self.stdout.write('no order found')
            return
        products = Product.objects.all()

        for product in products:
            order.products.add(product)

        order.save()
        self.stdout.write(f'Successfully added products {order.products.all()} '
                          f'to order {order}')
