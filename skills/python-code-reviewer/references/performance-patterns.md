# Python Performance Patterns

## Iteration and Comprehensions

### 1. List Comprehensions vs. Loops

**Fast**: List comprehensions are implemented in C and faster than equivalent loops

```python
# Slower
squares = []
for i in range(1000):
    squares.append(i ** 2)

# Faster (2x improvement typically)
squares = [i ** 2 for i in range(1000)]
```

### 2. Generator Expressions for Large Datasets

**Memory**: Generators produce items on-demand, avoiding memory overhead

```python
# Bad: Loads entire result in memory
squares = [i ** 2 for i in range(10_000_000)]
total = sum(squares)

# Good: Processes one item at a time
total = sum(i ** 2 for i in range(10_000_000))
```

### 3. Use Built-in Functions

**Fast**: Built-ins are implemented in C and highly optimized

```python
# Slower
total = 0
for num in numbers:
    total += num

# Faster
total = sum(numbers)

# Slower
max_val = numbers[0]
for num in numbers[1:]:
    if num > max_val:
        max_val = num

# Faster
max_val = max(numbers)
```

### 4. Avoid Repeated Attribute Lookups

**Fast**: Store frequently accessed attributes in local variables

```python
# Slower: Method lookup on every iteration
for i in range(1000):
    my_list.append(i)

# Faster: Single lookup
append = my_list.append
for i in range(1000):
    append(i)

# Slower: Multiple attribute lookups
for item in items:
    result = math.sqrt(item) + math.pi * math.e

# Faster
from math import sqrt, pi, e
for item in items:
    result = sqrt(item) + pi * e
```

## Data Structures

### 5. Use Appropriate Data Structures

**Fast**: Choose the right tool for the job

```python
# Bad: O(n) lookup in list
def has_duplicates(items):
    seen = []
    for item in items:
        if item in seen:  # O(n) lookup
            return True
        seen.append(item)
    return False

# Good: O(1) lookup in set
def has_duplicates(items):
    seen = set()
    for item in items:
        if item in seen:  # O(1) lookup
            return True
        seen.add(item)
    return False

# Best: Use set properties
def has_duplicates(items):
    return len(items) != len(set(items))
```

### 6. Use `collections` Module

```python
from collections import defaultdict, Counter, deque

# Bad: Manual counting
counts = {}
for item in items:
    if item in counts:
        counts[item] += 1
    else:
        counts[item] = 1

# Good: Counter
counts = Counter(items)

# Bad: Queue with list (O(n) for pop(0))
queue = []
queue.append(1)
queue.pop(0)  # Slow!

# Good: deque with O(1) operations
queue = deque()
queue.append(1)
queue.popleft()  # Fast!

# Bad: Checking for key existence
groups = {}
for item in items:
    key = item.category
    if key not in groups:
        groups[key] = []
    groups[key].append(item)

# Good: defaultdict
groups = defaultdict(list)
for item in items:
    groups[item.category].append(item)
```

### 7. String Concatenation

**Fast**: Use `join()` for building strings from sequences

```python
# Very slow: O(n²) due to string immutability
result = ""
for item in items:
    result += str(item)

# Fast: O(n)
result = "".join(str(item) for item in items)

# For simple cases, f-strings are fine and readable
name = f"{first} {last}"
```

## Function Calls and Algorithms

### 8. Avoid Unnecessary Function Calls

```python
# Bad: Calling len() on every iteration
for i in range(len(items)):
    if i < len(items) - 1:  # len() called again
        process(items[i])

# Good: Calculate once
length = len(items)
for i in range(length):
    if i < length - 1:
        process(items[i])

# Better: Avoid the index entirely
for i, item in enumerate(items):
    if i < len(items) - 1:
        process(item)
```

### 9. Use `any()` and `all()` with Short-Circuiting

```python
# Less efficient: Processes entire list
has_negative = len([n for n in numbers if n < 0]) > 0

# Efficient: Stops at first match
has_negative = any(n < 0 for n in numbers)

# Less efficient
all_valid = True
for item in items:
    if not item.is_valid():
        all_valid = False

# Efficient: Short-circuits on first False
all_valid = all(item.is_valid() for item in items)
```

### 10. Choose the Right Algorithm

```python
# Bad: O(n²) for membership testing
def get_common_items(list1, list2):
    common = []
    for item in list1:
        if item in list2:  # O(n) lookup for each item
            common.append(item)
    return common

# Good: O(n) with set intersection
def get_common_items(list1, list2):
    return list(set(list1) & set(list2))

# Or maintain order
def get_common_items(list1, list2):
    set2 = set(list2)  # O(n) to create, O(1) lookups
    return [item for item in list1 if item in set2]
```

