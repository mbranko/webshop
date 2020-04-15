from .base import *

DEBUG = True
SENDFILE_BACKEND = 'sendfile.backends.development'

ALLOWED_HOSTS = ['localhost', ]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ATOMIC_REQUESTS': True,  # opseg transakcije = HTTP zahtev
    }
}

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'wq9ndh*5=06y6r#ob-9*0iva#w#u8v5d&s095$o$^=j2rg&2*c'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

API_THROTTLE_RATE = 100
