from csv import DictReader
from io import TextIOWrapper

from shopapp.models import Product, Order


def save_csv_products(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = DictReader(csv_file)
    products = [
        Product(**row)
        for row in reader
    ]
    Product.objects.bulk_create(products)
    return products

def save_csv_orders(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = DictReader(csv_file)
    for row in reader:
        order = Order(
            delivery_address=row['delivery_address'],
            promocode=row['promocode'],
            created_at=row['created_at'],
            user_id=int(row['user_id']),
        )
        order.save()

        product_ids = [int(id) for id in row['products'].split(',')]
        products = Product.objects.filter(pk__in=product_ids)
        order.products.set(products)