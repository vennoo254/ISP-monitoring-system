# Minimal Django settings for the collector
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'change-me')
DEBUG = os.environ.get('DJANGO_DEBUG', '1') == '1'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'rest_framework',
    'api',
]
MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
]
ROOT_URLCONF = 'collector.urls'

TEMPLATES = []
WSGI_APPLICATION = 'collector.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# InfluxDB configuration (env)
INFLUX_URL = os.environ.get('INFLUX_URL', 'http://influxdb:8086')
INFLUX_ORG = os.environ.get('INFLUX_ORG', 'org')
INFLUX_BUCKET = os.environ.get('INFLUX_BUCKET', 'isp_metrics')
INFLUX_TOKEN = os.environ.get('INFLUX_TOKEN', 'influx-token')

# Notification service URL (Node.js service)
NOTIFICATION_SERVICE_URL = os.environ.get('NOTIFICATION_SERVICE_URL', 'http://node-notifier:4000/alert')

# Simple API key for probes
PROBE_API_KEY = os.environ.get('PROBE_API_KEY', 'default-probe-key')

STATIC_URL = '/static/'
