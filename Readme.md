# MiniTwitter (FastAPI + PostgreSQL + Redis)

This project is a backend API for a simple Twitter-like app using **FastAPI**, **PostgreSQL**, and **Redis** for caching.


---

## What Each File Does

### `twitter_database.py`
- Defines SQLAlchemy ORM models: `User`, `Post`, `Comment`, etc.
- Sets up database engine and session (`SessionLocal`)
  
### `schemas.py`
- Contains Pydantic models for validating API input/output
- Helps FastAPI auto-generate docs (like Swagger)

### `crud.py`
- Handles business logic for interacting with the database
- Functions for creating users, posts, comments, etc.

### `cache.py`
- Connects to a local Redis instance
- Provides helper functions to set and get cached responses

### `main.py`
- FastAPI application with all routes (`/users`, `/posts`, `/comments`, etc.)
- Includes JWT authentication, caching, and database integration