## I/O Operations

### 11. Batch File Operations

```python
# Bad: Opening file for each write
for item in items:
    with open("log.txt", "a") as f:
        f.write(str(item) + "\n")

# Good: Single file open
with open("log.txt", "w") as f:
    for item in items:
        f.write(str(item) + "\n")

# Better: Batch writes
with open("log.txt", "w") as f:
    f.write("\n".join(str(item) for item in items))
```

### 12. Use Binary Mode for Non-Text Files

```python
# Slower: Text mode with encoding/decoding overhead
with open("data.bin", "r") as f:
    data = f.read()

# Faster: Binary mode
with open("data.bin", "rb") as f:
    data = f.read()
```

### 13. Use `pathlib` for Path Operations

```python
# Slower: Multiple system calls
import os
if os.path.exists(path):
    if os.path.isfile(path):
        size = os.path.getsize(path)

# Faster: Single stat call
from pathlib import Path
p = Path(path)
if p.is_file():
    size = p.stat().st_size
```

## Database Operations

### 14. Batch Database Operations

```python
# Bad: N queries
for user in users:
    db.execute("INSERT INTO users VALUES (?, ?)", (user.id, user.name))
    db.commit()

# Good: Batch insert with single commit
db.executemany(
    "INSERT INTO users VALUES (?, ?)",
    [(u.id, u.name) for u in users]
)
db.commit()

# Bad: N+1 query problem
users = db.query(User).all()
for user in users:
    # Triggers separate query for each user!
    posts = user.posts

# Good: Eager loading
users = db.query(User).options(joinedload(User.posts)).all()
for user in users:
    posts = user.posts  # Already loaded
```

## Caching and Memoization

### 15. Use `functools.lru_cache` for Expensive Functions

```python
# Without caching: Recalculates every time
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# fibonacci(35) takes ~5 seconds

# With caching: Calculates once
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# fibonacci(35) takes <1 millisecond
```

### 16. Cache Expensive Computations

```python
# Bad: Recalculating every time
def process_data(data):
    normalized = expensive_normalization(data)
    return analyze(normalized)

# Good: Cache if data doesn't change often
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_normalization(data):
    # Expensive computation
    return normalized_data
```

## Object Creation

### 17. Reuse Objects When Possible

```python
# Bad: Creating regex on every call
import re

def validate_email(email):
    pattern = re.compile(r'^[a-z]+@[a-z]+\.[a-z]+$')
    return pattern.match(email) is not None

# Good: Compile once at module level
import re

EMAIL_PATTERN = re.compile(r'^[a-z]+@[a-z]+\.[a-z]+$')

def validate_email(email):
    return EMAIL_PATTERN.match(email) is not None
```

### 18. Use `__slots__` for Memory-Heavy Classes

```python
# Default: Each instance has a __dict__ (significant overhead)
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# With __slots__: Reduces memory by ~40%
class Point:
    __slots__ = ['x', 'y']

    def __init__(self, x, y):
        self.x = x
        self.y = y

# Creating 1 million Points:
# Without __slots__: ~200 MB
# With __slots__: ~120 MB
```

## Profiling Recommendations

### When to Optimize

1. **Profile first**: Don't optimize without measuring
2. **Focus on bottlenecks**: 80/20 rule - 80% of time in 20% of code
3. **Readability matters**: Only optimize if there's a real performance issue

### Profiling Tools

```python
# Time a specific block
import time

start = time.perf_counter()
# ... code to measure ...
elapsed = time.perf_counter() - start
print(f"Took {elapsed:.3f} seconds")

# Profile entire script
# python -m cProfile -s cumulative script.py

# Line-by-line profiling
# pip install line_profiler
# Add @profile decorator to functions
# kernprof -l -v script.py

# Memory profiling
# pip install memory_profiler
# Add @profile decorator to functions
# python -m memory_profiler script.py
```

## Performance Anti-Patterns to Flag

- **Quadratic complexity**: Nested loops over same/similar data
- **Repeated work**: Same calculation in a loop
- **Wrong data structure**: List for membership testing, etc.
- **Premature optimization**: Optimizing before profiling
- **Ignoring built-ins**: Reimplementing `sum`, `max`, `min`, etc.
- **Memory leaks**: Not closing resources, growing unbounded caches
- **Synchronous I/O in loops**: Not batching or using async
- **Loading everything in memory**: Not using generators for large datasets
