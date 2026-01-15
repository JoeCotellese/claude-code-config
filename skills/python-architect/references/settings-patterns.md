# Django Settings Patterns

## Table of Contents
- [Core Principles](#core-principles)
- [Settings File Structure](#settings-file-structure)
- [Base Settings](#base-settings)
- [Environment-Specific Settings](#environment-specific-settings)
- [Secrets Handling](#secrets-handling)
- [Requirements Structure](#requirements-structure)
- [Running with Settings](#running-with-settings)

## Core Principles

1. **All settings version-controlled** — No exceptions
2. **Secrets never in code** — Use environment variables
3. **DRY** — Inherit from base, don't copy-paste
4. **Explicit over implicit** — No `local_settings.py` imports

## Settings File Structure

```
config/
├── __init__.py
└── settings/
    ├── __init__.py      # Empty or smart default
    ├── base.py          # Shared settings for all environments
    ├── local.py         # Development (DEBUG=True)
    ├── test.py          # Test runner config
    ├── staging.py       # Semi-private production preview
    └── production.py    # Live server settings only
```

Each file imports from base:
```python
from .base import *  # noqa: F401, F403
```

## Base Settings

```python
# config/settings/base.py
"""
Base settings shared across all environments.
"""
from pathlib import Path
import os

from django.core.exceptions import ImproperlyConfigured


def get_env(var_name: str, default: str | None = None) -> str:
    """Get environment variable or raise if required and missing."""
    value = os.environ.get(var_name, default)
    if value is None:
        raise ImproperlyConfigured(f"Set the {var_name} environment variable")
    return value


# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Security - override in production.py
SECRET_KEY = get_env("DJANGO_SECRET_KEY", "dev-insecure-key-replace-in-production")
DEBUG = False
ALLOWED_HOSTS: list[str] = []

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "django_htmx",
]

LOCAL_APPS = [
    "project_name.core",
    "project_name.users",
    # Add your apps here
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "project_name" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database - PostgreSQL always
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": get_env("POSTGRES_DB", "project_db"),
        "USER": get_env("POSTGRES_USER", "postgres"),
        "PASSWORD": get_env("POSTGRES_PASSWORD", "postgres"),
        "HOST": get_env("POSTGRES_HOST", "localhost"),
        "PORT": get_env("POSTGRES_PORT", "5432"),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Custom user model
AUTH_USER_MODEL = "users.User"

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "project_name" / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
```

## Environment-Specific Settings

### local.py (Development)

```python
# config/settings/local.py
"""
Development settings - unsuitable for production.
"""
from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

# Debug toolbar
INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
INTERNAL_IPS = ["127.0.0.1"]

# Email to console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Simplified password validation for dev
AUTH_PASSWORD_VALIDATORS = []

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
```

### test.py (Testing)

```python
# config/settings/test.py
"""
Test runner settings.
"""
from .base import *  # noqa: F401, F403

DEBUG = False
SECRET_KEY = "test-secret-key-not-for-production"

# Use faster password hasher
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Use in-memory email
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Faster tests with in-memory cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Can use SQLite for faster tests if no Postgres-specific features
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": ":memory:",
#     }
# }
```

### production.py (Production)

```python
# config/settings/production.py
"""
Production settings - security hardened.
"""
from .base import *  # noqa: F401, F403

DEBUG = False
ALLOWED_HOSTS = get_env("DJANGO_ALLOWED_HOSTS").split(",")  # noqa: F405
SECRET_KEY = get_env("DJANGO_SECRET_KEY")  # noqa: F405

# Security
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Static files (use whitenoise or S3)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405

# Email - use real provider
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = get_env("EMAIL_HOST")  # noqa: F405
EMAIL_PORT = int(get_env("EMAIL_PORT", "587"))  # noqa: F405
EMAIL_USE_TLS = True
EMAIL_HOST_USER = get_env("EMAIL_HOST_USER")  # noqa: F405
EMAIL_HOST_PASSWORD = get_env("EMAIL_HOST_PASSWORD")  # noqa: F405

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
```

## Secrets Handling

### Option 1: Environment Variables (Preferred)

```bash
# .env (NEVER commit this)
DJANGO_SECRET_KEY=your-production-secret-key
DJANGO_ALLOWED_HOSTS=example.com,www.example.com
POSTGRES_DB=myapp
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
```

Load with direnv, docker-compose, or hosting provider.

### Option 2: JSON Secrets File

When env vars don't work (e.g., Apache):

```python
# config/settings/base.py
import json
from pathlib import Path

SECRETS_FILE = Path(__file__).resolve().parent.parent.parent / "secrets.json"

def get_secret(setting: str) -> str:
    with open(SECRETS_FILE) as f:
        secrets = json.load(f)
    try:
        return secrets[setting]
    except KeyError:
        raise ImproperlyConfigured(f"Set {setting} in secrets.json")
```

Add `secrets.json` to `.gitignore`.

## Requirements Structure

Mirror settings structure:

```
requirements/
├── base.txt         # Core dependencies
├── local.txt        # -r base.txt + dev tools
├── test.txt         # -r base.txt + test deps
└── production.txt   # -r base.txt (often just this)
```

**Or with UV (preferred)** - use pyproject.toml with optional dependencies:

```toml
[project.optional-dependencies]
dev = ["debug-toolbar", "ruff"]
test = ["pytest", "pytest-django", "coverage"]
```

## Running with Settings

```bash
# Development
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py runserver

# Or with manage.py flag
python manage.py runserver --settings=config.settings.local

# Testing
DJANGO_SETTINGS_MODULE=config.settings.test pytest

# Production (in gunicorn, etc.)
export DJANGO_SETTINGS_MODULE=config.settings.production
gunicorn config.wsgi:application
```

## Anti-Patterns to Avoid

❌ **Unversioned local_settings.py** - Use proper settings split

❌ **Hardcoded paths** - Use `Path(__file__).resolve()`

❌ **Secrets in code** - Use environment variables

❌ **`if DEBUG` scattered everywhere** - Use separate settings files

❌ **Copy-pasting between environments** - Inherit from base
