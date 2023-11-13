from timeit import default_timer

from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse, get_list_or_404, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin

from .models import Product, Order
from .forms import ProductForm, OrderForm, GroupForm

class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('laptop', 1999),
            ('desktop', 2999),
            ('smartphone', 999),
        ]
        context = {
            'time_running': default_timer(),
            'products': products,
        }
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

class ProductDetails(DetailView):
    template_name = 'shopapp/product-details.html'
    model = Product
    context_object_name = "product"


class ProductsListView(ListView):
    template_name = 'shopapp/products-list.html'
    # model = Product
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)

class ProductCreateView(UserPassesTestMixin, CreateView):
    def test_func(self):
        # return self.request.user.groups.filter(name="secret-group").exists()
        return self.request.user.is_superuser

    queryset = (
        Product.objects
        .select_related('created_by_id')
    )
    model = Product
    # form_class = ProductForm
    fields = "created_by_id", "name", "price", "description", "discount"

    success_url = reverse_lazy("shopapp:products_list")

class ProductUpdateView(UpdateView):
    model = Product 
    fields = "name", "price", "description", "discount",
    template_name_suffix = "_update_form"
    def get_success_url(self):
        return reverse(
            "shopapp:products_details",
            kwargs={"pk": self.object.pk},
        )

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

