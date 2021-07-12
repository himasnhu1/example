import os
import django_heroku
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# import environ

#environ.Env.read_env()

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['localhost', 'srmsp2c.herokuapp.com',"srms-backend.herokuapp.com","13.235.69.42"]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'widget_tweaks',
    'import_export',

    'corsheaders',

    'rest_framework',
    'fcm',
    'rest_framework.authtoken',
    'rest_auth',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'nested_admin',
    'rest_auth.registration',
    'djcelery',
    'storages',
    'django_crontab',
    'django_celery_results',
    "django_celery_beat",


    'core',
    'library',
    'owner',
    'student',
    'payment',
    'ubfcore',
    'ubfquiz',
    'ubfcart',
    'reward',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'srms.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'srms.wsgi.application'

OLD_PASSWORD_FIELD_ENABLED = True

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Calcutta'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# TIME_INPUT_FORMATS = ['%H:%M',]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static_in_venv')]
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_root')
STATICFILES_ROOT = os.path.join(BASE_DIR, 'static_root')

SITE_ID = 1
# LOGIN_REDIRECT_URL = '/'
# LOGIN_URL = 'accounts:login'
# LOGOUT_REDIRECT_URL = 'accounts:login'
# LOGOUT_URL = 'accounts:logout'


AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_KEY"]
# AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
# AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_KEY")
AWS_STORAGE_BUCKET_NAME = 'srms-bucket'
AWS_S3_REGION_NAME = 'ap-south-1'
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_ADDRESSING_STYLE = "virtual"

AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# AWS_S3_HOST = 's3.ap-south-1.amazonaws.com'

REST_FRAMEWORK = {
    # "DEFAULT_RENDERER_CLASSES" : [
    #     'rest_framework.renderers.JSONRenderer',
    # ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    "DATE_INPUT_FORMAT": "%Y-%m-%d",
    'DATETIME_INPUT_FORMAT': '%Y-%m-%d %H:%M',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DATETIME_FORMAT': "%b %d %Y %H:%M:%S",

}

CSRF_COOKIE_NAME = "csrftoken"

ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'
AUTH_USER_MODEL = 'core.User'

RAZORPAY_KEY_ID = os.environ["RAZORPAY_KEY_ID"]
RAZORPAY_KEY_SECRET = os.environ["RAZORPAY_KEY_SECRET"]

# EMAIL
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587

EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]
DEFAULT_FROM_EMAIL = 'UpscBasicFunda Team <noreply@upscbasicfunda.com>'

CELERY_BROKER_URL = os.environ["CELERY_BROKER_URL"]
CELERY_RESULT_BACKEND = os.environ["CELERY_RESULT_BACKEND"]
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Calcutta'
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'core.serializers.UserSerializer',
    'TOKEN_SERIALIZER': 'core.serializers.TokenSerializer'
}

FCM_DEVICE_MODEL : 'core.models.MyDevice'

REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'core.serializers.CustomRegisterSerializer',
}
# FCM_DJANGO_SETTINGS = {

#          # Your firebase API KEY
#         "FCM_SERVER_KEY": os.environ["FCM_SERVER_KEY"],
#         "ONE_DEVICE_PER_USER": False,
#         "DELETE_INACTIVE_DEVICES": False,
# }
FCM_APIKEY=os.environ["FCM_SERVER_KEY"]

#CORS_ORIGIN_WHITELIST = [
    #"https://srms.netlify.app",
    #"https://react-owner.herokuapp.com/",
    #"http://localhost:8080",
    #"http://127.0.0.1:8000",
    #"http://localhost:3000",
    #"https://localhost:3000",
    #"https://srms-backend.herokuapp.com",
    #"https://srms.example.com",
    #"http://srms.example.com",
    #"http://srms_owner_app.example.com",
    #"https://srms_owner_app.example.com",
    #"http://srms_employee_app.example.com",
    #"https://srms_employee_app.example.com",
    #"http://srms_student_app.example.com",
   # "https://srms_student_app.example.com",
#]

# CORS_ORIGIN_WHITELIST=[

# ]

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

django_heroku.settings(locals())
