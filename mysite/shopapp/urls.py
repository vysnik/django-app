from django.urls import path

from .views import (
    ShopIndexView,
    GroupListView,
    ProductDetailsView,
    ProductsListView,
    OrderListView,
    ProductCreateView,
    OrderDetailView,
    ProductUpdateView,
    ProductDeleteView,
    OrderCreateView,
    OrderUpdateView,
    OrderDeleteView,
    ProductsDataExportView,
    OrdersExportView,
    )

app_name = 'shopapp'

urlpatterns = [
    path('', ShopIndexView.as_view(), name='index'),
    path('groups/', GroupListView.as_view(), name='groups_list'),
    path('products/', ProductsListView.as_view(), name='products_list'),
    path('products/export/', ProductsDataExportView.as_view(), name='product-export'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/', ProductDetailsView.as_view(), name='products_details'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/confirm_delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('orders/', OrderListView.as_view(), name='orders_list'),
    path('orders/export/', OrdersExportView.as_view(), name='orders_export'),
    path('orders/<int:pk>/update/', OrderUpdateView.as_view(), name='order_update'),
    path('orders/<int:pk>/confirm_delete/', OrderDeleteView.as_view(), name='order_delete'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_details'),
    path('orders/create/', OrderCreateView.as_view(), name='order_create'),
]