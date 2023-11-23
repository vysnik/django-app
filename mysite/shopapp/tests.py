from string import ascii_letters
from random import choices

from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from shopapp.models import Product, Order
from shopapp.utils import add_two_numbers

# class ProductCreateViewTestCase(TestCase):
#     def setUp(self) -> None:
#         self.product_name = "".join(choices(ascii_letters, k=10))
#         Product.objects.filter(name=self.product_name).delete()
#     def test_product_create_view(self):
#         response = self.client.post(
#             reverse("shopapp:product_create"),
#             {"name": self.product_name, "price": "123.45", "description": "A good table", "discount": "10"},
#         )
#         self.assertRedirects(response, reverse("shopapp:products_list"))
#         self.assertTrue(Product.objects.filter(name=self.product_name).exists())
#
# class ProductsListViewTestCase(TestCase):
#     fixtures = [
#         'products-fixture.json',
#     ]
#     def test_products(self):
#         response = self.client.get(reverse("shopapp:products_list"))
#         # for product in Product.objects.filter(archived=False).all():
#         #     self.assertContains(response, product.name)
#         self.assertQuerySetEqual(
#             qs=Product.objects.filter(archived=False).all(),
#             values=(p.pk for p in response.context["products"]),
#             transform=lambda p: p.pk
#         )
#         self.assertTemplateUsed(response, 'shopapp/products-list.html')
#
# class OrderListViewTestCase(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         cls.user = User.objects.create_user(username="bob_test", password="qwerty")
#     @classmethod
#     def tearDownClass(cls):
#         cls.user.delete()
#     def setUp(self) -> None:
#         self.client.force_login(self.user)
#     def test_orders_view(self):
#         response = self.client.get(reverse('shopapp:orders_list'))
#         self.assertContains(response, "Orders")
#
#     def test_orders_view_not_authenticated(self):
#         self.client.logout()
#         response = self.client.get(reverse('shopapp:orders_list'))
#         self.assertEqual(response.status_code, 302)
#         self.assertIn(str(settings.LOGIN_URL), response.url)

# class ProductsExportViewTestCase(TestCase):
#     fixtures = [
#         'products-fixture.json',
#     ]
#     def test_products_view(self):
#         response = self.client.get(
#             reverse("shopapp:products-export"),
#         )
#         self.assertEqual(response.status_code, 200)
#         products = Product.objects.order_by("pk").all()
#         expected_data = [
#             {
#                 "pk": product.pk,
#                 "name": product.name,
#                 "price": str(product.price),
#                 "archived": product.archived,
#             }
#             for product in products
#         ]
#         products_data = response.json()
#         self.assertEqual(
#             products_data["products"],
#             expected_data,
#         )

class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="user_test", password="qwerty")
        cls.permission_view_order = Permission.objects.get(codename="view_order")
        cls.user.user_permissions.add(cls.permission_view_order)
    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
    def setUp(self) -> None:
        self.client.force_login(self.user)
        self.order = Order.objects.create(
            delivery_address="test address",
            promocode="test promocode",
            user=self.user
        )
    def tearDown(self) -> None:
        self.order.delete()
    def test_order_details(self):
        response = self.client.get(
            reverse("shopapp:order_details", kwargs={"pk": self.order.pk})
            )
        self.assertEqual(response.context['object'].delivery_address, "test address")
        self.assertEqual(response.context['object'].promocode, "test promocode")
        self.assertEqual(response.context['object'].pk, self.order.pk)

class OrdersExportTestCase(TestCase):
    fixtures = [
        'orders-fixture.json',
        'products-fixture.json',
        'users-fixture.json',
    ]
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="user_test", password="qwerty")
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.user.delete()
    def setUp(self) -> None:
        self.client.force_login(self.user)
    def test_orders_view(self):
        response = self.client.get(
            reverse("shopapp:orders_export"),
        )
        self.assertEqual(response.status_code, 200)
        orders = Order.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user_id": order.user.pk,
                "products": [product.pk for product in order.products.all()],
            }
            for order in orders
        ]
        orders_data = response.json()
        self.assertEqual(
            orders_data["orders"],
            expected_data,
        )
        self.assertEqual(response.status_code, 200)