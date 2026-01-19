# Python Anti-Patterns and Code Quality Issues

## Naming Conventions (PEP 8)

### Issues to Flag

- **Non-descriptive names**: Single letter variables (except i, j, k in loops), abbreviations
- **Wrong case**: Classes not in PascalCase, functions/variables not in snake_case, constants not in UPPER_CASE
- **Python keywords as names**: Using `list`, `dict`, `str`, `type`, etc. as variable names
- **Double underscore abuse**: Using `__private` unless actually needed for name mangling

### Good Examples

```python
# Good
class UserRepository:
    MAX_RETRY_COUNT = 3

    def get_active_users(self):
        return self._fetch_users(is_active=True)

# Bad
class userRepo:  # Wrong case
    maxRetry = 3  # Wrong case for constant

    def getUsers(self):  # camelCase instead of snake_case
        list = []  # Shadowing builtin
        return list
```

## Common Anti-Patterns

### 1. Mutable Default Arguments

**Problem**: Mutable defaults are shared across all function calls

```python
# Bad
def add_item(item, items=[]):
    items.append(item)
    return items

# Good
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

### 2. Bare Exception Handling

**Problem**: Catches system exits, keyboard interrupts, and hides real errors

```python
# Bad
try:
    risky_operation()
except:
    pass

# Bad
try:
    risky_operation()
except Exception:
    pass  # Silently swallowing exceptions

# Good
try:
    risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise
```

### 3. String Concatenation in Loops

**Problem**: Creates new string objects in each iteration (O(n²) complexity)

```python
# Bad
result = ""
for item in items:
    result += str(item)

# Good
result = "".join(str(item) for item in items)
```

### 4. Not Using Context Managers

**Problem**: Files/resources may not be properly closed

```python
# Bad
f = open("file.txt")
data = f.read()
f.close()

# Good
with open("file.txt") as f:
    data = f.read()
```

### 5. Using `type()` Instead of `isinstance()`

**Problem**: Doesn't respect inheritance

```python
# Bad
if type(obj) == list:
    process(obj)

# Good
if isinstance(obj, list):
    process(obj)
```

### 6. Checking for Empty Sequences with `len()`

**Problem**: Unnecessarily verbose, doesn't use Python's truthiness

```python
# Bad
if len(items) == 0:
    return

if len(items) > 0:
    process(items)

# Good
if not items:
    return

if items:
    process(items)
```

### 7. Using `range(len())` to Iterate

**Problem**: Unnecessarily complex, non-Pythonic

```python
# Bad
for i in range(len(items)):
    print(items[i])

# Good
for item in items:
    print(item)

# If you need the index
for i, item in enumerate(items):
    print(f"{i}: {item}")
```

### 8. Not Using List/Dict/Set Comprehensions

**Problem**: More verbose than necessary

```python
# Bad
squares = []
for i in range(10):
    squares.append(i ** 2)

# Good
squares = [i ** 2 for i in range(10)]

# Bad
unique_names = []
for name in names:
    if name not in unique_names:
        unique_names.append(name)

# Good
unique_names = list(set(names))
# Or if order matters
unique_names = list(dict.fromkeys(names))
```

### 9. Using `import *`

**Problem**: Namespace pollution, unclear dependencies

```python
# Bad
from module import *

# Good
from module import specific_function, SpecificClass
# Or
import module
```

### 10. Not Using `pathlib` for File Paths

**Problem**: String manipulation for paths is error-prone and non-portable

```python
# Bad
import os
path = os.path.join(base_dir, "subdir", "file.txt")
if os.path.exists(path):
    with open(path) as f:
        data = f.read()

# Good
from pathlib import Path
path = Path(base_dir) / "subdir" / "file.txt"
if path.exists():
    data = path.read_text()
```

### 11. Using `==` to Check for None, True, False

**Problem**: Should use `is` for singleton comparisons

```python
# Bad
if value == None:
    return

