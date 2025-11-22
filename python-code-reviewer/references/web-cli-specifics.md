# Web App and CLI Tool Specific Patterns

## Web Application Patterns

### Flask/FastAPI Best Practices

#### 1. Route Organization

```python
# Bad: All routes in one file
# app.py (2000+ lines)
@app.route("/")
def index(): pass

@app.route("/users")
def list_users(): pass

@app.route("/products")
def list_products(): pass
# ... 50+ more routes

# Good: Blueprint/Router organization
# app.py
from flask import Flask
from routes.users import users_bp
from routes.products import products_bp

app = Flask(__name__)
app.register_blueprint(users_bp, url_prefix="/users")
app.register_blueprint(products_bp, url_prefix="/products")

# routes/users.py
from flask import Blueprint

users_bp = Blueprint("users", __name__)

@users_bp.route("/")
def list_users():
    pass

@users_bp.route("/<int:user_id>")
def get_user(user_id):
    pass
```

#### 2. Request Validation

```python
# Bad: Manual validation scattered throughout
@app.route("/users", methods=["POST"])
def create_user():
    data = request.json
    if not data:
        return {"error": "No data"}, 400
    if "email" not in data:
        return {"error": "Email required"}, 400
    if "@" not in data["email"]:
        return {"error": "Invalid email"}, 400
    # ...

# Good: Use Pydantic for validation (FastAPI/Flask)
from pydantic import BaseModel, EmailStr, validator

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @validator("username")
    def username_valid(cls, v):
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        return v

    @validator("password")
    def password_valid(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

# FastAPI
@app.post("/users")
async def create_user(user: UserCreate):
    # user is validated automatically
    return {"username": user.username}

# Flask with pydantic
@app.route("/users", methods=["POST"])
def create_user():
    try:
        user = UserCreate(**request.json)
    except ValidationError as e:
        return {"errors": e.errors()}, 400
    # ...
```

#### 3. Dependency Injection

```python
# Bad: Global state and hard dependencies
db = Database()
cache = Redis()

@app.route("/users/<int:user_id>")
def get_user(user_id):
    cached = cache.get(f"user:{user_id}")
    if cached:
        return cached
    user = db.query(User).get(user_id)
    cache.set(f"user:{user_id}", user)
    return user

# Good: Dependency injection (FastAPI)
from fastapi import Depends

def get_db():
    db = Database()
    try:
        yield db
    finally:
        db.close()

def get_cache():
    return Redis()

@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    db: Database = Depends(get_db),
    cache: Redis = Depends(get_cache)
):
    cached = cache.get(f"user:{user_id}")
    if cached:
        return cached
    user = db.query(User).get(user_id)
    cache.set(f"user:{user_id}", user)
    return user
```

#### 4. Error Handling

```python
# Bad: Inconsistent error responses
@app.route("/users/<int:user_id>")
def get_user(user_id):
    user = db.get(user_id)
    if not user:
        return "Not found", 404
    return user

@app.route("/products/<int:product_id>")
def get_product(product_id):
    product = db.get(product_id)
    if not product:
        return {"error": "Product not found"}, 404
    return product

# Good: Consistent error handling
from werkzeug.exceptions import NotFound

class APIError(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code

@app.errorhandler(APIError)
def handle_api_error(error):
    return {"error": error.message}, error.status_code

@app.errorhandler(404)
def handle_not_found(error):
    return {"error": "Resource not found"}, 404

@app.route("/users/<int:user_id>")
def get_user(user_id):
    user = db.get(user_id)
    if not user:
        raise NotFound("User not found")
    return user
```

#### 5. Database Session Management

```python
# Bad: Session management in routes
@app.route("/users", methods=["POST"])
def create_user():
    session = Session()
    user = User(**request.json)
    session.add(user)
    session.commit()
    session.close()
    return user

# Good: Context manager or middleware
from contextlib import contextmanager

@contextmanager
def get_db_session():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

@app.route("/users", methods=["POST"])
def create_user():
    with get_db_session() as session:
        user = User(**request.json)
        session.add(user)
    return user

# Or use Flask-SQLAlchemy which handles this
```

