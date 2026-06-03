"""
Django settings for Adonis Real Estate project.
Luxury Greek Residency & Immigration Website
"""

import pathlib
import os
from django.core.exceptions import ImproperlyConfigured

try:
    from dotenv import load_dotenv
    load_dotenv(pathlib.Path(__file__).resolve().parent.parent / '.env')
except ImportError:
    pass

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent

# ── Environment ──────────────────────────────────────────────────────────────

ENV = os.getenv('ENV', 'development').lower()
IS_PRODUCTION = ENV == 'production'

default_secret_key = 'django-insecure-dev-only-change-me'
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', default_secret_key)
if IS_PRODUCTION and SECRET_KEY == default_secret_key:
    raise ImproperlyConfigured('DJANGO_SECRET_KEY must be set in production.')

DEBUG = os.getenv('DEBUG', '0') == '1'
if IS_PRODUCTION and DEBUG:
    raise ImproperlyConfigured('DEBUG must be disabled in production.')

ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv(
        'ALLOWED_HOSTS',
        'adoniss.eu,www.adoniss.eu,adonis.eu,www.adonis.eu,'
        'adonisgroup.gr,www.adonisgroup.gr,localhost,127.0.0.1,'
        '46.224.176.159,testserver',
    ).split(',')
    if h.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        'CSRF_TRUSTED_ORIGINS',
        'https://adoniss.eu,https://www.adoniss.eu,https://adonis.eu,'
        'https://www.adonis.eu,https://adonisgroup.gr,https://www.adonisgroup.gr,'
        'http://46.224.176.159,https://46.224.176.159,http://localhost,'
        'https://localhost',
    ).split(',')
    if origin.strip()
]

USE_S3_MEDIA = os.getenv('USE_S3_MEDIA', '0') == '1'

# ── Installed Apps ────────────────────────────────────────────────────────────

INSTALLED_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'unfold.contrib.inlines',
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.forms',
    'ckeditor',
    'django_ckeditor_5',
    'core',
    'properties',
    'brochures',
    'apps.persian_cms',
]

if USE_S3_MEDIA:
    INSTALLED_APPS.append('storages')

# ── CKEditor 4 legacy config ──────────────────────────────────────────────────

