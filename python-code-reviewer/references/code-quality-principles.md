# Code Quality Principles

## DRY (Don't Repeat Yourself)

### Identifying Violations

Look for:
- **Duplicated code blocks**: Same or very similar code in multiple places
- **Copy-paste patterns**: Nearly identical functions with minor variations
- **Repeated constants**: Same magic numbers/strings in multiple locations
- **Duplicated logic**: Same business rules implemented in different ways

### Examples

```python
# Bad: Repeated validation logic
def create_user(username, email):
    if not username or len(username) < 3:
        raise ValueError("Invalid username")
    if not email or "@" not in email:
        raise ValueError("Invalid email")
    # ...

def update_user(user_id, username, email):
    if not username or len(username) < 3:
        raise ValueError("Invalid username")
    if not email or "@" not in email:
        raise ValueError("Invalid email")
    # ...

# Good: Extract validation
def validate_username(username):
    if not username or len(username) < 3:
        raise ValueError("Invalid username")

def validate_email(email):
    if not email or "@" not in email:
        raise ValueError("Invalid email")

def create_user(username, email):
    validate_username(username)
    validate_email(email)
    # ...

def update_user(user_id, username, email):
    validate_username(username)
    validate_email(email)
    # ...
```

```python
# Bad: Repeated database queries
def get_active_admins():
    return db.query(User).filter_by(role='admin', is_active=True).all()

def count_active_admins():
    return db.query(User).filter_by(role='admin', is_active=True).count()

def has_active_admins():
    return db.query(User).filter_by(role='admin', is_active=True).count() > 0

# Good: Extract query building
def active_admins_query():
    return db.query(User).filter_by(role='admin', is_active=True)

def get_active_admins():
    return active_admins_query().all()

def count_active_admins():
    return active_admins_query().count()

def has_active_admins():
    return active_admins_query().count() > 0
```

```python
# Bad: Configuration duplication
def send_welcome_email(user):
    send_email(
        to=user.email,
        from_email="noreply@example.com",
        smtp_host="smtp.example.com",
        smtp_port=587
    )

def send_password_reset(user):
    send_email(
        to=user.email,
        from_email="noreply@example.com",
        smtp_host="smtp.example.com",
        smtp_port=587
    )

# Good: Centralize configuration
class EmailConfig:
    FROM_EMAIL = "noreply@example.com"
    SMTP_HOST = "smtp.example.com"
    SMTP_PORT = 587

def send_welcome_email(user):
    send_email(
        to=user.email,
        from_email=EmailConfig.FROM_EMAIL,
        smtp_host=EmailConfig.SMTP_HOST,
        smtp_port=EmailConfig.SMTP_PORT
    )
```

## Separation of Concerns

### Identifying Violations

Look for functions/classes that:
- **Mix business logic with I/O**: Database queries mixed with calculations
- **Mix presentation with logic**: HTML generation mixed with data processing
- **Handle multiple responsibilities**: One function doing validation, transformation, and persistence
- **Tight coupling**: Hard dependencies between unrelated components

### Layered Architecture

```python
# Bad: Everything in one place
def process_order(order_id):
    # Database access
    order = db.query(Order).filter_by(id=order_id).first()

    # Business logic
    total = sum(item.price * item.quantity for item in order.items)
    tax = total * 0.1
    grand_total = total + tax

    # Validation
    if grand_total > order.user.credit_limit:
        raise ValueError("Exceeds credit limit")

    # Payment processing
    payment_gateway.charge(order.user.card, grand_total)

    # Email notification
    send_email(order.user.email, f"Order total: ${grand_total}")

    # Database update
    order.status = "completed"
    db.commit()

# Good: Separated layers
# Domain/Business Logic Layer
class Order:
    def calculate_total(self):
        subtotal = sum(item.price * item.quantity for item in self.items)
        tax = subtotal * 0.1
        return subtotal + tax

    def can_be_processed(self):
        return self.calculate_total() <= self.user.credit_limit

# Repository/Data Layer
class OrderRepository:
    def get_by_id(self, order_id):
        return db.query(Order).filter_by(id=order_id).first()

    def mark_completed(self, order):
        order.status = "completed"
        db.commit()

# Service/Application Layer
class OrderService:
    def __init__(self, order_repo, payment_gateway, email_service):
        self.order_repo = order_repo
        self.payment_gateway = payment_gateway
        self.email_service = email_service

    def process_order(self, order_id):
        order = self.order_repo.get_by_id(order_id)

        if not order.can_be_processed():
            raise ValueError("Exceeds credit limit")

        total = order.calculate_total()
        self.payment_gateway.charge(order.user.card, total)
        self.email_service.send_order_confirmation(order.user.email, total)
        self.order_repo.mark_completed(order)
```

