# please at first create local_settings.py and put this information on it.

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '<your secret key>'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '<your database name>',
        'USER': '<your database root>',
        'PASSWORD': 'your password',
        'HOST': 'your database host',
        'PORT': 'your database port',
    }
}