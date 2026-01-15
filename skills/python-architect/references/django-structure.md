# Django Project Structure

## Table of Contents
- [Three-Tier Layout](#three-tier-layout)
- [Repository Root](#repository-root)
- [Configuration Root](#configuration-root)
- [Django Project Root](#django-project-root)
- [App Structure](#app-structure)
- [Complete Example](#complete-example)

## Three-Tier Layout

Based on Two Scoops of Django, use a three-tier structure:

```
<repository_root>/
├── <configuration_root>/    # Settings, URLs, WSGI
├── <django_project_root>/   # Apps, templates, static
└── [supporting files]       # docs, tests, pyproject.toml
```

## Repository Root

The absolute root containing everything:

```
repository_root/
├── config/                  # Configuration root
├── project_name/            # Django project root
├── docs/                    # Documentation
├── tests/                   # Project-wide tests (optional)
├── .gitignore
├── .env.example             # Environment template (never .env!)
├── pyproject.toml           # UV/Ruff/pytest config
├── manage.py
├── README.md
└── docker-compose.yml       # If using Docker
```

### Key Files

**pyproject.toml** (UV + Ruff + pytest)
```toml
[project]
name = "project-name"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "django>=5.0",
    "psycopg[binary]>=3.1",
    "django-htmx>=1.17",
    "django-environ>=0.11",
    "gunicorn>=21.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-django>=4.7",
    "pytest-cov>=4.1",
    "ruff>=0.1",
    "django-debug-toolbar>=4.2",
]

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "DJ", "C90"]
ignore = ["E501"]  # Line length handled separately

[tool.ruff.lint.isort]
known-first-party = ["project_name"]

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.test"
python_files = ["test_*.py"]
addopts = "-v --tb=short"
```

**.gitignore essentials**
```
# Python
__pycache__/
*.py[cod]
.venv/
*.egg-info/

# Django
*.log
local_settings.py
db.sqlite3
/media/
/staticfiles/

# Environment
.env
.envrc
secrets.json

# IDE
.idea/
.vscode/
*.swp
```

## Configuration Root

Contains settings, URL config, and WSGI/ASGI:

```
config/
├── __init__.py
├── settings/
│   ├── __init__.py
│   ├── base.py          # Shared settings
│   ├── local.py         # Development
│   ├── test.py          # Test runner
│   ├── staging.py       # Staging server
│   └── production.py    # Production
├── urls.py              # Root URL configuration
├── wsgi.py
└── asgi.py
```

## Django Project Root

Contains all Django apps and shared resources:

```
project_name/
├── __init__.py
├── core/                # Shared utilities
│   ├── __init__.py
│   ├── models.py        # TimeStampedModel, etc.
│   ├── mixins.py        # View mixins
│   └── utils.py         # Shared utilities
├── users/               # Custom user app
│   ├── __init__.py
│   ├── admin.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── tests/
├── feature_app/         # Feature-specific app
│   └── ...
├── static/              # Project static files
│   ├── css/
│   ├── js/
│   └── img/
└── templates/           # Project templates
    ├── base.html
    ├── _partials/       # HTMX partials
    └── feature_app/
```

## App Structure

Standard app layout:

```
feature_app/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── views.py
├── urls.py
├── forms.py             # If using forms
├── services/            # Business logic (when needed)
│   ├── __init__.py
│   └── feature_service.py
├── managers.py          # Custom managers (if many)
├── signals.py           # Signal handlers (if any)
├── tasks.py             # Celery tasks (if any)
├── templates/
│   └── feature_app/
│       ├── list.html
│       ├── detail.html
│       └── _partials/   # HTMX partials
│           └── _list.html
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_views.py
    └── test_services.py
```

## Complete Example

MailJawn email marketing platform:

```
mailjawn/
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   ├── test.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py        # Celery config
├── mailjawn/            # Django project root
│   ├── core/
│   │   ├── models.py    # TimeStampedModel
│   │   └── utils.py
│   ├── accounts/        # User accounts & auth
│   │   ├── models.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── apps/            # Developer apps (multi-tenant)
│   │   ├── models.py    # App model
│   │   └── ...
│   ├── subscribers/     # Subscriber management
│   │   ├── models.py    # Subscriber, Tag
│   │   ├── views.py
│   │   ├── services/
│   │   │   ├── import_service.py
│   │   │   └── subscriber_service.py
│   │   └── tasks.py     # CSV import task
│   ├── campaigns/       # Email campaigns
│   │   ├── models.py    # Campaign, Draft
│   │   ├── views.py
│   │   └── services/
│   │       └── send_service.py
│   ├── api/             # REST API (DRF)
│   │   ├── v1/
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   └── urls.py
│   │   └── urls.py
│   ├── static/
│   └── templates/
├── docs/
│   ├── ARCHITECTURE.md
│   └── PRODUCT_REQUIREMENTS.md
├── pyproject.toml
├── manage.py
└── README.md
```

## Anti-Patterns to Avoid

❌ **Don't include virtualenv in repo** - Use UV, keep `.venv/` in `.gitignore`

❌ **Don't use single settings.py** - Split into base/local/production

❌ **Don't hardcode paths** - Use `Path(__file__).resolve().parent`

❌ **Don't put business logic in views** - Use services or fat models

❌ **Don't create God apps** - Split at 20+ models