### Single Responsibility Principle

```python
# Bad: Class doing too much
class UserManager:
    def create_user(self, username, email, password):
        # Validation
        if not self._is_valid_email(email):
            raise ValueError("Invalid email")

        # Password hashing
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        # Database
        user = User(username=username, email=email, password=hashed)
        db.add(user)
        db.commit()

        # Email
        self._send_welcome_email(email)

        # Logging
        logger.info(f"User created: {username}")

        return user

# Good: Separated responsibilities
class EmailValidator:
    @staticmethod
    def is_valid(email):
        return "@" in email and "." in email.split("@")[1]

class PasswordHasher:
    @staticmethod
    def hash(password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

class UserRepository:
    def save(self, user):
        db.add(user)
        db.commit()
        return user

class WelcomeEmailService:
    def send(self, email):
        # Email sending logic
        pass

class UserService:
    def __init__(self, validator, hasher, repo, email_service):
        self.validator = validator
        self.hasher = hasher
        self.repo = repo
        self.email_service = email_service

    def create_user(self, username, email, password):
        if not self.validator.is_valid(email):
            raise ValueError("Invalid email")

        hashed_password = self.hasher.hash(password)
        user = User(username=username, email=email, password=hashed_password)
        user = self.repo.save(user)

        self.email_service.send(email)
        logger.info(f"User created: {username}")

        return user
```

## Idiomatic Python (Pythonic Code)

### EAFP vs. LBYL

**Pythonic**: "Easier to Ask for Forgiveness than Permission" (EAFP)

```python
# Bad: Look Before You Leap (LBYL)
if key in my_dict:
    value = my_dict[key]
else:
    value = default

if os.path.exists(filename):
    with open(filename) as f:
        data = f.read()

# Good: EAFP
try:
    value = my_dict[key]
except KeyError:
    value = default

# Or better
value = my_dict.get(key, default)

try:
    with open(filename) as f:
        data = f.read()
except FileNotFoundError:
    data = None
```

### Context Managers

```python
# Bad: Manual resource management
file = open("data.txt")
try:
    data = file.read()
finally:
    file.close()

# Good: Context manager
with open("data.txt") as file:
    data = file.read()

# Good: Custom context manager
from contextlib import contextmanager

@contextmanager
def database_transaction():
    transaction = db.begin()
    try:
        yield transaction
        transaction.commit()
    except Exception:
        transaction.rollback()
        raise

with database_transaction() as tx:
    # Work with transaction
    pass
```

### Descriptive Variable Names with Unpacking

```python
# Bad: Numeric indexing
point = (10, 20)
x = point[0]
y = point[1]

# Good: Unpacking
x, y = point

# Bad: Range with index
for i in range(len(items)):
    print(i, items[i])

# Good: Enumerate
for i, item in enumerate(items):
    print(i, item)
```

### Properties Over Getters/Setters

```python
# Bad: Java-style getters/setters
class User:
    def __init__(self):
        self._email = None

    def get_email(self):
        return self._email

    def set_email(self, email):
        if "@" not in email:
            raise ValueError("Invalid email")
        self._email = email

user = User()
user.set_email("test@example.com")
print(user.get_email())

# Good: Properties
class User:
    def __init__(self):
        self._email = None

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        if "@" not in email:
            raise ValueError("Invalid email")
        self._email = email

user = User()
user.email = "test@example.com"
print(user.email)
```