_CK_HEADINGS_FULL = [
    {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
    {'model': 'heading1',   'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1'},
    {'model': 'heading2',   'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
    {'model': 'heading3',   'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3'},
    {'model': 'heading4',   'view': 'h4', 'title': 'Heading 4', 'class': 'ck-heading_heading4'},
    {'model': 'heading5',   'view': 'h5', 'title': 'Heading 5', 'class': 'ck-heading_heading5'},
    {'model': 'heading6',   'view': 'h6', 'title': 'Heading 6', 'class': 'ck-heading_heading6'},
]

_CK_FONT_SIZE = {
    'options': ['Tiny/10px', 'Small/12px', 'Normal/14px', '18px', 'Larger/22px', 'Huge/28px'],
}

_CK_ALIGNMENT = {
    'options': ['left', 'right', 'center', 'justify'],
}

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline', 'Strike', 'RemoveFormat'],
            ['NumberedList', 'BulletedList'],
            ['Link', 'Unlink'],
            ['Source'],
        ],
        'width': '100%',
        'removePlugins': 'elementspath',
        'fontSize_sizes': '10/10px;12/12px;14/14px;16/16px;18/18px;20/20px;24/24px;28/28px;32/32px;',
    },
}

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': {
            'items': [
                'heading', '|',
                'bold', 'italic', 'underline', 'strikethrough', '|',
                'fontSize', 'fontColor', 'fontBackgroundColor', '|',
                'alignment', '|',
                'bulletedList', 'numberedList', '|',
                'link', 'blockQuote', 'insertTable', '|',
                'imageUpload', 'mediaEmbed', '|',
                'undo', 'redo', 'sourceEditing',
            ],
        },
        'heading': {'options': _CK_HEADINGS_FULL},
        'fontSize': _CK_FONT_SIZE,
        'alignment': _CK_ALIGNMENT,
        'image': {
            'toolbar': [
                'imageTextAlternative', 'imageStyle:inline',
                'imageStyle:block', 'imageStyle:side',
            ],
        },
        'table': {
            'contentToolbar': [
                'tableColumn', 'tableRow', 'mergeTableCells',
                'tableProperties', 'tableCellProperties',
            ],
        },
        'height': '400px',
        'width': '100%',
    },
    'minimal': {
        'toolbar': {
            'items': ['bold', 'italic', 'link', '|', 'bulletedList', 'numberedList'],
        },
        'height': '200px',
        'width': '100%',
    },
    'blog': {
        'toolbar': [
            'heading', '|',
            'bold', 'italic', 'underline', 'strikethrough', '|',
            'fontSize', 'fontColor', 'fontBackgroundColor', '|',
            'alignment', '|',
            'link', 'bulletedList', 'numberedList', '|',
            'blockQuote', 'insertTable', '|',
            'undo', 'redo',
        ],
        'language': 'en',
    },
    # ── Dedicated config for the webinar landing rich-text fields ─────────
    # Mirrors the proven 'blog' config (used on GoldenVisaFa landing) and
    # adds fontFamily + custom palette. Anything advanced like
    # supportAllValues / supplementary plugins is intentionally avoided —
    # those flags break editor initialisation in this CKEditor 5 build and
    # cause the textarea to fall back to plain HTML input.
    'webinar_full': {
        'toolbar': [
            'heading', '|',
            'bold', 'italic', 'underline', 'strikethrough', '|',
            'fontFamily', 'fontSize', 'fontColor', 'fontBackgroundColor', '|',
            'alignment', '|',
            'bulletedList', 'numberedList', '|',
            'link', 'blockQuote', '|',
            'undo', 'redo',
        ],
        'heading': {'options': _CK_HEADINGS_FULL},
        'fontSize': {
            'options': [10, 12, 14, 16, 18, 20, 22, 24, 28, 32, 36, 40, 48, 56, 64, 72],
        },
        'fontFamily': {
            'options': [
                'default',
                'Vazirmatn, sans-serif',
                'Inter, sans-serif',
                'Tahoma, Geneva, sans-serif',
                'Arial, Helvetica, sans-serif',
                'Georgia, serif',
                '"Times New Roman", Times, serif',
                '"Courier New", Courier, monospace',
            ],
        },
        'fontColor': {
            'colors': [
                {'color': '#ffffff', 'label': 'White'},
                {'color': '#f5f1e6', 'label': 'Cream'},
                {'color': '#efd99a', 'label': 'Gold light'},
                {'color': '#d4b057', 'label': 'Gold'},
                {'color': '#c9a84c', 'label': 'Gold deep'},
                {'color': '#b08d35', 'label': 'Gold dark'},
                {'color': '#0a1530', 'label': 'Navy'},
                {'color': '#0f2147', 'label': 'Navy 2'},
                {'color': '#1f407c', 'label': 'Royal blue'},
                {'color': '#c5cee0', 'label': 'Muted blue'},
                {'color': '#1e293b', 'label': 'Slate'},
                {'color': '#94a3b8', 'label': 'Slate light'},
                {'color': '#16a34a', 'label': 'Green'},
                {'color': '#dc2626', 'label': 'Red'},
            ],
        },
        'fontBackgroundColor': {
            'colors': [
                {'color': '#ffffff', 'label': 'White'},
                {'color': '#fef9c3', 'label': 'Sand'},
                {'color': '#fde68a', 'label': 'Light gold'},
                {'color': '#d4b057', 'label': 'Gold'},
                {'color': '#0a1530', 'label': 'Navy'},
                {'color': '#1f407c', 'label': 'Royal blue'},
                {'color': '#dc2626', 'label': 'Red'},
                {'color': '#16a34a', 'label': 'Green'},
            ],
        },
        'alignment': _CK_ALIGNMENT,
        'language': 'en',
    },
    # ── Persian blog body: RTL content + image upload ─────────────────────
    # Mirrors the package 'default' toolbar (proven to initialise in this
    # build) and only flips the *content* language to Persian so the editing
    # area is right-to-left. UI language stays English (always bundled) to
    # avoid the init-fallback issue noted on the webinar config. Images upload
    # to the local FileSystemStorage (/ckeditor5/), so it works fully offline.
    'persian_blog': {
        'toolbar': {
            'items': [
                'heading', '|',
                'bold', 'italic', 'underline', 'strikethrough', '|',
                'fontSize', 'fontColor', 'fontBackgroundColor', '|',
                'alignment', '|',
                'bulletedList', 'numberedList', '|',
                'link', 'blockQuote', 'insertTable', '|',
                'imageUpload', 'mediaEmbed', '|',
                'undo', 'redo', 'sourceEditing',
            ],
        },
        'heading': {'options': _CK_HEADINGS_FULL},
        'fontSize': _CK_FONT_SIZE,
        'alignment': _CK_ALIGNMENT,
        'image': {
            'toolbar': [
                'imageTextAlternative', 'imageStyle:inline',
                'imageStyle:block', 'imageStyle:side',
            ],
        },
        'table': {
            'contentToolbar': [
                'tableColumn', 'tableRow', 'mergeTableCells',
                'tableProperties', 'tableCellProperties',
            ],
        },
        'language': {'ui': 'en', 'content': 'fa'},
        'height': '500px',
        'width': '100%',
    },
    # ── Persian Clean: RTL editor with removeFormat for Word paste cleanup ──────
    # This config is optimized for pasting content from Microsoft Word. It has
    # minimal formatting tools and includes removeFormat to strip Word styles.
    # Allowed tags: p, h2, h3, h4, ul, ol, li, strong, b, em, br, a
    'persian_clean': {
        'toolbar': {
            'items': [
                'heading', '|',
                'bold', 'italic', '|',
                'bulletedList', 'numberedList', '|',
                'link', '|',
                'removeFormat', '|',
                'undo', 'redo', 'sourceEditing',
            ],
        },
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3'},
                {'model': 'heading4', 'view': 'h4', 'title': 'Heading 4', 'class': 'ck-heading_heading4'},
            ],
        },
        'language': {'ui': 'en', 'content': 'fa'},
        'height': '400px',
        'width': '100%',
    },
}

