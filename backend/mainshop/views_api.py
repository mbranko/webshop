import datetime
import hashlib
import logging
import smtplib
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone
import django_filters
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, BooleanFilter, NumberFilter
from rest_framework import permissions, generics, status
from rest_framework.decorators import api_view, throttle_classes, permission_classes
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from drf_yasg.openapi import Schema, TYPE_STRING, TYPE_OBJECT, TYPE_ARRAY, TYPE_NUMBER, TYPE_INTEGER
from drf_yasg.utils import swagger_auto_schema
from concurrency.exceptions import RecordModifiedError
from mainshop.email import ACTIVATE_ACCOUNT_TEXT, ACTIVATE_ACCOUNT_TITLE
from mainshop.models import *
from mainshop.serializers import *


logger = logging.getLogger(__name__)


class DailyThrottle(UserRateThrottle):
    rate = f'{settings.API_THROTTLE_RATE}/day'


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Proverava da li prijavljeni korisnik ima prava da cita dati objekat
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        if not request.user.customer:
            return False
        if isinstance(view, CustomerDetail):
            return request.user.id == obj.user.id
        elif isinstance(view, ShoppingCartDetail):
            return request.user.customer.id == obj.customer_id
        elif isinstance(view, ShoppingCartItemDetail):
            return request.user.customer.id == obj.cart.customer_id
        return False


@swagger_auto_schema(
    method='POST',
    operation_description="Request account registration",
    request_body=Schema(
        title='Account registration data',
        type=TYPE_OBJECT,
        properties={
            'firstname': Schema(type=TYPE_STRING),
            'lastname': Schema(type=TYPE_STRING),
            'email': Schema(type=TYPE_STRING),
            'password': Schema(type=TYPE_STRING),
            'address': Schema(type=TYPE_STRING),
            'city': Schema(type=TYPE_STRING),
            'zipcode': Schema(type=TYPE_STRING),
        },
        required=['firstname', 'lastname', 'email', 'password', 'address', 'city', 'zipcode']
    ),
    responses={
       200: Schema(
           type=TYPE_OBJECT,
           properties={
               'activation_link': Schema(type=TYPE_STRING, description='account activation URL that will be sent in email')
           },
           required=['activation_url']
       ),

       409: 'A user with the given email is already registered',
       400: 'Invalid content in request',
       500: 'Internal server error',
    })
@api_view(['POST'])
@throttle_classes([DailyThrottle])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = NewUserSerializer(data=request.data)
    if serializer.is_valid():
        try:
            User.objects.get(email=request.data['email'])
            return Response(status=status.HTTP_409_CONFLICT)
        except User.MultipleObjectsReturned:
            logger.fatal(f"Two users found with email: {request.data['email']}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except User.DoesNotExist:
            user = User.objects.create_user(serializer.data['email'], serializer.data['email'],
                                            serializer.data['password'], is_staff=0, is_active=0)
            user.first_name = serializer.data['firstname']
            user.last_name = serializer.data['lastname']
            user.save()
            new_customer = Customer()
            new_customer.user = user
            new_customer.address = serializer.data['address']
            new_customer.city = serializer.data['city']
            new_customer.zip_code = serializer.data['zipcode']
            new_customer.activation_link = generate_link(user.email, datetime.datetime.now())
            new_customer.save()
            try:
                send_mail(ACTIVATE_ACCOUNT_TITLE,
                          ACTIVATE_ACCOUNT_TEXT % (new_customer.user.first_name, new_customer.user.last_name,
                                                   new_customer.activation_link),
                          'badasswebshop@gmail.com',
                          [user.email],
                          fail_silently=True)
            except smtplib.SMTPException:
                logger.fatal(f'Error sending email to: {user.email}')
            return Response({'activation_link': new_customer.activation_link}, status=status.HTTP_200_OK,
                            content_type='application/json')
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='POST',
    operation_description="Request account registration",
    request_body=Schema(
        title='Account registration data',
        type=TYPE_OBJECT,
        properties={
            'firstname': Schema(type=TYPE_STRING),
            'lastname': Schema(type=TYPE_STRING),
            'email': Schema(type=TYPE_STRING),
            'password': Schema(type=TYPE_STRING),
            'address': Schema(type=TYPE_STRING),
            'city': Schema(type=TYPE_STRING),
            'zipcode': Schema(type=TYPE_STRING),
        },
        required=['firstname', 'lastname', 'email', 'password', 'address', 'city', 'zipcode']
    ),
    responses={
       201: 'Purchase order created',
       404: 'Not enough items available',
       409: 'Optimistic lock: other client updated the same product',
       400: 'Invalid content in request',
       500: 'Internal server error',
    })
