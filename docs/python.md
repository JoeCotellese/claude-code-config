# Python Development Standards

## Package Management
- Always use `uv` for package management (not pip, poetry, or conda)
- Create virtual environments local to the project directory using `uv`
- Never use global Python installations for project dependencies

## Project Setup
```bash
# Initialize a new Python project
uv init

# Create virtual environment in project directory
uv venv

# Install dependencies
uv pip install -r requirements.txt

# Add new dependencies
uv pip install package_name
```

## Code Style and Standards
- Follow PEP 8 for code style
- Use type hints for all function signatures
- Prefer f-strings over .format() or % formatting
- Use pathlib for file operations instead of os.path
- Use dataclasses or Pydantic for data structures

## Import Organization
```python
# Standard library imports
import os
import sys
from pathlib import Path

# Third-party imports
import pandas as pd
import numpy as np

# Local application imports
from app.models import User
from app.utils import helpers
```

## Testing
- Use pytest for testing framework
- Place tests in a `tests/` directory
- Name test files with `test_` prefix
- Use fixtures for common test setup
- Aim for high test coverage (>80%)

## Async Programming
- Use asyncio for concurrent operations
- Prefer async/await over threading for I/O operations
- Use aiohttp for async HTTP requests
- Use asyncpg for async PostgreSQL operations

## Error Handling
- Use specific exception types, not bare except
- Log errors appropriately
- Provide user-friendly error messages
- Use context managers for resource management

## Documentation
- Use docstrings for all public functions and classes
- Follow Google or NumPy docstring style consistently
- Include type hints in function signatures
- Document complex algorithms and business logic

## Common Libraries and Preferences
- **Web Framework**: FastAPI (preferred) or Flask
- **ORM**: SQLAlchemy or Tortoise-ORM for async
- **Data Processing**: pandas, numpy, polars
- **HTTP Client**: httpx (supports async) or requests
- **Testing**: pytest with pytest-asyncio for async tests
- **Linting**: ruff (preferred) or flake8 + black
- **Type Checking**: pyright (preferred) with django-stubs for Django projects

## Type Checking
- Use pyright for static type analysis
- Add type annotations to all new function signatures (parameters and return types)
- Use `X | None` union syntax (PEP 604), not `Optional[X]`
- Use `django-stubs` for Django model/queryset type awareness
- For Django models with custom managers or related fields, use explicit type annotations rather than relying on inference
- Common django-stubs patterns:
  - `QuerySet[MyModel]` for queryset return types
  - `ForeignKey` fields resolve to the related model type
  - `request.user` typed via `AUTH_USER_MODEL` setting in django-stubs config
- When pyright reports false positives on Django dynamic attributes (e.g., reverse relations, custom manager methods), use `# type: ignore[reportAttributeAccessIssue]` with a brief comment explaining why

## Project Structure
```
project_name/
├── src/
│   └── project_name/
│       ├── __init__.py
│       ├── main.py
│       ├── models/
│       ├── services/
│       └── utils/
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   └── test_services.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Performance Considerations
- Profile before optimizing
- Use generators for large datasets
- Consider using Cython or Numba for CPU-intensive operations
- Use connection pooling for database operations
- Implement caching where appropriate

## Security
- Never hardcode secrets or API keys
- Use environment variables for configuration
- Validate all user inputs
- Use parameterized queries to prevent SQL injection
- Keep dependencies updated