CKEDITOR_5_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
CKEDITOR_5_UPLOAD_PATH  = 'blog/uploads/'
CKEDITOR_5_CUSTOM_CSS   = 'css/ckeditor5-custom.css'
CK_EDITOR_5_UPLOAD_FILE_TYPES = ['jpeg', 'jpg', 'png', 'gif', 'webp']
CK_EDITOR_5_MAX_FILE_SIZE = 5242880  # 5 MB

MODELTRANSLATION_CUSTOM_FIELDS = ('RichTextField', 'CKEditor5Field')

# ── Middleware ────────────────────────────────────────────────────────────────

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'apps.persian_cms.middleware.PersianRedirectMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.persian_cms.middleware.PersianAdminNoIndexMiddleware',
    'core.middleware.ErrorCaptureMiddleware',
    'core.middleware.SlugRedirectMiddleware',
    'core.middleware.AdminNoCacheMiddleware',
]

ROOT_URLCONF = 'adonis.urls'

# Template loader chain. In production the cached loader keeps parsed
# templates in memory, eliminating per-request disk I/O. In DEBUG we use the
# raw loaders so editing templates is reflected without restarting the worker.
# NOTE: Django forbids `APP_DIRS` and `loaders` from being set at the same
# time, so APP_DIRS is set to False here and `app_directories.Loader` is
# included explicitly inside the loaders list to preserve the previous
# template-discovery behaviour.
_TEMPLATE_LOADERS = [
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
]
if not DEBUG:
    _TEMPLATE_LOADERS = [
        ('django.template.loaders.cached.Loader', _TEMPLATE_LOADERS),
    ]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'adonis' / 'templates'],
        'APP_DIRS': False,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.site_settings',
            ],
            'loaders': _TEMPLATE_LOADERS,
        },
    },
]

WSGI_APPLICATION = 'adonis.wsgi.application'

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

# ── Database ──────────────────────────────────────────────────────────────────

DB_ENGINE = os.getenv('DB_ENGINE', 'sqlite')

if IS_PRODUCTION and DB_ENGINE != 'postgres':
    raise ImproperlyConfigured('Production must use PostgreSQL only (DB_ENGINE=postgres).')

if DB_ENGINE == 'postgres':
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.postgresql',
            'NAME':     os.getenv('POSTGRES_DB', 'adonis'),
            'USER':     os.getenv('POSTGRES_USER', 'adonis'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
            'HOST':     os.getenv('POSTGRES_HOST', '127.0.0.1'),
            'PORT':     int(os.getenv('POSTGRES_PORT', '5432')),
            'CONN_MAX_AGE': int(os.getenv('POSTGRES_CONN_MAX_AGE', '60')),
        }
    }
    DB_ENV_TAG = os.getenv('DB_ENV_TAG', '')
    if DB_ENV_TAG and DB_ENV_TAG != ENV:
        raise ImproperlyConfigured(
            f"Database environment tag mismatch: DB_ENV_TAG='{DB_ENV_TAG}' but ENV='{ENV}'"
        )
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME':   os.getenv('SQLITE_PATH', str(BASE_DIR / 'db.sqlite3')),
        }
    }

# ── Cache ─────────────────────────────────────────────────────────────────────

CACHES = {
    'default': {
        'BACKEND':  os.getenv('CACHE_BACKEND', 'django.core.cache.backends.locmem.LocMemCache'),
        'LOCATION': os.getenv('CACHE_LOCATION', 'adonis-default-cache'),
        'TIMEOUT':  int(os.getenv('CACHE_TIMEOUT', '300')),
    }
}

REDIS_URL = os.getenv('REDIS_URL', '')
if REDIS_URL and os.getenv('CACHE_BACKEND', '').startswith('django_redis'):
    CACHES['default'] = {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'IGNORE_EXCEPTIONS': True,
        },
        'TIMEOUT': int(os.getenv('CACHE_TIMEOUT', '300')),
    }

