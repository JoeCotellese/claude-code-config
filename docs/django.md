# Opinionated Django Design Principles

These principles guide Django development across all projects. They are drawn from
*Fluent Python*, *Python Tricks*, *How to Tango with Django*, and hard-won project
experience. They complement `python.md` (tooling/style) with architectural philosophy.

## 1. DRY — Don't Repeat Yourself

Every piece of knowledge must have a single, unambiguous, authoritative representation
within a system. In practice:

- Use template inheritance (`{% extends %}`) instead of duplicating markup
- Use `{% url %}` and URL namespacing — never hardcode paths
- Extract shared constants to model class attributes (e.g., `NAME_MAX_LENGTH`)
- If you see similar code in two places, extract it to a service function or template tag

## 2. Follow Model-View-Template Faithfully

Django's architecture is opinionated by design. Respect the separation:

- **Models** handle data and business rules close to the data
- **Views** handle request/response orchestration — delegate mutations to services
- **Templates** handle presentation only — no business logic in templates
- **Services** handle complex business operations that span models or have side effects

Do not collapse these layers. A view should not contain SQL. A template should not
decide who to email. A model should not know about HTTP.

## 3. Favor Composition Over Deep Inheritance

Keep inheritance trees shallow. Prefer mixins and composition:

- Use abstract base models for shared fields (e.g., `UUIDModel`, `TimeStampedModel`)
- Prefer function-based views over class-based views for most cases
- When using CBVs, prefer shallow mixin composition over deep class hierarchies
- If a mixin does more than one thing, split it

## 4. Leverage First-Class Functions

Python's first-class functions make many classical design patterns invisible or simpler
(per Peter Norvig). Apply this in Django:

- Prefer function-based views — they are explicit and composable via decorators
- Use decorators for cross-cutting concerns (`@login_required`, `@require_http_methods`)
- Prefer simple callables over strategy/command class hierarchies
- Django uses this principle everywhere: view functions, signal handlers, middleware callables

## 5. Build Small, Reusable Apps

Each Django app should have a single, clear responsibility:

- An app should be describable in one short sentence
- Apps communicate through service functions and model relations, not by reaching
  into each other's internals
- Circular imports between apps signal a design problem — extract shared logic to `core`

## 6. Use Django's Machinery Before Rolling Your Own

Always check if Django provides it before building it:

- Forms and `ModelForm` for validation and cleaning
- The ORM for queries — avoid raw SQL unless there's a measured performance need
- The auth framework for authentication and permissions
- `slugify()`, `timezone.now()`, `F()` expressions, `get_or_create()`, etc.
- Management commands for CLI operations
- Signals sparingly — prefer explicit service calls over implicit signal handlers

## 7. Clean, Readable URLs

URL design is part of the user interface:

- Use slugs for human-readable URLs
- Use `app_name` namespacing to avoid URL name collisions
- Use `{% url %}` in templates and `reverse()` in Python — never hardcode paths
- RESTful resource naming: `/projects/<id>/subscribers/`, not `/get_subscribers/`

## 8. Test by Default

"Code without tests is broken by design." — Jacob Kaplan-Moss

- Write the test first (TDD): failing test, minimal code to pass, refactor
- Each test should focus on one small bit of functionality
- Tests must be independent — no test should depend on another test's state
- Use factories/fixtures for setup, not manual object construction scattered everywhere
- Test the contract (inputs/outputs), not the implementation

## 9. KISS and Fail-Fast

Start simple. Add complexity only when the current approach is proven insufficient:

- Start with public attributes — they can become properties later
- Raise errors early rather than silently passing bad data downstream

## 10. Communicate Intent Through Conventions

Mastering Python is as much about community conventions as language features:

- Follow Django's naming conventions (`verbose_name_plural`, `get_absolute_url`, etc.)
- Write descriptive test names that explain the expected behavior
- Use `Meta` classes for model configuration
- Service functions return consistent result types (e.g., `ServiceResult`)
- Document assumptions in comments; document *why*, not *what*

## Implementation References

For detailed patterns and code examples, see the python-architect skill references:
- Project structure: `skills/python-architect/references/django-structure.md`
- Model patterns: `skills/python-architect/references/model-patterns.md`
- HTMX patterns: `skills/python-architect/references/htmx-patterns.md`
- Testing patterns: `skills/python-architect/references/testing-patterns.md`
- Settings patterns: `skills/python-architect/references/settings-patterns.md`