### Use `with` for Multiple Context Managers

```python
# Bad: Nested with statements
with open("input.txt") as f_in:
    with open("output.txt", "w") as f_out:
        f_out.write(f_in.read())

# Good: Multiple context managers
with open("input.txt") as f_in, open("output.txt", "w") as f_out:
    f_out.write(f_in.read())
```

## Length Limits (Avoiding "Too Long")

### Function Length

**Guideline**: Functions should be **< 50 lines**, ideally **< 25 lines**

**Indicators a function is too long**:
- Hard to understand at a glance
- Multiple levels of abstraction mixed together
- Many local variables
- Multiple concerns handled

```python
# Too long (100+ lines)
def process_user_registration(form_data):
    # Validation (20 lines)
    # Password hashing (10 lines)
    # Database operations (20 lines)
    # Email sending (15 lines)
    # Logging (10 lines)
    # Analytics tracking (15 lines)
    # ...

# Better: Extract sub-functions
def process_user_registration(form_data):
    user_data = validate_registration(form_data)
    user = create_user_account(user_data)
    send_welcome_email(user)
    track_registration(user)
    return user
```

### Class Length

**Guideline**: Classes should be **< 300 lines**, ideally **< 200 lines**

**Indicators a class is too long**:
- Too many methods (> 20)
- Too many instance variables (> 10)
- Multiple responsibilities
- God object anti-pattern

```python
# Too long: UserManager handling everything
class UserManager:  # 500+ lines
    def create_user(self): pass
    def update_user(self): pass
    def delete_user(self): pass
    def authenticate(self): pass
    def send_password_reset(self): pass
    def send_welcome_email(self): pass
    def validate_email(self): pass
    def hash_password(self): pass
    def generate_token(self): pass
    # ... 20+ more methods

# Better: Split by responsibility
class UserRepository:  # 100 lines
    def create(self, user): pass
    def update(self, user): pass
    def delete(self, user_id): pass
    def find_by_email(self, email): pass

class AuthenticationService:  # 80 lines
    def authenticate(self, email, password): pass
    def generate_token(self, user): pass
    def verify_token(self, token): pass

class UserEmailService:  # 60 lines
    def send_welcome(self, user): pass
    def send_password_reset(self, user): pass
```

### File Length

**Guideline**: Files should be **< 500 lines**, ideally **< 300 lines**

**Indicators a file is too long**:
- Multiple classes that aren't closely related
- Mixing concerns (models + views + business logic)
- Monolithic module

```python
# Bad: models.py with 50+ models (2000+ lines)
# models.py
class User: pass
class Product: pass
class Order: pass
# ... 47 more models

# Good: Split by domain
# users/models.py (150 lines)
class User: pass
class UserProfile: pass
class UserSettings: pass

# products/models.py (200 lines)
class Product: pass
class Category: pass
class ProductImage: pass

# orders/models.py (180 lines)
class Order: pass
class OrderItem: pass
class Payment: pass
```

### Method Parameter Count

**Guideline**: Methods should have **< 5 parameters**, ideally **< 3**

```python
# Bad: Too many parameters
def create_user(username, email, password, first_name, last_name,
                phone, address, city, state, zip_code, country):
    pass

# Good: Use a data class or dict
from dataclasses import dataclass

@dataclass
class UserRegistration:
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    phone: str
    address: str
    city: str
    state: str
    zip_code: str
    country: str

def create_user(registration: UserRegistration):
    pass
```

### Nesting Depth

**Guideline**: Maximum nesting depth of **3 levels**, ideally **2 levels**

