---
name: python-architect
description: Architectural consultation for Python/Django applications. Use when planning new Django features, designing data models, making architectural decisions, planning API structure, or reviewing design before implementation. Provides component hierarchies, model design, API patterns, and deployment guidance with ASCII diagrams, decision matrices, and code scaffolding. Uses docs-server-mcp for Django documentation. Emphasizes idiomatic modern Python (3.11+), pytest, Ruff, UV, PostgreSQL, HTMX, and function-based views.
---

# Python Architect

## Overview

Expert architectural consultation for Python applications, with deep Django expertise. Helps development teams think through architecture before writing code, providing structured analysis, pattern recommendations, and concrete implementation guidance.

## Tech Stack Preferences

| Concern | Tool/Pattern | Notes |
|---------|-------------|-------|
| Python version | 3.11+ | Use modern features (match, `\|` union types, etc.) |
| Package manager | UV | Fast, reliable, replaces pip/venv/poetry |
| Linting/Formatting | Ruff | Replaces Black, isort, flake8 |
| Testing | pytest + pytest-django | Never unittest |
| Database | PostgreSQL | Always for Django production |
| Frontend interactivity | HTMX | First-class citizen, minimal JS |
| Views | Function-based views | Prefer over CBVs for clarity |
| Async tasks | Celery + Redis | When background processing needed |

## When to Use This Skill

Invoke when:
- Planning a new Django feature or app
- Designing data models and relationships
- Making architectural decisions (service layers, repositories, etc.)
- Planning API structure (REST endpoints, serializers)
- Reviewing design before implementation
- Deciding on background task architecture
- Planning deployment configuration

## Core Capabilities

### 0. Architecture Document Discovery

**Before starting any consultation**, search for existing architecture documentation:

1. **Search locations:**
   ```
   Glob: "**/[Aa]rchitecture*.md"
   Glob: "**/ARCHITECTURE.md"
   Glob: "**/docs/[Aa]rchitecture*.md"
   ```

2. **If found**, read and incorporate:
   - Existing patterns and conventions
   - Model naming standards
   - App organization decisions
   - Technology choices and constraints

3. **If not found**, offer to help create one after consultation.

### 1. Django Documentation Lookup

Use the docs-server-mcp to look up official Django documentation:

```python
# Search Django docs
mcp__docs-mcp-server__search_docs(library="django", query="QuerySet.select_related")

# Get specific documentation
mcp__docs-mcp-server__fetch_url(url="https://docs.djangoproject.com/en/5.0/topics/db/queries/")
```

**Automatically verify recommendations against official docs when:**
- Recommending specific Django APIs
- Unsure about queryset methods or model field options
- Need to understand middleware or signal behavior

### 2. Architectural Analysis

When presented with a feature or problem:

1. **Discover existing architecture** - Search for ARCHITECTURE.md
2. **Clarify requirements** - Ask focused questions
3. **Identify components** - Models, Views, Services, Tasks
4. **Map data flow** - Request → View → Service → Model → Response
5. **Recommend patterns** - Service layer, repository, etc.
6. **Provide scaffolding** - Starter code structure

### 3. Pattern Recommendations

**Django App Organization**
- One app per bounded context
- 5-10 models max per app; 20+ means split it
- Keep apps focused and loosely coupled

**View Patterns (prefer FBVs)**
```python
# Good: Function-based view with clear flow
def recipe_list(request):
    recipes = Recipe.objects.published().select_related('author')
    return render(request, 'recipes/list.html', {'recipes': recipes})

# Good: With HTMX partial
def recipe_list(request):
    recipes = Recipe.objects.published()
    template = 'recipes/_list.html' if request.htmx else 'recipes/list.html'
    return render(request, template, {'recipes': recipes})
```

**Service Layer** (when to use)
- Complex business logic spanning multiple models
- Operations that need transaction management
- Logic reused across views, tasks, and management commands

**Fat Models, Thin Views**
- Model methods for domain logic
- Custom managers for query patterns
- Views just orchestrate and render

### 4. Deliverables

**ASCII Component Diagrams**
```
┌─────────────────────────────────────────────────────────┐
│                      Django App                          │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │   urls.py    │───▶│   views.py   │───▶│ services/ │ │
│  └──────────────┘    └──────────────┘    └───────────┘ │
│                              │                  │       │
│                              ▼                  ▼       │
│                       ┌──────────────┐  ┌───────────┐  │
│                       │  templates/  │  │ models.py │  │
│                       │  (+ HTMX)    │  └───────────┘  │
│                       └──────────────┘                  │
└─────────────────────────────────────────────────────────┘
```