# ── Auth ──────────────────────────────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Internationalisation ──────────────────────────────────────────────────────

LANGUAGE_CODE = 'en'
TIME_ZONE     = 'Europe/Athens'
USE_I18N = True
USE_L10N = True
USE_TZ   = True

LANGUAGES = [
    ('en', 'English'),
    ('tr', 'Turkish'),
]

LOCALE_PATHS = [BASE_DIR / 'locale']

LANGUAGE_COOKIE_AGE      = 365 * 24 * 3600  # 1 year
LANGUAGE_COOKIE_SAMESITE = 'Lax'

MODELTRANSLATION_DEFAULT_LANGUAGE   = 'en'
MODELTRANSLATION_FALLBACK_LANGUAGES = ('en',)

# ── Static & Media ────────────────────────────────────────────────────────────

STATIC_URL      = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'adonis' / 'static']
STATIC_ROOT     = BASE_DIR / 'staticfiles'

# WhiteNoise: serve compressed (gzip + brotli) hashed static files with a
# 1-year browser cache. Requires `pip install whitenoise[brotli]` and a
# successful `python manage.py collectstatic` run for the manifest.
STATICFILES_STORAGE = 'adonis.storage.GracefulCompressedManifestStaticFilesStorage'
WHITENOISE_MAX_AGE  = 31536000
WHITENOISE_USE_FINDERS = False  # only serve from STATIC_ROOT in prod (faster, no per-request finder walk)