### API Response Patterns

```python
# Bad: Inconsistent response format
@app.route("/users")
def list_users():
    return [{"id": 1, "name": "Alice"}]

@app.route("/products")
def list_products():
    return {"products": [{"id": 1}], "total": 1}

# Good: Consistent envelope pattern
def success_response(data, message=None):
    response = {"success": True, "data": data}
    if message:
        response["message"] = message
    return response

def error_response(message, errors=None):
    response = {"success": False, "error": message}
    if errors:
        response["errors"] = errors
    return response

@app.route("/users")
def list_users():
    users = [{"id": 1, "name": "Alice"}]
    return success_response(users)

@app.route("/products")
def list_products():
    products = [{"id": 1}]
    return success_response({"items": products, "total": len(products)})
```

## CLI Tool Patterns

### Click Best Practices

#### 1. Command Organization

```python
# Bad: All commands in one function
import click

@click.command()
@click.option("--action")
@click.option("--name")
@click.option("--id")
def cli(action, name, id):
    if action == "create":
        # create logic
        pass
    elif action == "delete":
        # delete logic
        pass
    # ...

# Good: Use command groups
import click

@click.group()
def cli():
    """My CLI tool"""
    pass

@cli.command()
@click.argument("name")
def create(name):
    """Create a new resource"""
    click.echo(f"Creating {name}")

@cli.command()
@click.argument("id", type=int)
def delete(id):
    """Delete a resource by ID"""
    click.echo(f"Deleting {id}")

if __name__ == "__main__":
    cli()
```

#### 2. Configuration Management

```python
# Bad: Hardcoded configuration
@click.command()
def deploy():
    host = "production.example.com"
    port = 22
    # ...

# Good: Configuration file + environment variables
import click
from pathlib import Path
import json
import os

def load_config():
    config_path = Path.home() / ".myapp" / "config.json"
    if config_path.exists():
        return json.loads(config_path.read_text())
    return {}

@click.command()
@click.option("--host", envvar="DEPLOY_HOST", help="Deployment host")
@click.option("--port", envvar="DEPLOY_PORT", type=int, default=22)
def deploy(host, port):
    config = load_config()
    host = host or config.get("host", "localhost")
    port = port or config.get("port", 22)
    click.echo(f"Deploying to {host}:{port}")
```

#### 3. Progress Indication

```python
# Bad: Silent operations
@click.command()
def process():
    items = load_items()
    for item in items:
        process_item(item)

# Good: Show progress
@click.command()
def process():
    items = load_items()
    with click.progressbar(items, label="Processing items") as bar:
        for item in bar:
            process_item(item)

# For long-running tasks
@click.command()
def download():
    with click.progressbar(length=100, label="Downloading") as bar:
        for chunk in download_chunks():
            bar.update(len(chunk))
```

#### 4. Interactive Prompts

```python
# Bad: Requiring all options upfront
@click.command()
@click.option("--name", required=True)
@click.option("--email", required=True)
@click.option("--confirm", is_flag=True, required=True)
def create_user(name, email, confirm):
    # ...

# Good: Interactive prompts with defaults
@click.command()
@click.option("--name", prompt="Enter name")
@click.option("--email", prompt="Enter email")
@click.confirmation_option(prompt="Are you sure?")
def create_user(name, email):
    click.echo(f"Creating user {name} ({email})")

# Better: Prompt only if not provided
@click.command()
@click.option("--name", prompt="Enter name", help="User name")
@click.option("--email", prompt="Enter email", help="User email")
@click.option("--force", is_flag=True, help="Skip confirmation")
def create_user(name, email, force):
    if not force:
        click.confirm("Are you sure?", abort=True)
    click.echo(f"Creating user {name} ({email})")
```

#### 5. Output Formatting

