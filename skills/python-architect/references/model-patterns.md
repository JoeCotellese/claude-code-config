# Django Model Patterns

## Table of Contents
- [Core Principles](#core-principles)
- [TimeStampedModel](#timestampedmodel)
- [Model Inheritance](#model-inheritance)
- [Field Patterns](#field-patterns)
- [Choices with Enums](#choices-with-enums)
- [Custom Managers](#custom-managers)
- [Fat Models](#fat-models)
- [Migrations](#migrations)

## Core Principles

1. **5-10 models per app** — 20+ means the app does too much
2. **Always version control migrations** — Treat as code
3. **Start normalized** — Denormalize only when caching fails
4. **Avoid GenericForeignKey** — Use explicit ForeignKeys

## TimeStampedModel

Use for every model (via django-model-utils or custom):

```python
# core/models.py
from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base with created/modified timestamps."""

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # Critical: no table created


# Usage
class Subscriber(TimeStampedModel):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True)
    # created and modified are inherited
```

## Model Inheritance

| Type | Creates Tables | Use When |
|------|---------------|----------|
| Abstract base class | Child only ✓ | Sharing common fields |
| Proxy model | Original only | Different Python behavior, same data |
| Multi-table inheritance | Parent + Child ✗ | **NEVER USE** |

### Abstract Base Class (use this)

```python
class Publishable(models.Model):
    """Mixin for content that can be published."""

    published_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def publish(self):
        from django.utils import timezone
        self.is_published = True
        self.published_at = timezone.now()
        self.save(update_fields=["is_published", "published_at"])


class Article(TimeStampedModel, Publishable):
    title = models.CharField(max_length=200)
    body = models.TextField()
```

### Proxy Model

```python
class Campaign(TimeStampedModel):
    status = models.CharField(max_length=20)
    # ...


class DraftCampaign(Campaign):
    """Proxy for draft campaigns with specialized methods."""

    class Meta:
        proxy = True

    def publish(self):
        self.status = "published"
        self.save()
```

## Field Patterns

### Null and Blank Quick Reference

| Field Type | null=True | blank=True |
|------------|-----------|------------|
| CharField, TextField | Only if `unique=True` + `blank=True` | OK for empty form values |
| IntegerField, DecimalField | OK for NULL in DB | OK if also `null=True` |
| DateTimeField | OK for NULL in DB | OK if also `null=True` or using `auto_now` |
| ForeignKey, OneToOneField | OK for NULL in DB | OK if also `null=True` |
| ManyToManyField | No effect | OK for empty selection |
| BooleanField | Don't do it | OK |
| JSONField | OK | OK |

### Common Field Patterns

```python
class Subscriber(TimeStampedModel):
    # Email - required, unique
    email = models.EmailField(unique=True)

    # Name - optional
    name = models.CharField(max_length=255, blank=True)

    # Status with choices
    status = models.CharField(
        max_length=20,
        choices=SubscriberStatus.choices,
        default=SubscriberStatus.ACTIVE,
        db_index=True,  # Index for filtering
    )

    # Timezone - optional, IANA format
    timezone = models.CharField(max_length=50, blank=True)

    # Last seen - nullable datetime
    last_seen = models.DateTimeField(null=True, blank=True)

    # Custom fields - flexible JSON
    custom_fields = models.JSONField(default=dict, blank=True)

    # Foreign key - required
    app = models.ForeignKey(
        "apps.App",
        on_delete=models.CASCADE,
        related_name="subscribers",
    )

    # Foreign key - optional
    imported_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["email", "app"],
                name="unique_subscriber_per_app",
            )
        ]
```

## Choices with Enums

Use TextChoices or IntegerChoices:

```python
from django.db import models


class SubscriberStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    UNSUBSCRIBED = "unsubscribed", "Unsubscribed"
    BOUNCED = "bounced", "Bounced"
    COMPLAINED = "complained", "Complained"


class CampaignType(models.TextChoices):
    EMAIL = "email", "Email"
    SMS = "sms", "SMS"
    PUSH = "push", "Push Notification"


class Subscriber(TimeStampedModel):
    status = models.CharField(
        max_length=20,
        choices=SubscriberStatus.choices,
        default=SubscriberStatus.ACTIVE,
    )


# Usage in queries
Subscriber.objects.filter(status=SubscriberStatus.ACTIVE)

# Usage in views
if subscriber.status == SubscriberStatus.BOUNCED:
    ...
```

## Custom Managers

**Always define `objects = models.Manager()` first**, then custom managers:

```python
from django.db import models
from django.utils import timezone


class SubscriberQuerySet(models.QuerySet):
    """Chainable query methods."""

    def active(self):
        return self.filter(status=SubscriberStatus.ACTIVE)

    def with_tag(self, tag_name: str):
        return self.filter(tags__name=tag_name)

    def inactive_since(self, days: int):
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.filter(last_seen__lt=cutoff)


class SubscriberManager(models.Manager):
    """Manager with custom QuerySet."""

    def get_queryset(self):
        return SubscriberQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def with_tag(self, tag_name: str):
        return self.get_queryset().with_tag(tag_name)


class Subscriber(TimeStampedModel):
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=SubscriberStatus.choices)
    last_seen = models.DateTimeField(null=True, blank=True)

    objects = SubscriberManager()  # Custom manager


# Usage
Subscriber.objects.active()
Subscriber.objects.active().with_tag("pro_user")
Subscriber.objects.active().inactive_since(30)
```

## Fat Models

Put logic in models for reuse across views:

```python
class Campaign(TimeStampedModel):
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=CampaignStatus.choices)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    # Properties
    @property
    def is_scheduled(self) -> bool:
        return self.status == CampaignStatus.SCHEDULED and self.scheduled_at

    @property
    def can_send(self) -> bool:
        return self.status in (CampaignStatus.DRAFT, CampaignStatus.SCHEDULED)

    # Domain methods
    def schedule(self, send_at: datetime) -> None:
        """Schedule campaign for future send."""
        if not self.can_send:
            raise ValueError(f"Cannot schedule campaign in status {self.status}")
        self.scheduled_at = send_at
        self.status = CampaignStatus.SCHEDULED
        self.save(update_fields=["scheduled_at", "status", "modified"])

    def mark_sent(self) -> None:
        """Mark campaign as sent."""
        self.status = CampaignStatus.SENT
        self.sent_at = timezone.now()
        self.save(update_fields=["status", "sent_at", "modified"])

    # Class methods
    @classmethod
    def create_draft(cls, app: App, name: str, **kwargs) -> "Campaign":
        """Factory method for creating draft campaigns."""
        return cls.objects.create(
            app=app,
            name=name,
            status=CampaignStatus.DRAFT,
            **kwargs,
        )
```

### When to Extract to Services

Fat models should stay under ~500 lines. Extract to services when:

- Logic spans multiple models
- Complex transactions needed
- Reused in views, tasks, and management commands

```python
# subscribers/services/import_service.py
from django.db import transaction

from ..models import Subscriber, Tag


class ImportService:
    """Handle CSV import logic."""

    def __init__(self, app: App, user: User):
        self.app = app
        self.user = user

    @transaction.atomic
    def import_csv(self, rows: list[dict]) -> ImportResult:
        created = 0
        updated = 0
        errors = []

        for row in rows:
            try:
                subscriber, was_created = self._upsert_subscriber(row)
                if was_created:
                    created += 1
                else:
                    updated += 1
            except ValidationError as e:
                errors.append({"row": row, "error": str(e)})

        return ImportResult(created=created, updated=updated, errors=errors)

    def _upsert_subscriber(self, row: dict) -> tuple[Subscriber, bool]:
        # Implementation
        ...
```

## Migrations

### Best Practices

1. **Run makemigrations immediately** when creating/modifying models
2. **Review generated code** before running, especially for complex changes
3. **Use `sqlmigrate`** to preview SQL
4. **Always back up data** before migrating production
5. **Test on staging** with production-sized data

### Useful Commands

```bash
# Create migration
python manage.py makemigrations app_name

# Preview SQL
python manage.py sqlmigrate app_name 0001

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

### Data Migrations

```python
# migrations/0002_populate_slugs.py
from django.db import migrations


def populate_slugs(apps, schema_editor):
    Tag = apps.get_model("subscribers", "Tag")
    for tag in Tag.objects.filter(slug=""):
        tag.slug = slugify(tag.name)
        tag.save(update_fields=["slug"])


def reverse_slugs(apps, schema_editor):
    pass  # Reversing is optional but good practice


class Migration(migrations.Migration):
    dependencies = [
        ("subscribers", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(populate_slugs, reverse_slugs),
    ]
```

## Anti-Patterns to Avoid

❌ **Multi-table inheritance** — Causes joins, performance issues

❌ **GenericForeignKey for primary data** — Loses indexing, referential integrity

❌ **BinaryField for file storage** — Use FileField or external storage

❌ **Denormalizing before caching** — Cache first

❌ **God models (1000+ lines)** — Extract to services/behaviors