if USE_S3_MEDIA:
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', '')
    AWS_S3_REGION_NAME      = os.getenv('AWS_S3_REGION_NAME', '')
    AWS_S3_SIGNATURE_VERSION = os.getenv('AWS_S3_SIGNATURE_VERSION', 's3v4')
    AWS_ACCESS_KEY_ID       = os.getenv('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY   = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    AWS_DEFAULT_ACL         = None
    AWS_QUERYSTRING_AUTH    = False
    AWS_S3_FILE_OVERWRITE   = False
    AWS_S3_CUSTOM_DOMAIN    = os.getenv('AWS_S3_CUSTOM_DOMAIN', '')
    if not AWS_STORAGE_BUCKET_NAME:
        raise ImproperlyConfigured('AWS_STORAGE_BUCKET_NAME must be set when USE_S3_MEDIA=1')
    DEFAULT_FILE_STORAGE = 'adonis.storage_backends.PrivateMediaStorage'
    if AWS_S3_CUSTOM_DOMAIN:
        MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
    else:
        MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
else:
    MEDIA_URL  = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

DATA_UPLOAD_MAX_MEMORY_SIZE    = 524288000   # 500 MB
FILE_UPLOAD_MAX_MEMORY_SIZE    = 524288000   # 500 MB
FILE_UPLOAD_TEMP_DIR           = '/tmp'
DATA_UPLOAD_MAX_NUMBER_FILES   = 200

# ── Logging ───────────────────────────────────────────────────────────────────

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'pii_redact': {
            '()': 'core.logging_filters.PiiRedactionFilter',
        },
    },
    'handlers': {
        'file': {
            'level':    os.getenv('DJANGO_FILE_LOG_LEVEL', 'WARNING'),
            'class':    'logging.FileHandler',
            'filename': str(BASE_DIR / 'django_errors.log'),
            'filters':  ['pii_redact'],
        },
        'console': {
            'level': os.getenv('DJANGO_LOG_LEVEL', 'WARNING'),
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers':  ['file', 'console'],
            'level':     os.getenv('DJANGO_LOG_LEVEL', 'WARNING'),
            'propagate': True,
        },
        'django.security': {
            'handlers':  ['file', 'console'],
            'level':     os.getenv('DJANGO_SECURITY_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}

# ── Misc ──────────────────────────────────────────────────────────────────────

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SITE_NAME    = 'Adonis Group'
SITE_TAGLINE = 'Greek Residency & Immigration'
WHATSAPP_NUMBER = '+306985989596'
SITE_EMAIL   = 'info@adonisgroup.gr'
SITE_ADDRESS = 'Athens, Alimos, Poseidonos Avenue, No. 78, 1st Floor'

GOOGLE_MAPS_API_KEY  = os.getenv('GOOGLE_MAPS_API_KEY', '')
ANTHROPIC_API_KEY   = os.getenv('ANTHROPIC_API_KEY', '')
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY', '')

GTM_ID = os.getenv('GTM_ID', 'GTM-WS58NGGC')

# ── Email ─────────────────────────────────────────────────────────────────────

EMAIL_BACKEND      = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST         = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT         = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS      = os.getenv('EMAIL_USE_TLS', '1') == '1'
EMAIL_USE_SSL      = os.getenv('EMAIL_USE_SSL', '0') == '1'
EMAIL_HOST_USER    = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@adoniss.gr')
MARKETING_EMAIL    = os.getenv('MARKETING_EMAIL', 'Marketing@adoniss.gr')

# ── Auth redirects ────────────────────────────────────────────────────────────

LOGIN_REDIRECT_URL  = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# ── Security ──────────────────────────────────────────────────────────────────

SECURE_PROXY_SSL_HEADER     = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY      = 'strict-origin-when-cross-origin'
X_FRAME_OPTIONS             = 'SAMEORIGIN'
SESSION_COOKIE_SAMESITE     = 'Lax'
CSRF_COOKIE_SAMESITE        = 'Lax'

if IS_PRODUCTION:
    SECURE_SSL_REDIRECT             = True
    SESSION_COOKIE_SECURE           = True
    CSRF_COOKIE_SECURE              = True
    SECURE_HSTS_SECONDS             = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS  = True
    SECURE_HSTS_PRELOAD             = True
else:
    SECURE_SSL_REDIRECT             = False
    SESSION_COOKIE_SECURE           = False
    CSRF_COOKIE_SECURE              = False
    SECURE_HSTS_SECONDS             = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS  = False
    SECURE_HSTS_PRELOAD             = False

# ── Backup settings ───────────────────────────────────────────────────────────

BACKUP_LOCAL_DIR       = os.getenv('BACKUP_LOCAL_DIR', str(BASE_DIR / 'backups'))
BACKUP_RETENTION_DAYS  = int(os.getenv('BACKUP_RETENTION_DAYS', '30'))
BACKUP_S3_BUCKET       = os.getenv('BACKUP_S3_BUCKET', '')
BACKUP_S3_PREFIX       = os.getenv('BACKUP_S3_PREFIX', f'{ENV}/database')
BACKUP_REQUIRE_OFFSITE = os.getenv('BACKUP_REQUIRE_OFFSITE', '0') == '1'
# S3-compatible endpoint for off-site backups. For ArvanCloud Object Storage
# set e.g. https://s3.ir-thr-at1.arvanstorage.ir (leave empty for AWS S3).
BACKUP_S3_ENDPOINT_URL = os.getenv('BACKUP_S3_ENDPOINT_URL', '') or os.getenv('AWS_S3_ENDPOINT_URL', '')
# Object-storage prefix under which the (incrementally synced) media/ tree is mirrored.
BACKUP_MEDIA_PREFIX    = os.getenv('BACKUP_MEDIA_PREFIX', f'{ENV}/media')

# ── Sentry (optional) ─────────────────────────────────────────────────────────

SENTRY_DSN = os.getenv('SENTRY_DSN', '')
if SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[DjangoIntegration()],
            traces_sample_rate=float(os.getenv('SENTRY_TRACES_SAMPLE_RATE', '0.05')),
            send_default_pii=False,
        )
    except ImportError:
        pass

# ── Unfold Admin ──────────────────────────────────────────────────────────────

from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


def _can(perm: str):
    def check(request):
        return request.user.has_perm(perm)
    return check


def _can_any(*perms: str):
    def check(request):
        return any(request.user.has_perm(p) for p in perms)
    return check


def _any_staff(request):
    return request.user.is_active and request.user.is_staff


UNFOLD = {
    'SITE_TITLE': 'ADONIS Admin',
    'SITE_HEADER': 'ADONIS Group',
    'SITE_SYMBOL': 'domain',
    'SHOW_HISTORY': True,
    'DASHBOARD_CALLBACK': 'core.admin_dashboard.dashboard_callback',
    'STYLES': [
        lambda request: static('css/admin-unfold.css'),
        lambda request: static('css/admin-persian-font.css') + '?v=20260528-estedad',
        lambda request: static('css/fa-admin-fix.css'),
    ],
    'COLORS': {
        'font': {
            '50':  '240 253 250',
            '100': '204 251 241',
            '200': '153 246 228',
            '300': '94 234 212',
            '400': '45 212 191',
            '500': '20 184 166',
            '600': '13 148 136',
            '700': '15 118 110',
            '800': '17 94 89',
            '900': '19 78 74',
            '950': '4 47 46',
        },
        'primary': {
            '50':  '243 244 246',
            '100': '209 213 219',
            '200': '156 163 175',
            '300': '107 114 128',
            '400': '75 85 99',
            '500': '17 24 39',
            '600': '17 24 39',
            '700': '17 24 39',
            '800': '17 24 39',
            '900': '17 24 39',
            '950': '17 24 39',
        },
    },
    'SIDEBAR': {
        'show_search': True,
        'show_all_applications': False,
        'navigation': [
            {
                'title': _('🏠 صفحه اصلی فارسی'),
                'collation': 'fa-homepage',
                'icon': 'home',
                'separator': True,
                'collapsible': True,
                'items': [
                    {'title': _('⚙️ تنظیمات کلی و هیرو (ویدیوی اینترو)'), 'icon': 'play_circle', 'icon_class': 'text-blue-500', 'link': reverse_lazy('admin:core_fanewsettings_changelist'), 'permission': _can('core.change_fanewsettings')},
                    {'title': _('📐 سکشن‌های صفحه اصلی'), 'icon': 'view_agenda', 'icon_class': 'text-blue-400', 'link': reverse_lazy('admin:core_fanewsection_changelist'), 'permission': _can('core.change_fanewsection')},
                    {'title': _('🧭 منوی ناوبری (+ زیرمنو)'), 'icon': 'menu', 'icon_class': 'text-blue-500', 'link': reverse_lazy('admin:core_fanavmenuitem_changelist'), 'permission': _can('core.change_fanavmenuitem')},
                    {'title': _('🦶 فوتر'), 'icon': 'bottom_navigation', 'link': reverse_lazy('admin:core_fafootersettings_changelist'), 'permission': _can('core.change_fafootersettings')},
                    {'title': _('👁 پیش‌نمایش صفحه فارسی'), 'icon': 'preview', 'icon_class': 'text-green-300', 'link': '/fa-new/'},
                ],
            },
            {
                'title': _('📝 محتوای فارسی'),
                'collation': 'fa-content',
                'icon': 'edit_note',
                'separator': True,
                'collapsible': True,
                'items': [
                    {'title': _('📝 بلاگ فارسی'), 'icon': 'edit_note', 'icon_class': 'text-green-400', 'link': '/fa-admin/persian_cms/persianblogpost/', 'permission': _any_staff},
                    {'title': _('📄 صفحات فارسی (تعریف/طراحی)'), 'icon': 'description', 'icon_class': 'text-green-400', 'link': '/fa-admin/persian_cms/persianpage/', 'permission': _any_staff},
                    {'title': _('➕ صفحه جدید'), 'icon': 'note_add', 'link': '/fa-admin/persian_cms/persianpage/add/', 'permission': _any_staff},
                    {'title': _('🔍 تنظیمات سئو فارسی'), 'icon': 'travel_explore', 'link': '/fa-admin/persian_cms/persianseosettings/', 'permission': _any_staff},
                    {'title': _('🤖 پایپ‌لاین SEO فارسی'), 'icon': 'auto_awesome', 'icon_class': 'text-green-400', 'link': reverse_lazy('admin:properties_facontentpipeline_changelist'), 'permission': _any_staff},
                    {'title': _('🛠 پنل کامل مدیریت فارسی'), 'icon': 'dashboard', 'icon_class': 'text-green-400', 'link': '/fa-admin/', 'permission': _any_staff},
                ],
            },
            {
                'title': _('🏢 املاک فارسی'),
                'collation': 'fa-properties',
                'icon': 'apartment',
                'separator': True,
                'collapsible': True,
                'items': [
                    {'title': _('📋 پروژه‌های ملکی فارسی'), 'icon': 'apartment', 'icon_class': 'text-amber-500', 'link': '/fa-admin/persian_cms/faproperty/', 'permission': _any_staff},
                    {'title': _('➕ افزودن پروژه جدید'), 'icon': 'add_home', 'icon_class': 'text-amber-400', 'link': '/fa-admin/persian_cms/faproperty/add/', 'permission': _any_staff},
                    {'title': _('🖼️ رسانه‌های املاک'), 'icon': 'photo_library', 'link': '/fa-admin/persian_cms/fapropertymedia/', 'permission': _any_staff},
                ],
            },
            {
                'title': _('🏢 املاک انگلیسی'),
                'collation': 'properties',
                'icon': 'domain',
                'separator': False,
                'collapsible': True,
                'items': [
                    {'title': _('همه ملک‌ها (EN)'), 'icon': 'apartment', 'icon_class': 'text-primary-500', 'link': reverse_lazy('admin:properties_property_changelist'), 'permission': _can('properties.view_property')},
                    {'title': _('افزودن ملک (EN)'), 'icon': 'add_home', 'icon_class': 'text-primary-400', 'link': reverse_lazy('admin:properties_property_add'), 'permission': _can('properties.add_property')},
                    {'title': _('واحدها'), 'icon': 'door_open', 'link': reverse_lazy('admin:properties_propertyunit_changelist'), 'permission': _can('properties.view_propertyunit')},
                    {'title': _('دسته‌بندی‌ها'), 'icon': 'category', 'link': reverse_lazy('admin:properties_propertycategory_changelist'), 'permission': _can('properties.view_propertycategory')},
                ],
            },
            {
                'title': _('✉️ فرم‌ها و درخواست‌ها'),
                'collation': 'forms-requests',
                'icon': 'inbox',
                'separator': True,
                'collapsible': True,
                'items': [
                    {'title': _('فرم‌های تماس / مشاوره'), 'icon': 'mail', 'link': reverse_lazy('admin:core_contactsubmission_changelist'), 'permission': _can('core.view_contactsubmission'), 'badge': 'core.admin_dashboard.badge_contacts_today'},
                    {'title': _('درخواست‌های همکاری'), 'icon': 'handshake', 'link': reverse_lazy('admin:core_partnerlead_changelist'), 'permission': _can('core.view_partnerlead'), 'badge': 'core.admin_dashboard.badge_partner_leads_new'},
                    {'title': _('مشتریان'), 'icon': 'person', 'link': reverse_lazy('admin:core_customer_changelist'), 'permission': _can('core.view_customer')},
                ],
            },
            {
                'title': _('👥 کاربران و دسترسی'),
                'collation': 'users-access',
                'icon': 'manage_accounts',
                'separator': True,
                'collapsible': True,
                'items': [
                    {'title': _('کاربران ادمین'), 'icon': 'manage_accounts', 'link': reverse_lazy('admin:auth_user_changelist'), 'permission': _can('auth.view_user')},
                    {'title': _('نقش‌ها / گروه‌ها'), 'icon': 'groups', 'icon_class': 'text-violet-400', 'link': reverse_lazy('admin:auth_group_changelist'), 'permission': _can('auth.view_group')},
                ],
            },
            {
                'title': _('⚙️ پیشرفته'),
                'collation': 'advanced',
                'icon': 'settings_applications',
                'separator': True,
                'collapsible': True,
                'items': [
                    {'title': _('تنظیمات سایت'), 'icon': 'settings', 'link': reverse_lazy('admin:core_sitesettings_changelist'), 'permission': _can('core.view_sitesettings')},
                    {'title': _('📅 برنامه تولید محتوا'), 'icon': 'schedule', 'link': reverse_lazy('admin:properties_contentschedule_changelist'), 'permission': _any_staff},
                    {'title': _('لاگ تغییرات'), 'icon': 'history', 'link': reverse_lazy('admin:core_auditlog_changelist'), 'permission': _can('core.view_auditlog')},
                    {'title': _('لاگ خطاها'), 'icon': 'bug_report', 'link': reverse_lazy('admin:core_errorlog_changelist'), 'permission': _can('core.view_errorlog')},
                    {'title': _('پشتیبان‌گیری کامل'), 'icon': 'cloud_download', 'link': '/admin/site-backup/'},
                ],
            },
            # NOTE: English-only homepage blocks (testimonials, FAQ, services,
            # process steps, golden-visa cards, events, brochures, EN SEO
            # pipeline) are intentionally hidden from the sidebar for now.
            # They are NOT deleted — the models stay registered and reachable
            # by direct URL (e.g. /admin/core/testimonial/). Re-add a group
            # here to surface them again.
        ],
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# UNFOLD_PERSIAN — Separate settings for Persian admin at /fa-admin/
# This ensures the Persian admin sidebar only shows Persian models
# ══════════════════════════════════════════════════════════════════════════════
UNFOLD_PERSIAN = {
    'SITE_TITLE': 'پنل فارسی آدونیس',
    'SITE_HEADER': 'مدیریت محتوای فارسی',
    'SITE_SYMBOL': 'domain',
    'SHOW_HISTORY': True,
    'STYLES': [
        lambda request: static('css/admin-unfold.css'),
        lambda request: static('css/persian-admin.css'),
        lambda request: static('css/fa-admin-fix.css'),
    ],
    'SIDEBAR': {
        'show_search': True,
        'show_all_applications': False,
        'navigation': [
            {
                'title': _('🏠 پروژه‌های ملکی'),
                'separator': True,
                'collapsible': False,
                'items': [
                    {'title': _('📋 همه پروژه‌ها'), 'icon': 'apartment', 'link': '/fa-admin/persian_cms/faproperty/'},
                    {'title': _('➕ افزودن پروژه'), 'icon': 'add_home', 'link': '/fa-admin/persian_cms/faproperty/add/'},
                    {'title': _('🖼️ رسانه‌های املاک'), 'icon': 'photo_library', 'link': '/fa-admin/persian_cms/fapropertymedia/'},
                ],
            },
            {
                'title': _('📐 صفحه اصلی'),
                'separator': True,
                'collapsible': True,
                'items': [
                    {'title': _('⚙️ تنظیمات هیرو'), 'icon': 'play_circle', 'link': '/fa-admin/core/fanewsettings/'},
                    {'title': _('📐 سکشن‌ها'), 'icon': 'view_agenda', 'link': '/fa-admin/core/fanewsection/'},
                    {'title': _('🧭 منوی ناوبری'), 'icon': 'menu', 'link': '/fa-admin/core/fanavmenuitem/'},
                    {'title': _('🦶 فوتر'), 'icon': 'bottom_navigation', 'link': '/fa-admin/core/fafootersettings/'},
                ],
            },
            {
                'title': _('📝 محتوا'),
                'separator': True,
                'collapsible': True,
                'items': [
                    {'title': _('📝 بلاگ فارسی'), 'icon': 'edit_note', 'link': '/fa-admin/persian_cms/persianblogpost/'},
                    {'title': _('📄 صفحات'), 'icon': 'description', 'link': '/fa-admin/persian_cms/persianpage/'},
                    {'title': _('🚀 لندینگ پیج‌ها'), 'icon': 'rocket_launch', 'link': '/fa-admin/persian_cms/goldenvisalandingpage/'},
                    {'title': _('🔍 تنظیمات سئو'), 'icon': 'travel_explore', 'link': '/fa-admin/persian_cms/persianseosettings/'},
                    {'title': _('❓ سوالات متداول'), 'icon': 'quiz', 'link': '/fa-admin/persian_cms/persianfaq/'},
                ],
            },
            {
                'title': _('🎨 بخش‌های لندینگ'),
                'separator': False,
                'collapsible': True,
                'items': [
                    {'title': _('🎬 هیرو'), 'icon': 'slideshow', 'link': '/fa-admin/persian_cms/gvherosection/'},
                    {'title': _('⭐ مزایا'), 'icon': 'stars', 'link': '/fa-admin/persian_cms/gvbenefitssection/'},
                    {'title': _('✅ شرایط'), 'icon': 'checklist', 'link': '/fa-admin/persian_cms/gveligibilitysection/'},
                    {'title': _('📊 مراحل'), 'icon': 'timeline', 'link': '/fa-admin/persian_cms/gvprocesssection/'},
                    {'title': _('📈 آمار'), 'icon': 'analytics', 'link': '/fa-admin/persian_cms/gvstatisticssection/'},
                    {'title': _('🏗️ پروژه‌ها'), 'icon': 'business', 'link': '/fa-admin/persian_cms/gvproject/'},
                    {'title': _('👨‍👩‍👧 خانواده'), 'icon': 'family_restroom', 'link': '/fa-admin/persian_cms/gvfamilysection/'},
                    {'title': _('📋 مدارک'), 'icon': 'folder', 'link': '/fa-admin/persian_cms/gvdocumentssection/'},
                    {'title': _('💰 هزینه‌ها'), 'icon': 'payments', 'link': '/fa-admin/persian_cms/gvcostsection/'},
                    {'title': _('💬 نظرات'), 'icon': 'reviews', 'link': '/fa-admin/persian_cms/gvtestimonialssection/'},
                    {'title': _('❓ FAQ'), 'icon': 'help', 'link': '/fa-admin/persian_cms/gvfaqsection/'},
                    {'title': _('📢 CTA'), 'icon': 'campaign', 'link': '/fa-admin/persian_cms/gvfinalctasection/'},
                    {'title': _('🔍 سئو'), 'icon': 'search', 'link': '/fa-admin/persian_cms/gvseosettings/'},
                    {'title': _('🎨 طراحی'), 'icon': 'palette', 'link': '/fa-admin/persian_cms/gvdesignsettings/'},
                ],
            },
            {
                'title': _('⚙️ تنظیمات'),
                'separator': True,
                'collapsible': True,
                'items': [
                    {'title': _('🖼️ رسانه‌ها'), 'icon': 'perm_media', 'link': '/fa-admin/persian_cms/persianmediaasset/'},
                    {'title': _('🔗 منوها'), 'icon': 'link', 'link': '/fa-admin/persian_cms/persianmenuitem/'},
                    {'title': _('🔀 ریدایرکت‌ها'), 'icon': 'alt_route', 'link': '/fa-admin/persian_cms/persianredirectmap/'},
                ],
            },
            {
                'title': _('👁 پیش‌نمایش'),
                'separator': True,
                'collapsible': False,
                'items': [
                    {'title': _('🌐 مشاهده سایت'), 'icon': 'preview', 'link': '/fa-new/'},
                ],
            },
        ],
    },
}

# Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
# Source label prefixed to every outgoing Telegram message so leads from this
# server are distinguishable when multiple sites share one bot/group.
TELEGRAM_SOURCE_LABEL = os.getenv('TELEGRAM_SOURCE_LABEL', '')
