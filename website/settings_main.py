# Django settings for the newsdiffs project.

ALLOWED_HOSTS = ['.newsdiffs.de', '.newsdiffs.de.',
                 'dev.newsdiffs.de', 'localhost', '127.0.0.1']

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('Newsdifds Admin', 'info@newsdiffs.de'),
)

MANAGERS = ADMINS
SERVER_EMAIL = "info@newsdiffs.de"

for line in open('/var/www/dev/.passdb.cnf').read().split():
    if line.startswith('password='):
        pwd = line.split('=')[1]
    if line.startswith('host='):
        host = line.split('=')[1] 
    if line.startswith('name='):
        name = line.split('=')[1]
    if line.startswith('user='):
        user = line.split('=')[1] 
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': host,
        'NAME': name,
        'USER': user,
        'PASSWORD': pwd,
        'OPTIONS': {
# This doesn't seem to work.
#            'read_default_file': '/mit/ecprice/.my.cnf',
        },
    }
}

if False: #django 1.3
    DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    DATABASE_NAME = name            # Or path to database file if using sqlite3.
    DATABASE_USER = user             # Not used with sqlite3.
    DATABASE_PASSWORD = pwd         # Not used with sqlite3.
    DATABASE_HOST = host             # Set to empty string for localhost. Not used with sqlite3.
    DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Berlin'

DATETIME_FORMAT = 'F j, Y, g:i a'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'de-DE'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '%p^2v#afb+ew#3en+%r55^gm4av_=e+s7w6a5(#ky92yp*56+l'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
  'django.template.loaders.filesystem.Loader',
  'django.template.loaders.app_directories.Loader',
#    'django.template.loaders.filesystem.load_template_source',
#    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
)

ROOT_URLCONF = 'website.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'south',
    'frontend',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}