```python
# Bad: 5 levels of nesting
def process(data):
    if data:
        for item in data:
            if item.is_valid():
                for sub_item in item.children:
                    if sub_item.active:
                        result.append(sub_item)

# Good: Early returns and extraction
def process(data):
    if not data:
        return []

    result = []
    for item in data:
        if not item.is_valid():
            continue
        result.extend(_process_item(item))
    return result

def _process_item(item):
    return [sub for sub in item.children if sub.active]
```

### Complexity Thresholds

**Guideline**: Cyclomatic complexity should be **< 10**, ideally **< 5**

Use tools to measure:
```bash
# radon for complexity
pip install radon
radon cc myfile.py -a  # -a shows average

# Flag functions with complexity > 10
radon cc myfile.py --min C
```

## Long String Formatting

### Line Length and Strings

Ruff/Black formatters do **not** automatically break long strings because it can change semantics (breaking regexes, SQL, etc.). Use **implicit string concatenation** to manually break long strings.

### Implicit String Concatenation

Python automatically concatenates adjacent string literals. This is the idiomatic way to handle long strings:

```python
# Bad: Long single-line string exceeding line length
message = "This is a very long error message that explains what went wrong and provides detailed context about the failure"

# Good: Implicit string concatenation with parentheses
message = (
    "This is a very long error message that explains what went wrong "
    "and provides detailed context about the failure"
)
```

### F-strings with Implicit Concatenation

For f-strings, each segment needs its own `f` prefix:

```python
# Bad: Long f-string on single line
prompt = f"Enhance this {room_type} description with atmospheric details. Add vivid sensory details including sights, sounds, and smells."

# Good: Break with implicit concatenation
prompt = (
    f"Enhance this {room_type} description with atmospheric details. "
    f"Add vivid sensory details including sights, sounds, and smells."
)
```

### Multi-line Content with Explicit Newlines

When the string content needs actual newlines, include `\n` explicitly:

```python
# Good: Multi-line prompt with explicit newlines
prompt = (
    f"Narrate this combat action:\n\n"
    f"Attacker: {attacker}\n"
    f"Defender: {defender}\n\n"
    f"Describe the action in one dramatic sentence."
)
```

### When to Use Triple-Quoted Strings

Use triple-quoted strings only when:
- The string content itself needs to preserve formatting/indentation
- You're writing docstrings
- The content is truly multi-line by nature (like SQL, HTML templates)

```python
# Good: SQL query that benefits from readable formatting
query = """
    SELECT u.name, u.email
    FROM users u
    JOIN orders o ON u.id = o.user_id
    WHERE o.status = 'pending'
"""

# Bad: Using triple quotes just to avoid line length
# (loses control over whitespace)
message = """This is a long message that
should be on one line but was wrapped
using triple quotes."""
```

### textwrap.dedent for Indented Blocks

When you need multi-line strings in indented code:

```python
from textwrap import dedent

def get_help_text():
    return dedent("""
        Usage: my_command [options]

        Options:
            -h, --help    Show this help message
            -v, --verbose Enable verbose output
    """).strip()
```

## Review Checklist

When reviewing code, check:

**DRY:**
- [ ] No duplicated code blocks
- [ ] Constants extracted and named
- [ ] Common logic in shared functions
- [ ] Configuration centralized

**Separation of Concerns:**
- [ ] Business logic separated from I/O
- [ ] Presentation separated from data processing
- [ ] Single responsibility per class/function
- [ ] Clear layer boundaries

**Idiomatic Python:**
- [ ] EAFP pattern where appropriate
- [ ] Context managers for resources
- [ ] Properties instead of getters/setters
- [ ] List comprehensions where readable
- [ ] Built-in functions used
- [ ] Pythonic naming conventions

**Length:**
- [ ] Functions < 50 lines (ideally < 25)
- [ ] Classes < 300 lines (ideally < 200)
- [ ] Files < 500 lines (ideally < 300)
- [ ] Methods < 5 parameters (ideally < 3)
- [ ] Nesting depth < 3 levels
- [ ] Cyclomatic complexity < 10
- [ ] Long strings use implicit concatenation (not single long lines)
