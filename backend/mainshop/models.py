from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    name = models.CharField('name', max_length=100)
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'


class Supplier(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'supplier'
        verbose_name_plural = 'suppliers'


class Product(models.Model):
    name = models.CharField(max_length=100)
    vendor = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    description = models.TextField(max_length=2000, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'products'


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    activation_link = models.CharField(max_length=100, default='')

    def name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def __str__(self):
        return self.name()

    class Meta:
        verbose_name = 'customer'
        verbose_name_plural = 'customers'


class ShoppingCart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateTimeField()

    def __str__(self):
        return f"{self.customer.name()} {self.order_date.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name = 'shopping cart'
        verbose_name_plural = 'shopping carts'


class ShoppingCartItem(models.Model):
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.cart.customer.name()} {self.product.name} {self.quantity}"

    class Meta:
        verbose_name = 'shopping cart item'
        verbose_name_plural = 'shopping cart items'
