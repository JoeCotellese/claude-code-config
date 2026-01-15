# Django Testing Patterns

## Table of Contents
- [Core Principles](#core-principles)
- [Setup with pytest](#setup-with-pytest)
- [Test Organization](#test-organization)
- [Fixtures](#fixtures)
- [Model Tests](#model-tests)
- [View Tests](#view-tests)
- [Service Tests](#service-tests)
- [API Tests](#api-tests)
- [Test Utilities](#test-utilities)

## Core Principles

1. **Always use pytest** — Never unittest
2. **Use pytest-django** — Django integration
3. **Fixtures over setUp** — More flexible, reusable
4. **Test behavior, not implementation** — Focus on outcomes
5. **Fast tests** — Use in-memory cache, faster hasher

## Setup with pytest

### pyproject.toml Configuration

```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.test"
python_files = ["test_*.py"]
addopts = "-v --tb=short --reuse-db"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
]

[tool.coverage.run]
source = ["project_name"]
omit = ["*/migrations/*", "*/tests/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
```

### Test Settings (config/settings/test.py)

```python
from .base import *  # noqa

DEBUG = False
SECRET_KEY = "test-secret-key-not-for-production"

# Faster password hashing
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# In-memory email
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# In-memory cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Disable logging noise
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {"null": {"class": "logging.NullHandler"}},
    "root": {"handlers": ["null"]},
}
```

## Test Organization

```
project_name/
├── subscribers/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py      # App-specific fixtures
│   │   ├── test_models.py
│   │   ├── test_views.py
│   │   ├── test_services.py
│   │   └── factories.py     # Factory Boy factories
│   └── ...
└── conftest.py              # Project-wide fixtures
```

## Fixtures

### Project-wide Fixtures (conftest.py)

```python
# conftest.py
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def user(db):
    """Create a regular user."""
    return User.objects.create_user(
        email="user@example.com",
        password="testpass123",
    )


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    return User.objects.create_superuser(
        email="admin@example.com",
        password="adminpass123",
    )


@pytest.fixture
def authenticated_client(client, user):
    """Client with logged-in user."""
    client.force_login(user)
    return client


@pytest.fixture
def api_client():
    """DRF API client."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_api_client(api_client, user):
    """Authenticated DRF client."""
    api_client.force_authenticate(user=user)
    return api_client
```

### App-specific Fixtures

```python
# subscribers/tests/conftest.py
import pytest
from subscribers.models import Subscriber, Tag


@pytest.fixture
def app(db, user):
    """Create a test app."""
    from apps.models import App
    return App.objects.create(
        name="Test App",
        owner=user,
    )


@pytest.fixture
def subscriber(db, app):
    """Create a test subscriber."""
    return Subscriber.objects.create(
        app=app,
        email="subscriber@example.com",
        name="Test Subscriber",
    )


@pytest.fixture
def tag(db, app):
    """Create a test tag."""
    return Tag.objects.create(
        app=app,
        name="test-tag",
        slug="test-tag",
    )


@pytest.fixture
def subscribers_batch(db, app):
    """Create multiple subscribers for batch tests."""
    return Subscriber.objects.bulk_create([
        Subscriber(app=app, email=f"user{i}@example.com")
        for i in range(10)
    ])
```

### Factory Boy (for Complex Data)

```python
# subscribers/tests/factories.py
import factory
from factory.django import DjangoModelFactory

from subscribers.models import Subscriber, Tag


class TagFactory(DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Sequence(lambda n: f"tag-{n}")
    slug = factory.LazyAttribute(lambda o: o.name)


class SubscriberFactory(DjangoModelFactory):
    class Meta:
        model = Subscriber

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    name = factory.Faker("name")
    status = Subscriber.Status.ACTIVE

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        for tag in extracted:
            self.tags.add(tag)
```

## Model Tests

```python
# subscribers/tests/test_models.py
import pytest
from django.utils import timezone

from subscribers.models import Subscriber, SubscriberStatus


class TestSubscriber:
    """Tests for Subscriber model."""

    def test_create_subscriber(self, app):
        """Can create subscriber with required fields."""
        subscriber = Subscriber.objects.create(
            app=app,
            email="test@example.com",
        )

        assert subscriber.id is not None
        assert subscriber.email == "test@example.com"
        assert subscriber.status == SubscriberStatus.ACTIVE
        assert subscriber.created is not None

    def test_email_unique_per_app(self, subscriber):
        """Email must be unique within an app."""
        with pytest.raises(Exception):  # IntegrityError
            Subscriber.objects.create(
                app=subscriber.app,
                email=subscriber.email,
            )

    def test_update_last_seen(self, subscriber):
        """update_last_seen sets timestamp."""
        assert subscriber.last_seen is None

        subscriber.update_last_seen()

        subscriber.refresh_from_db()
        assert subscriber.last_seen is not None

    def test_active_manager(self, app):
        """Manager.active() filters to active subscribers."""
        active = Subscriber.objects.create(
            app=app,
            email="active@example.com",
            status=SubscriberStatus.ACTIVE,
        )
        Subscriber.objects.create(
            app=app,
            email="unsubscribed@example.com",
            status=SubscriberStatus.UNSUBSCRIBED,
        )

        result = Subscriber.objects.active()

        assert list(result) == [active]
```

## View Tests

```python
# subscribers/tests/test_views.py
import pytest
from django.urls import reverse


class TestSubscriberListView:
    """Tests for subscriber_list view."""

    def test_requires_login(self, client, app):
        """Unauthenticated users are redirected."""
        url = reverse("subscribers:list", args=[app.id])

        response = client.get(url)

        assert response.status_code == 302
        assert "/login/" in response.url

    def test_shows_subscribers(self, authenticated_client, subscriber):
        """Authenticated users see subscriber list."""
        url = reverse("subscribers:list", args=[subscriber.app.id])

        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert subscriber.email in response.content.decode()

    def test_htmx_returns_partial(self, authenticated_client, subscriber):
        """HTMX request returns partial template."""
        url = reverse("subscribers:list", args=[subscriber.app.id])

        response = authenticated_client.get(
            url,
            HTTP_HX_REQUEST="true",
        )

        assert response.status_code == 200
        # Partial should not include full page wrapper
        assert "<html>" not in response.content.decode()


class TestSubscriberCreateView:
    """Tests for subscriber creation."""

    def test_create_subscriber(self, authenticated_client, app):
        """Can create subscriber via form."""
        url = reverse("subscribers:create", args=[app.id])
        data = {
            "email": "new@example.com",
            "name": "New User",
        }

        response = authenticated_client.post(url, data)

        assert response.status_code == 302  # Redirect on success
        assert Subscriber.objects.filter(email="new@example.com").exists()

    def test_invalid_email_shows_error(self, authenticated_client, app):
        """Invalid email shows form error."""
        url = reverse("subscribers:create", args=[app.id])
        data = {"email": "not-an-email"}

        response = authenticated_client.post(url, data)

        assert response.status_code == 200  # Re-render form
        assert "Enter a valid email" in response.content.decode()
```

## Service Tests

```python
# subscribers/tests/test_services.py
import pytest
from unittest.mock import patch

from subscribers.services.import_service import ImportService


class TestImportService:
    """Tests for CSV import service."""

    def test_import_creates_subscribers(self, app, user):
        """Importing CSV creates subscribers."""
        service = ImportService(app=app, user=user)
        rows = [
            {"email": "one@example.com", "name": "One"},
            {"email": "two@example.com", "name": "Two"},
        ]

        result = service.import_csv(rows)

        assert result.created == 2
        assert result.updated == 0
        assert Subscriber.objects.count() == 2

    def test_import_updates_existing(self, subscriber):
        """Importing existing email updates subscriber."""
        service = ImportService(app=subscriber.app, user=subscriber.app.owner)
        rows = [{"email": subscriber.email, "name": "Updated Name"}]

        result = service.import_csv(rows)

        assert result.created == 0
        assert result.updated == 1
        subscriber.refresh_from_db()
        assert subscriber.name == "Updated Name"

    def test_import_skips_invalid_emails(self, app, user):
        """Invalid emails are collected as errors."""
        service = ImportService(app=app, user=user)
        rows = [
            {"email": "valid@example.com"},
            {"email": "not-valid"},
        ]

        result = service.import_csv(rows)

        assert result.created == 1
        assert len(result.errors) == 1
        assert "not-valid" in str(result.errors[0])

    @pytest.mark.slow
    def test_large_import_performance(self, app, user):
        """Large imports complete in reasonable time."""
        service = ImportService(app=app, user=user)
        rows = [{"email": f"user{i}@example.com"} for i in range(1000)]

        result = service.import_csv(rows)

        assert result.created == 1000
```

## API Tests

```python
# api/tests/test_subscribers.py
import pytest
from django.urls import reverse


class TestSubscriberAPI:
    """Tests for subscriber API endpoints."""

    def test_list_subscribers(self, authenticated_api_client, subscriber):
        """GET /api/v1/subscribers/ returns subscriber list."""
        url = reverse("api-v1:subscriber-list")

        response = authenticated_api_client.get(url)

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["email"] == subscriber.email

    def test_create_subscriber(self, authenticated_api_client, app):
        """POST /api/v1/subscribers/ creates subscriber."""
        url = reverse("api-v1:subscriber-list")
        data = {
            "app": app.id,
            "email": "api@example.com",
            "name": "API User",
        }

        response = authenticated_api_client.post(url, data)

        assert response.status_code == 201
        assert response.data["email"] == "api@example.com"

    def test_unauthenticated_rejected(self, api_client):
        """Unauthenticated requests are rejected."""
        url = reverse("api-v1:subscriber-list")

        response = api_client.get(url)

        assert response.status_code == 401
```

## Test Utilities

### Assertions

```python
# conftest.py or tests/utils.py

def assert_redirects_to_login(response):
    """Assert response redirects to login."""
    assert response.status_code == 302
    assert "/login/" in response.url


def assert_form_error(response, field, message):
    """Assert form has specific error."""
    assert response.status_code == 200
    errors = response.context["form"].errors
    assert field in errors
    assert message in str(errors[field])
```

### Test Markers

```python
# Run only fast tests
# pytest -m "not slow"

@pytest.mark.slow
def test_large_import():
    ...

@pytest.mark.integration
def test_external_api():
    ...
```

### Mocking External Services

```python
from unittest.mock import patch


class TestEmailSending:
    @patch("campaigns.services.send_service.ses_client")
    def test_send_campaign(self, mock_ses, campaign):
        """Campaign sends via SES."""
        mock_ses.send_email.return_value = {"MessageId": "123"}

        result = send_campaign(campaign)

        assert result.success
        mock_ses.send_email.assert_called_once()
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=project_name --cov-report=html

# Run specific test file
pytest subscribers/tests/test_models.py

# Run specific test class
pytest subscribers/tests/test_models.py::TestSubscriber

# Run specific test
pytest subscribers/tests/test_models.py::TestSubscriber::test_create_subscriber

# Run excluding slow tests
pytest -m "not slow"

# Run in parallel
pytest -n auto
```
