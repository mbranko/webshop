from django.urls import path, include
from mainshop.views import activate_account, index

app_name = 'mainshop'

urlpatterns = [
    path('activate/<str:key>/', activate_account),
    path('', index),
]