```python
# Bad: Inconsistent output
@click.command()
def list_users():
    users = get_users()
    for user in users:
        print(f"{user.id} - {user.name}")

# Good: Structured output with format options
import json
from tabulate import tabulate

@click.command()
@click.option("--format", type=click.Choice(["table", "json", "csv"]), default="table")
def list_users(format):
    users = get_users()

    if format == "json":
        click.echo(json.dumps([u.to_dict() for u in users], indent=2))
    elif format == "csv":
        click.echo("id,name,email")
        for u in users:
            click.echo(f"{u.id},{u.name},{u.email}")
    else:  # table
        headers = ["ID", "Name", "Email"]
        rows = [[u.id, u.name, u.email] for u in users]
        click.echo(tabulate(rows, headers=headers))
```

#### 6. Error Handling

```python
# Bad: Uncaught exceptions
@click.command()
def process():
    data = load_data()  # May raise FileNotFoundError
    result = process_data(data)  # May raise ValueError
    save_result(result)  # May raise IOError

# Good: Graceful error handling
@click.command()
def process():
    try:
        data = load_data()
    except FileNotFoundError as e:
        click.echo(click.style(f"Error: {e}", fg="red"), err=True)
        raise click.Abort()

    try:
        result = process_data(data)
    except ValueError as e:
        click.echo(click.style(f"Invalid data: {e}", fg="red"), err=True)
        raise click.Abort()

    try:
        save_result(result)
    except IOError as e:
        click.echo(click.style(f"Failed to save: {e}", fg="red"), err=True)
        raise click.Abort()

    click.echo(click.style("Success!", fg="green"))

# Better: Context manager for common error handling
from contextlib import contextmanager

@contextmanager
def handle_errors(operation_name):
    try:
        yield
    except Exception as e:
        click.echo(
            click.style(f"Error during {operation_name}: {e}", fg="red"),
            err=True
        )
        raise click.Abort()

@click.command()
def process():
    with handle_errors("loading data"):
        data = load_data()

    with handle_errors("processing"):
        result = process_data(data)

    with handle_errors("saving"):
        save_result(result)

    click.echo(click.style("Success!", fg="green"))
```

#### 7. Logging

```python
# Bad: Print statements everywhere
@click.command()
@click.option("--verbose", is_flag=True)
def process(verbose):
    if verbose:
        print("Starting process")
    data = load_data()
    if verbose:
        print(f"Loaded {len(data)} items")
    # ...

# Good: Proper logging
import logging

def setup_logging(verbose):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

@click.command()
@click.option("--verbose", is_flag=True, help="Enable verbose output")
def process(verbose):
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    logger.info("Starting process")
    data = load_data()
    logger.debug(f"Loaded {len(data)} items")
    # ...
```

## Common Web/CLI Anti-Patterns

### Web Apps

- **No request validation**: Trusting client input
- **Missing CORS configuration**: Security issues in production
- **Synchronous I/O in async frameworks**: Blocking event loop
- **No rate limiting**: Vulnerable to abuse
- **Inconsistent error responses**: Poor API design
- **Missing authentication decorators**: Security holes
- **Database queries in templates**: Performance issues
- **No connection pooling**: Resource exhaustion

### CLI Tools

- **Silent failures**: No feedback to user
- **No progress indication**: User doesn't know if it's working
- **Inconsistent exit codes**: Scripts can't detect failures
- **No --help text**: Poor discoverability
- **Missing --dry-run mode**: Risky operations without preview
- **No configuration file support**: Must retype options
- **Printing errors to stdout instead of stderr**: Breaks piping
- **Not handling SIGINT gracefully**: Can't interrupt cleanly

## Review Checklist

**Web Applications:**
- [ ] Routes organized with blueprints/routers
- [ ] Request validation with Pydantic or similar
- [ ] Consistent error handling and responses
- [ ] Database sessions properly managed
- [ ] Authentication/authorization on protected routes
- [ ] CORS configured if needed
- [ ] Rate limiting on public endpoints
- [ ] Logging configured properly

**CLI Tools:**
- [ ] Commands organized with groups
- [ ] Progress indication for long operations
- [ ] Interactive prompts where appropriate
- [ ] Multiple output formats (JSON, table, etc.)
- [ ] Proper error handling with user-friendly messages
- [ ] --help text for all commands/options
- [ ] Configuration file support
- [ ] Errors written to stderr, not stdout
- [ ] Meaningful exit codes (0 = success, non-zero = failure)
