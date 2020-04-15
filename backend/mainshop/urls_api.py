from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from mainshop.views_api import *

app_name = 'mainshop'

urlpatterns = [
    path('customers/', CustomerList.as_view()),
    path('customers/<int:pk>/', CustomerDetail.as_view()),
    path('register/', register),
    path('products/', ProductList.as_view()),
    path('products/<int:pk>/', ProductDetail.as_view()),
    path('categories/', CategoryList.as_view()),
    path('categories/<int:pk>/', CategoryDetail.as_view()),
    path('suppliers/', SupplierList.as_view()),
    path('suppliers/<int:pk>/', SupplierDetail.as_view()),
    path('shopping-carts/', ShoppingCartList.as_view()),
    path('shopping-carts/<int:pk>/', ShoppingCartDetail.as_view()),
    path('shopping-cart-items/', ShoppingCartItemList.as_view()),
    path('shopping-cart-items/<int:pk>/', ShoppingCartItemDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
