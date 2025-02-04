from pathlib import Path
# 为了后面添加命令：STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]，导入OS:
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-ce66#u&3$g3gr!%at9r6-36247$au)rlv^qlgg&*96%$ya!jlt'

# At local runtime
# DEBUG = True
# ALLOWED_HOSTS = []

# At web runtime
DEBUG = False
# ALLOWED_HOSTS = ['first.mbcai.top', 'localhost', '66.42.86.76', '127.0.0.1']
ALLOWED_HOSTS = ['first.mbcai.top']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app01.apps.App01Config'
]

MIDDLEWARE = [
    'app01.midware.XContentTypeOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'EaninWeb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'app01', 'templates')],
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

WSGI_APPLICATION = 'EaninWeb.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mbcai',  # 数据库名
        'USER': 'root',
        'PASSWORD': '00ooMbc00oo',
        'HOST': '127.0.0.1',  # 哪台机器安装了MySQL
        'PORT': 3306,  # 端口
    }
}

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

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'app01', 'static'),  # 这种写法会在 collectstatic 时将 app01/static 目录中的静态文件包含在内
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # 或者 '/mbc/mbcaiWeb/app01/staticfiles/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