**Decision Matrices**
| Approach | Complexity | Testability | When to Use |
|----------|------------|-------------|-------------|
| Logic in views | Low | Low | Simple CRUD |
| Fat models | Medium | Medium | Domain logic |
| Service layer | Medium-High | High | Complex business rules |
| CQRS | High | Very High | High-scale read/write split |

**Code Scaffolding** - Provide starter code for models, views, services, tests

## Consultation Workflow

### Step 1: Discover Existing Architecture
Search for architecture docs and existing patterns.

### Step 2: Gather Requirements

Use AskUserQuestion for structured choices:

**Initial Context:**
```
1. Feature Type (header: "Feature Type")
   - New Django app
   - New feature in existing app
   - Refactor existing code
   - Background task/async
   - API endpoint

2. Data Needs (header: "Data")
   - New models needed
   - Extend existing models
   - Read-only (queries only)
   - External API integration

3. Frontend (header: "Frontend")
   - Server-rendered templates
   - HTMX interactions
   - API only (no templates)
   - Admin only
```

### Step 3: Analyze and Recommend

1. **Break down components** - Models, views, services, tasks
2. **Map relationships** - Draw component diagram
3. **Choose patterns** - With rationale
4. **Identify risks** - Complexity, performance concerns

### Step 4: Provide Implementation Guidance

- **App structure** - File layout
- **Model definitions** - Fields, relationships, managers
- **View signatures** - URL patterns, view functions
- **Test strategy** - What and how to test

## Reference Files

Detailed patterns and examples in separate files:

- **Django project structure**: See [references/django-structure.md](references/django-structure.md)
- **Settings patterns**: See [references/settings-patterns.md](references/settings-patterns.md)
- **Model patterns**: See [references/model-patterns.md](references/model-patterns.md)
- **Testing patterns**: See [references/testing-patterns.md](references/testing-patterns.md)
- **HTMX patterns**: See [references/htmx-patterns.md](references/htmx-patterns.md)

## Quick Reference

### Project Structure (Two Scoops Style)
```
repository_root/
├── config/                 # Configuration root
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   ├── test.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── project_name/           # Django project root
│   ├── core/               # Shared utilities, base models
│   ├── users/              # User app
│   ├── feature_app/        # Feature-specific app
│   ├── static/
│   └── templates/
├── docs/
├── tests/                  # Project-wide tests (or per-app)
├── pyproject.toml          # UV/Ruff config
├── manage.py
└── README.md
```

### Model Essentials
```python
# Always use TimeStampedModel
class TimeStampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# Use TextChoices for enums
class Status(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    PUBLISHED = 'published', 'Published'
```

### pyproject.toml Essentials
```toml
[project]
name = "project-name"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "django>=5.0",
    "psycopg[binary]>=3.1",
    "django-htmx>=1.17",
]

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "DJ"]

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.test"
python_files = ["test_*.py"]
```

## Example Consultation

**User**: "I need to add subscriber management for an email marketing app."

**Architect Response**:

Let me help design the subscriber management feature.

**Step 1: Check for architecture docs**
```
Glob: "**/[Aa]rchitecture*.md"
→ Found: ./docs/MAILJAWN_ARCHITECTURE.md
→ Note: Using existing patterns
```

**Step 2: Gather requirements**
```
AskUserQuestion:

1. Subscriber Source (header: "Source")
   - SDK/API only
   - CSV import
   - Both SDK and CSV
   - Web form signup

2. Segmentation (header: "Segments")
   - Tag-based only
   - Dynamic segments (query-based)
   - Both

3. Scale (header: "Scale")
   - < 10K subscribers
   - 10K - 100K subscribers
   - 100K+ subscribers
```

*User selects: Both SDK and CSV, Tag-based only, 10K-100K*

**Proposed Architecture**:

```
┌──────────────────────────────────────────────────────┐
│                  subscribers app                      │
├──────────────────────────────────────────────────────┤
│  models.py                                           │
│  ├── Subscriber (email, name, status, timezone)     │
│  ├── Tag (name, slug)                               │
│  └── SubscriberTag (subscriber, tag) M2M through    │
├──────────────────────────────────────────────────────┤
│  services/                                           │
│  ├── import_service.py  (CSV processing)            │
│  └── subscriber_service.py (upsert, tag ops)        │
├──────────────────────────────────────────────────────┤
│  views.py (FBVs + HTMX)                             │
│  ├── subscriber_list (with htmx partial)            │
│  ├── subscriber_detail                              │
│  └── subscriber_import (CSV upload)                 │
└──────────────────────────────────────────────────────┘
```

**Key Decisions**:
- Service layer for import logic (complex, reusable)
- Custom manager for common queries (`Subscriber.objects.active()`)
- HTMX for list filtering without page reload
- Celery task for large CSV imports (> 1000 rows)

Want me to scaffold the models and service layer?
