from .base import *
from .utils import read_variable, get_variable

ALLOWED_HOSTS = ['localhost', 'badasswebshop.com', 'www.badasswebshop.com']
DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': get_variable('POSTGRES_DBNAME', 'webshop'),
        'USER': get_variable('POSTGRES_USER', 'webshop'),
        'PASSWORD': get_variable('POSTGRES_PASSWORD', 'webshop'),
        'HOST': get_variable('POSTGRES_HOST', 'webshopdb'),
        'PORT': get_variable('POSTGRES_PORT', ''),
        'ATOMIC_REQUESTS': True,  # opseg transakcije = HTTP zahtev
    }
}

# email app_settings
EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'badasswebshop@gmail.com'
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

SECRET_KEY = read_variable('/private/secrets', 'SECRET_KEY') or get_variable('SECRET_KEY', 'unknown')
EMAIL_HOST_PASSWORD = read_variable('/private/secrets', 'EMAIL_HOST_PASSWORD') or get_variable('EMAIL_HOST_PASSWORD', 'unknown')

API_THROTTLE_RATE = 10
