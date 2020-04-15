from django.shortcuts import render
from mainshop.models import Customer


def activate_account(request, key):
    try:
        customer = Customer.objects.get(activation_link=key)
        customer.user.is_active = True
        customer.user.save()
        return render(request, 'mainshop/activated.html', context={'success': True})
    except Customer.DoesNotExist:
        return render(request, 'mainshop/activated.html', context={'success': False})


def index(request):
    return render(request, 'mainshop/index.html')
