# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'j!l4u$r(^nusma)ll3izh!o79+x0yg4=$6!(0m0iwzchso28^-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Application definition

INSTALLED_APPS = (
  'epa.apps.EpaConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, "static"),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)
# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), '..', 'templates').replace('\\','/'),)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'EPA_Admin.urls'

WSGI_APPLICATION = 'EPA_Admin.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        #'HOST': 'local',
        'NAME': 'db',
       # 'USER': 'root',
       # 'PASSWORD': 'syefria'
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_PATH = (os.path.join(os.path.dirname(__file__), '..', 'static').replace('\\','/'),)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR + '/logs/debug.log',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'epa': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}

#EPA ADMIN SPECIFIC CONFIG

LOGIN_URL = '/login/'

MEDIA_ROOT = BASE_DIR + '/media/'
MEDIA_URL = '/media/'

#allowable file type type to upload
FILE_IMAGE = ('.jpg', 'jpeg', '.png', '.gif', '.bmp', 'tiff', '.tif')
FILE_TXT = ('.txt', 'text', '.xls', 'xlsx', '.csv')
EPA_ALLOWABLE_FILE_TYPES = [FILE_IMAGE, FILE_TXT]
EPA_IMAGE_VALID_HEADER = ('jpeg', 'gif', 'png', 'bmp', 'tiff')

#model config
EPA_UPLOAD_DATA_FILE_NAME_LENGTH = 100
EPA_UPLOAD_DATA_FOLDER = 'data/'
EPA_UPLOAD_DATA_THUMB_FOLDER = 'thumb/'
EPA_DEFAULT_THUMB_TXT_PATH = MEDIA_ROOT + '/' + EPA_UPLOAD_DATA_THUMB_FOLDER + 'default_text_thumb.jpg'
EPA_DEFAULT_THUMB_IMAGE_PATH = MEDIA_ROOT + '/' + EPA_UPLOAD_DATA_THUMB_FOLDER + 'default_image_thumb.jpg'
EPA_THUMB_SIZE = 110, 110

EPA_HELP_CAT_LENGTH = 400
EPA_HELP_TOPIC_LENGTH = 400
EPA_PREDICTION_TITLE_LENGTH = 300
EPA_PREDICTION_FOLDER = 'prediction/'
EPA_EXECUTE_LENGTH = 30

EPA_SHARED_FOLDER = BASE_DIR + '/upload'
EPA_SHARED_FOLDER_DATA = EPA_SHARED_FOLDER + '/' + EPA_UPLOAD_DATA_FOLDER

EPA_DEFAULT_PASSWORD_LENGTH = 8
EPA_FORGOT_PASSWORD_EMAIL_SENDER = 'no_replay@email.com'
EPA_FORGOT_PASSWORD_EMAIL_TITLE = 'EPA Admin Site Password Reset'
EPA_FORGOT_PASSWORD_EMAIL_BODY_TEMPLATE ='''
Hi %username%,

You're new password is %new_password%
'''

GET_AGGREGATE_DATA_ANALYSIS_URL = 'http://localhost:8989/epa/cyano/analysis/'
GET_PREDICTION_RESULTS_URL = 'http://localhost:8989/epa/cyano/blooming/'

EXECUTE_PREDICTION_DATA_ID = 1
PREDICTION_ALGORITHM_CONFIG_DATA_ID =1
