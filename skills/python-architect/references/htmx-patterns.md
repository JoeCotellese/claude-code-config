# HTMX Patterns for Django

## Table of Contents
- [Core Concepts](#core-concepts)
- [Setup](#setup)
- [View Patterns](#view-patterns)
- [Template Patterns](#template-patterns)
- [Common Patterns](#common-patterns)
- [Form Handling](#form-handling)
- [Polling and Events](#polling-and-events)
- [Error Handling](#error-handling)

## Core Concepts

HTMX extends HTML with attributes that enable:
- **Partial page updates** — Replace only what changed
- **Server-driven UI** — Logic stays in Django views
- **Progressive enhancement** — Works without JS

Key attributes:
- `hx-get`, `hx-post`, `hx-put`, `hx-delete` — HTTP requests
- `hx-target` — What to replace with response
- `hx-swap` — How to swap content (innerHTML, outerHTML, etc.)
- `hx-trigger` — When to fire request

## Setup

### Install django-htmx

```bash
uv add django-htmx
```

### Configure

```python
# settings/base.py
INSTALLED_APPS = [
    ...
    "django_htmx",
]

MIDDLEWARE = [
    ...
    "django_htmx.middleware.HtmxMiddleware",
]
```

### Base Template

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}App{% endblock %}</title>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
</head>
<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>
    {% block content %}{% endblock %}
</body>
</html>
```

## View Patterns

### Partial vs Full Response

```python
# views.py
from django.shortcuts import render


def subscriber_list(request):
    """Return full page or partial based on request type."""
    subscribers = Subscriber.objects.active().select_related("app")

    # Choose template based on HTMX request
    if request.htmx:
        template = "subscribers/_list.html"
    else:
        template = "subscribers/list.html"

    return render(request, template, {"subscribers": subscribers})
```

### Using htmx.boosted

```python
def subscriber_list(request):
    """Support both HTMX and boosted navigation."""
    subscribers = Subscriber.objects.active()

    if request.htmx and not request.htmx.boosted:
        # Pure HTMX request - return partial
        template = "subscribers/_list.html"
    else:
        # Full page or boosted navigation
        template = "subscribers/list.html"

    return render(request, template, {"subscribers": subscribers})
```

### Response Headers

```python
from django_htmx.http import HttpResponseClientRedirect, trigger_client_event


def subscriber_create(request):
    if request.method == "POST":
        form = SubscriberForm(request.POST)
        if form.is_valid():
            subscriber = form.save()

            if request.htmx:
                # Trigger event for other components
                response = render(request, "subscribers/_row.html", {
                    "subscriber": subscriber
                })
                trigger_client_event(response, "subscriberCreated")
                return response
            else:
                return redirect("subscribers:list")

    return render(request, "subscribers/_form.html", {"form": form})
```

## Template Patterns

### Partial Templates

Use underscore prefix for partials (`_list.html`):

```
templates/subscribers/
├── list.html          # Full page
├── _list.html         # Just the list
├── _row.html          # Single subscriber row
├── _form.html         # Create/edit form
└── _search.html       # Search results
```

### Full Page Template

```html
<!-- templates/subscribers/list.html -->
{% extends "base.html" %}

{% block content %}
<div class="container">
    <h1>Subscribers</h1>

    <div id="subscriber-search">
        {% include "subscribers/_search.html" %}
    </div>

    <div id="subscriber-list">
        {% include "subscribers/_list.html" %}
    </div>
</div>
{% endblock %}
```

### Partial Template

```html
<!-- templates/subscribers/_list.html -->
<table>
    <thead>
        <tr>
            <th>Email</th>
            <th>Name</th>
            <th>Status</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody id="subscriber-rows">
        {% for subscriber in subscribers %}
            {% include "subscribers/_row.html" %}
        {% empty %}
            <tr>
                <td colspan="4">No subscribers yet.</td>
            </tr>
        {% endfor %}
    </tbody>
</table>
```

### Row Template (for adding/updating)

```html
<!-- templates/subscribers/_row.html -->
<tr id="subscriber-{{ subscriber.id }}">
    <td>{{ subscriber.email }}</td>
    <td>{{ subscriber.name }}</td>
    <td>
        <span class="badge badge-{{ subscriber.status }}">
            {{ subscriber.get_status_display }}
        </span>
    </td>
    <td>
        <button hx-get="{% url 'subscribers:edit' subscriber.id %}"
                hx-target="#modal"
                hx-swap="innerHTML">
            Edit
        </button>
        <button hx-delete="{% url 'subscribers:delete' subscriber.id %}"
                hx-target="#subscriber-{{ subscriber.id }}"
                hx-swap="outerHTML"
                hx-confirm="Delete this subscriber?">
            Delete
        </button>
    </td>
</tr>
```

## Common Patterns

### Infinite Scroll / Load More

```html
<!-- templates/subscribers/_list.html -->
{% for subscriber in page_obj %}
    {% include "subscribers/_row.html" %}
{% endfor %}

{% if page_obj.has_next %}
    <tr hx-get="{% url 'subscribers:list' %}?page={{ page_obj.next_page_number }}"
        hx-trigger="revealed"
        hx-swap="afterend"
        hx-select="tbody > tr">
        <td colspan="4">Loading more...</td>
    </tr>
{% endif %}
```

### Search with Debounce

```html
<!-- templates/subscribers/_search.html -->
<input type="search"
       name="q"
       placeholder="Search subscribers..."
       hx-get="{% url 'subscribers:list' %}"
       hx-target="#subscriber-list"
       hx-trigger="keyup changed delay:300ms"
       hx-indicator="#search-spinner">

<span id="search-spinner" class="htmx-indicator">
    Searching...
</span>
```

```python
def subscriber_list(request):
    subscribers = Subscriber.objects.active()

    query = request.GET.get("q")
    if query:
        subscribers = subscribers.filter(
            Q(email__icontains=query) | Q(name__icontains=query)
        )

    template = "subscribers/_list.html" if request.htmx else "subscribers/list.html"
    return render(request, template, {"subscribers": subscribers})
```

### Modal Dialog

```html
<!-- templates/base.html -->
<body>
    {% block content %}{% endblock %}

    <!-- Modal container -->
    <div id="modal" class="modal"></div>
</body>
```

```html
<!-- Trigger button -->
<button hx-get="{% url 'subscribers:create' %}"
        hx-target="#modal"
        hx-swap="innerHTML">
    Add Subscriber
</button>

<!-- templates/subscribers/_modal_form.html -->
<div class="modal-content">
    <h2>Add Subscriber</h2>
    <form hx-post="{% url 'subscribers:create' %}"
          hx-target="#subscriber-rows"
          hx-swap="afterbegin">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Save</button>
        <button type="button" onclick="closeModal()">Cancel</button>
    </form>
</div>
```

### Inline Editing

```html
<!-- templates/subscribers/_row.html -->
<tr id="subscriber-{{ subscriber.id }}" hx-target="this" hx-swap="outerHTML">
    <td>{{ subscriber.email }}</td>
    <td>
        <span hx-get="{% url 'subscribers:edit_name' subscriber.id %}"
              hx-trigger="click"
              class="editable">
            {{ subscriber.name|default:"Click to edit" }}
        </span>
    </td>
    <td>{{ subscriber.status }}</td>
</tr>

<!-- templates/subscribers/_edit_name.html -->
<tr id="subscriber-{{ subscriber.id }}" hx-target="this" hx-swap="outerHTML">
    <td>{{ subscriber.email }}</td>
    <td>
        <form hx-put="{% url 'subscribers:edit_name' subscriber.id %}">
            {% csrf_token %}
            <input type="text" name="name" value="{{ subscriber.name }}" autofocus>
            <button type="submit">Save</button>
        </form>
    </td>
    <td>{{ subscriber.status }}</td>
</tr>
```

### Tab Navigation

```html
<div class="tabs">
    <button hx-get="{% url 'subscribers:list' %}"
            hx-target="#tab-content"
            class="tab active">
        All
    </button>
    <button hx-get="{% url 'subscribers:list' %}?status=active"
            hx-target="#tab-content"
            class="tab">
        Active
    </button>
    <button hx-get="{% url 'subscribers:list' %}?status=unsubscribed"
            hx-target="#tab-content"
            class="tab">
        Unsubscribed
    </button>
</div>

<div id="tab-content">
    {% include "subscribers/_list.html" %}
</div>
```

## Form Handling

### Create with Validation Errors

```python
def subscriber_create(request):
    if request.method == "POST":
        form = SubscriberForm(request.POST)
        if form.is_valid():
            subscriber = form.save()
            if request.htmx:
                # Return new row to prepend to list
                return render(request, "subscribers/_row.html", {
                    "subscriber": subscriber
                })
            return redirect("subscribers:list")
    else:
        form = SubscriberForm()

    template = "subscribers/_form.html" if request.htmx else "subscribers/create.html"
    return render(request, template, {"form": form})
```

```html
<!-- templates/subscribers/_form.html -->
<form hx-post="{% url 'subscribers:create' %}"
      hx-target="#subscriber-rows"
      hx-swap="afterbegin"
      hx-on::after-request="if(event.detail.successful) this.reset()">
    {% csrf_token %}

    <div class="field {% if form.email.errors %}has-error{% endif %}">
        <label for="{{ form.email.id_for_label }}">Email</label>
        {{ form.email }}
        {% for error in form.email.errors %}
            <span class="error">{{ error }}</span>
        {% endfor %}
    </div>

    <div class="field">
        <label for="{{ form.name.id_for_label }}">Name</label>
        {{ form.name }}
    </div>

    <button type="submit">Add Subscriber</button>
</form>
```

### Update in Place

```python
def subscriber_update(request, pk):
    subscriber = get_object_or_404(Subscriber, pk=pk)

    if request.method == "POST":
        form = SubscriberForm(request.POST, instance=subscriber)
        if form.is_valid():
            subscriber = form.save()
            if request.htmx:
                return render(request, "subscribers/_row.html", {
                    "subscriber": subscriber
                })
            return redirect("subscribers:list")
    else:
        form = SubscriberForm(instance=subscriber)

    return render(request, "subscribers/_form.html", {
        "form": form,
        "subscriber": subscriber,
    })
```

## Polling and Events

### Polling for Updates

```html
<!-- Poll for new subscribers every 30 seconds -->
<div hx-get="{% url 'subscribers:count' %}"
     hx-trigger="every 30s"
     hx-swap="innerHTML">
    {{ subscriber_count }} subscribers
</div>
```

### Server-Sent Events (SSE)

```python
# views.py
from django.http import StreamingHttpResponse


def campaign_progress(request, pk):
    """Stream campaign send progress."""
    campaign = get_object_or_404(Campaign, pk=pk)

    def event_stream():
        while not campaign.is_complete:
            campaign.refresh_from_db()
            yield f"data: {campaign.progress_percent}\n\n"
            time.sleep(1)
        yield f"data: 100\n\n"

    return StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream",
    )
```

```html
<div hx-ext="sse"
     sse-connect="{% url 'campaigns:progress' campaign.id %}"
     sse-swap="message">
    0%
</div>
```

### Custom Events

```python
from django_htmx.http import trigger_client_event


def subscriber_create(request):
    # ... create subscriber ...

    response = render(request, "subscribers/_row.html", {"subscriber": subscriber})

    # Trigger event that other components can listen to
    trigger_client_event(response, "subscriberCreated", {"id": subscriber.id})

    return response
```

```html
<!-- Listen for event and refresh count -->
<div hx-get="{% url 'subscribers:count' %}"
     hx-trigger="subscriberCreated from:body"
     hx-swap="innerHTML">
    {{ subscriber_count }}
</div>
```

## Error Handling

### Handle Errors Gracefully

```html
<form hx-post="{% url 'subscribers:create' %}"
      hx-target="#subscriber-rows"
      hx-swap="afterbegin"
      hx-target-error="#form-errors">
    {% csrf_token %}
    {{ form.as_p }}
    <div id="form-errors"></div>
    <button type="submit">Save</button>
</form>
```

```python
from django.http import HttpResponse


def subscriber_create(request):
    if request.method == "POST":
        form = SubscriberForm(request.POST)
        if form.is_valid():
            subscriber = form.save()
            return render(request, "subscribers/_row.html", {
                "subscriber": subscriber
            })
        else:
            # Return 422 with form errors
            response = render(request, "subscribers/_form_errors.html", {
                "form": form
            })
            response.status_code = 422
            return response
```

### Loading States

```html
<button hx-post="{% url 'campaigns:send' campaign.id %}"
        hx-indicator="#send-spinner"
        class="button">
    <span id="send-spinner" class="htmx-indicator">Sending...</span>
    <span class="htmx-show-not-active">Send Campaign</span>
</button>
```

```css
/* Show/hide based on request state */
.htmx-indicator {
    display: none;
}
.htmx-request .htmx-indicator {
    display: inline;
}
.htmx-request .htmx-show-not-active {
    display: none;
}
```
