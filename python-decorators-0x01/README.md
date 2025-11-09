# Python Decorators for Database Operations

This repository contains Python decorators designed to enhance database operations by adding logging, connection handling, transaction management, retry logic, and caching.

---

## Tasks

### 0. Logging Database Queries
**Objective:** Create a decorator that logs SQL queries before execution.

#### Instructions
- Implement the `log_queries` decorator to log the SQL query before executing it.

#### Prototype
```python
def log_queries(func):
    """Decorator to log SQL queries."""
    # Your code here