@api_view(['POST'])
def purchase(request):
    try:
        cart = ShoppingCart(customer=request.user.customer, order_date=timezone.now())
        cart.save()
        for order_item in request.data['items']:
            pid = order_item['productID']
            quantity = order_item['quantity']
            product = Product.objects.get(id=pid)
            if product.available_quantity >= quantity:
                product.available_quantity -= quantity
                product.save()
                cart_item = ShoppingCartItem(cart=cart, product=product, quantity=quantity)
                cart_item.save()
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        logger.info(f'Recorded purchase for: {request.user.email}')
        return Response(status=status.HTTP_201_CREATED)
    except RecordModifiedError:
        logger.warning('Optimistic lock!!!')
        return Response(status=status.HTTP_409_CONFLICT)
    except Product.MultipleObjectsReturned:
        logger.fatal(f'Multiple products found for ID: {pid}')
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except Product.DoesNotExist:
        logger.fatal(f'Unknown product ID: {pid}')
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except KeyError:
        logger.fatal(f'Invalid request data: {request.data}')
        return Response(status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='GET',
    operation_description="Fetch 6 most popular products",
    responses={
       200: Schema(
           type=TYPE_ARRAY,
           items=Schema(
               type=TYPE_OBJECT,
               properties={
                   'id': Schema(type=TYPE_STRING),
                   'name': Schema(type=TYPE_STRING),
                   'vendor': Schema(type=TYPE_STRING),
                   'description': Schema(type=TYPE_STRING),
                   'price': Schema(type=TYPE_NUMBER),
                   'available_quantity': Schema(type=TYPE_INTEGER),
                   'category': Schema(type=TYPE_INTEGER),
                   'supplier': Schema(type=TYPE_INTEGER),
               }
           ),
           required=['id', 'name', 'vendor', 'price', 'available_quantity', 'category', 'supplier']
       ),
       500: 'Internal server error',
    })
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def most_popular_products(request):
    try:
        result = Product.objects.all().annotate(sold=Sum('shoppingcartitem__quantity')).order_by('-sold')[:6]
    except Product.DoesNotExist:
        result = []
    srlzr = ProductSerializer(result, many=True)
    return Response(srlzr.data, status=status.HTTP_200_OK, content_type='application/json')


def generate_link(email, timestamp):
    """
    Generise link za aktivaciju naloga
    """
    src = email + timestamp.strftime('%Y-%m-%d %H:%M')
    return hashlib.sha1(src.encode('utf-8')).hexdigest()


class CustomerList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['user__first_name', 'user__last_name']


class CustomerDetail(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class ProductList(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['name', 'vendor', 'supplier__name', 'category_id']


class ProductDetail(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CategoryFilter(FilterSet):
    """
    Omogucava filtriranje kategorija:
    GET /api/categories/?parent=1 vraca kategorije kojima je roditelj catID:1
    GET /api/categories/?noparent=True vraca kategorije koje nemaju roditelja (top-level kategorije)
    GET /api/categories/?child=1 vraca kategorije kojima je dete catID:1 (lista je ili prazna ili ima 1 element)
    GET /api/categories/?product=1 vraca kategorije kojima pripada product ID:1 (lista je prazna ili ima 1 element)
    """
    noparent = BooleanFilter(field_name='parent', lookup_expr='isnull')
    child = NumberFilter(field_name='category', lookup_expr='exact')
    product = NumberFilter(field_name='product', lookup_expr='exact')

    class Meta:
        model = Category
        fields = ['name', 'parent', 'noparent', 'child', 'product']


class CategoryList(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CategoryFilter


class CategoryDetail(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SupplierList(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['name']


class SupplierDetail(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


class ShoppingCartList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['customer_id']


class ShoppingCartDetail(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer


class ShoppingCartItemList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    queryset = ShoppingCartItem.objects.all()
    serializer_class = ShoppingCartItemSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['cart__customer_id']


class ShoppingCartItemDetail(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    queryset = ShoppingCartItem.objects.all()
    serializer_class = ShoppingCartItemSerializer
