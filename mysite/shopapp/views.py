from timeit import default_timer

from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse, get_list_or_404, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView

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

class ProductCreateView(CreateView):
    model = Product
    # form_class = ProductForm
    fields = "name", "price", "description", "discount"
    success_url = reverse_lazy("shopapp:products_list")

class ProductUpdateView(UpdateView):
    model = Product 
    fields = "name", "price", "description", "discount"
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

def create_product(request: HttpRequest):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            # name = form.changed_data["name"]
            # price = form.changed_data["price"]
            # Product.objects.create(**form.cleaned_data)
            form.save()
            url = reverse("shopapp:products_list")
            return redirect(url)
    else:
        form = ProductForm()
    context = {
        'form': form,
    }
    return render(request, 'shopapp/create-product.html', context=context)

class OrderListView(ListView):
    queryset = (
        Order.objects
        .select_related('user')
        .prefetch_related('products')
    )

class OrderDetailView(DetailView):
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

