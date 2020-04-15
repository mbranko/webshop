from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from mainshop.models import Category, Supplier, Product, Customer, ShoppingCart, ShoppingCartItem


class CustomerInline(admin.StackedInline):
    model = Customer
    can_delete = False
    verbose_name_plural = 'customer'


# define a new user admin
class UserAdmin(BaseUserAdmin):
    inlines = (CustomerInline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Category)
admin.site.register(Supplier)
admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(ShoppingCart)
admin.site.register(ShoppingCartItem)
