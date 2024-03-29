import logging
from timeit import default_timer

from csv import DictWriter

from django.contrib.auth.models import Group, User
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse, get_list_or_404, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from rest_framework import serializers

from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from drf_spectacular.utils import extend_schema, OpenApiResponse

from .common import save_csv_products
from .models import Product, Order, ProductImage
from .forms import ProductForm, OrderForm, GroupForm
from .serializers import ProductSerializer, OrderSerializer

log = logging.getLogger(__name__)

@extend_schema(description='Product views CRUD')
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product
    Полный CRUD для сущностей товара
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ["name", "description"]
    filterset_fields = [
        "name",
        "description",
        "price",
        "discount",
        "archived",
    ]
    ordering_fields = [
        "name",
        "price",
        "discount",
    ]
    @extend_schema(
        summary='Get one product by ID',
        description='Retrieves **product**, returns 404 if not found',
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description="Empty response, product by id  not found"),
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)
    @method_decorator(cache_page(60))
    def list(self, *args, **kwargs):
        # print("hello products list")
        return super().list(*args, **kwargs)

    @action(methods=['get'], detail=False)
    def download_csv(self, request: Request):

        response = HttpResponse(content_type='text/csv')
        filename = "products-export.csv"
        response['Content-Dispotion'] = f'attachment; filename={filename}'
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "price",
            "discount",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })

        return response
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser])
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES["file"].file,
            encoding=request.encoding,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ["delivery_address", "promocode"]
    filterset_fields = [
        "delivery_address",
        "promocode",
    ]
    ordering_fields = [
        "delivery_address",
        "promocode",
    ]

class ShopIndexView(View):
    # @method_decorator(cache_page(60))
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('laptop', 1999),
            ('desktop', 2999),
            ('smartphone', 999),
        ]
        context = {
            'time_running': default_timer(),
            'products': products,
            'items': 1,
        }
        print("Shop index context", context)
        log.debug("Products for shop index: %s", products)
        log.info("Rendering shop index")
        return render(request, 'shopapp/shop-index.html', context=context)

class GroupListView(View):
    def get(self, request: HttpRequest):
        context = {
            'groups': Group.objects.prefetch_related('permissions').all(),
            'form': GroupForm(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)
    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect(request.path)

class ProductDetailsView(DetailView):
    template_name = 'shopapp/product-details.html'
    # model = Product
    queryset = Product.objects.prefetch_related("images")
    context_object_name = "product"

class ProductsListView(ListView):
    template_name = 'shopapp/products-list.html'
    # model = Product
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)

class ProductCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "shopapp.add_product"
    def form_valid(self, form):
       form.instance.created_by = self.request.user
       response = super().form_valid(form)
       return response

    queryset = (
        Product.objects
        .select_related('created_by_id')
    )
    model = Product
    fields = "created_by", "name", "price", "description", "discount", "preview"

    success_url = reverse_lazy("shopapp:products_list")

class ProductUpdateView(UserPassesTestMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "shopapp.change_product"

    model = Product 
    # fields = "name", "price", "description", "discount", "preview"
    form_class = ProductForm
    template_name_suffix = "_update_form"

    def test_func(self):
        # return self.request.user.groups.filter(name="secret-group").exists()
        if self.request.user.is_superuser or self.get_object().created_by == self.request.user:
            return True

    def get_success_url(self):
        return reverse(
            "shopapp:products_details",
            kwargs={"pk": self.object.pk},
        )
    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )
        return response

class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrderListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects
        .select_related('user')
        .prefetch_related('products')
    )

class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shopapp.view_order"
    queryset = (
        Order.objects
        .select_related('user')
        .prefetch_related('products')
    )

class OrderCreateView(CreateView):
    queryset = (
        Order.objects
        .select_related('user')
        .prefetch_related('products')
    )
    # form_class = OrderForm
    fields = "user", "delivery_address", "promocode", "products"
    template_name = 'shopapp/order_form.html'
    success_url = reverse_lazy('shopapp:orders_list')

class OrderUpdateView(UpdateView):
    queryset = (
        Order.objects
        .select_related('user')
        .prefetch_related('products')
    )
    fields = "user", "delivery_address", "promocode", "products"
    template_name = 'shopapp/order_update_form.html'
    def get_success_url(self):
        return reverse(
            "shopapp:order_details",
            kwargs={"pk": self.object.pk},
        )

class OrderDeleteView(DeleteView):
    queryset = (
        Order.objects
        .select_related('user')
        .prefetch_related('products')
    )
    template_name = 'shopapp/order_confirm_delete.html'
    success_url = reverse_lazy("shopapp:orders_list")


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = "products_data_export"
        prdoucts_data = cache.get(cache_key)
        if prdoucts_data is None:
            products = Product.objects.order_by("pk").all()
            prdoucts_data = [
                {
                    "pk": product.pk,
                    "name": product.name,
                    "price": product.price,
                    "archived": product.archived,
                }
                for product in products
            ]

            cache.set(cache_key, prdoucts_data, 60)

        return JsonResponse({"products": prdoucts_data})

class OrdersExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.order_by("pk").all()
        orders_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user_id": order.user.pk,
                "products": [product.pk for product in order.products.all()],
            }
            for order in orders
        ]
        return JsonResponse({"orders": orders_data})

class UserOrdersListView(View):
    template_name = 'shopapp/user_orders_list.html'
    def get(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)

        orders = Order.objects.filter(user=user)

        self.owner = user

        context = self.get_context_data(owner=user, orders=orders)
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = {
            'owner': self.owner,
            **kwargs,
        }
        return context

class UserOrdersExportView(View):
    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)

        cache_key = f'user_orders_export_{user_id}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return JsonResponse(cached_data, safe=False)
        else:
            orders = Order.objects.filter(user=user).order_by('pk')
            serializer = OrderSerializer(orders, many=True)

            cache.set(cache_key, serializer.data, 60)

            return JsonResponse(serializer.data, safe=False)