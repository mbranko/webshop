from .base import *
from .utils import read_variable

ALLOWED_HOSTS = ['localhost', 'badasswebshop.com', 'www.badasswebshop.com']
DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'webshop',
        'USER': 'webshop',
        'PASSWORD': 'webshop',
        'HOST': 'webshopdb',
        'PORT': '',
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

SECRET_KEY = read_variable('/private/secrets', 'SECRET_KEY') or 'unknown'
EMAIL_HOST_PASSWORD = read_variable('/private/secrets', 'EMAIL_HOST_PASSWORD') or 'unknown'

API_THROTTLE_RATE = 10