if flag == True:
    process()

# Good
if value is None:
    return

if flag:  # or 'if flag is True' if you really need explicit check
    process()
```

### 12. Not Using `get()` for Dictionaries

**Problem**: KeyError exceptions or verbose try/except blocks

```python
# Bad
if key in my_dict:
    value = my_dict[key]
else:
    value = default

# Good
value = my_dict.get(key, default)
```

### 13. Creating Classes with Only `__init__`

**Problem**: Should just use a function or dataclass

```python
# Bad
class DataHolder:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Good (if you need a data container)
from dataclasses import dataclass

@dataclass
class DataHolder:
    x: int
    y: int

# Or just use a function if it's processing data
def process_data(x, y):
    return x + y
```

### 14. Reimplementing Built-in Functions

**Problem**: Reinventing the wheel

```python
# Bad
def maximum(items):
    max_val = items[0]
    for item in items[1:]:
        if item > max_val:
            max_val = item
    return max_val

# Good
max_val = max(items)
```

### 15. Not Using `any()` and `all()`

**Problem**: Verbose loops for simple checks

```python
# Bad
has_negative = False
for num in numbers:
    if num < 0:
        has_negative = True
        break

# Good
has_negative = any(num < 0 for num in numbers)

# Bad
all_positive = True
for num in numbers:
    if num <= 0:
        all_positive = False
        break

# Good
all_positive = all(num > 0 for num in numbers)
```

## Code Organization Issues

### 1. Too Many Responsibilities (SRP Violation)

**Problem**: Functions/classes doing too much

```python
# Bad
def process_user_data(user_id):
    # Fetch from database
    user = db.query(User).filter_by(id=user_id).first()
    # Validate
    if not user.email:
        raise ValueError("No email")
    # Transform
    user.email = user.email.lower()
    # Send email
    send_email(user.email, "Welcome")
    # Log
    logger.info(f"Processed {user_id}")
    return user

# Good - Split into focused functions
def get_user(user_id):
    return db.query(User).filter_by(id=user_id).first()

def validate_user(user):
    if not user.email:
        raise ValueError("No email")

def normalize_user_email(user):
    user.email = user.email.lower()
    return user

def process_user_data(user_id):
    user = get_user(user_id)
    validate_user(user)
    user = normalize_user_email(user)
    send_welcome_email(user)
    logger.info(f"Processed {user_id}")
    return user
```

### 2. Deep Nesting

**Problem**: Hard to read and understand control flow

```python
# Bad
def process(data):
    if data:
        if data.is_valid():
            if data.user:
                if data.user.is_active:
                    return data.user.process()
    return None

# Good - Early returns
def process(data):
    if not data:
        return None
    if not data.is_valid():
        return None
    if not data.user:
        return None
    if not data.user.is_active:
        return None
    return data.user.process()
```

### 3. Magic Numbers

**Problem**: Unclear meaning of numeric literals

```python
# Bad
if user.age < 18:
    return False
if len(password) < 8:
    return False

# Good
MINIMUM_AGE = 18
MINIMUM_PASSWORD_LENGTH = 8

if user.age < MINIMUM_AGE:
    return False
if len(password) < MINIMUM_PASSWORD_LENGTH:
    return False
```

## Documentation Issues

### 1. Missing or Poor Docstrings

```python
# Bad
def calc(x, y):
    return x / y

# Good
def calculate_average_rate(total_amount: float, time_period: int) -> float:
    """Calculate the average rate over a time period.

    Args:
        total_amount: The total amount to average
        time_period: Number of time units

    Returns:
        The average rate per time unit

    Raises:
        ValueError: If time_period is zero
    """
    if time_period == 0:
        raise ValueError("Time period cannot be zero")
    return total_amount / time_period
```

### 2. Comments Explaining What Instead of Why

```python
# Bad
# Increment i by 1
i += 1

# Good
# Account for zero-based indexing when displaying to user
display_number = i + 1
```
