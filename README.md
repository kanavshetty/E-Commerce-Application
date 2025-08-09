## E-Commerce-Application

Built using (Tkinter + Flask + PostgreSQL)
A desktop e-commerce application with a Tkinter UI (multi-screen frame stack) that talks to a Flask REST API and stores data in PostgreSQL.


# Features
* User registration, login/logout, password reset

* Product catalog browsing & search

* Cart, wishlist, and checkout flow

* Orders, order history, profile & addresses

* Admin endpoints (optional) for inventory & product management

* Tkinter UI with frame stack (screens navigate without re-creating widgets)

* Token-based API auth (session/JWT — configurable)

# Tech Stack

* Frontend: Python 3, Tkinter, requests

* Backend: Python 3, Flask (+ Blueprints), psycopg2 or asyncpg/SQLAlchemy

* Database: PostgreSQL

* Migrations: Alembic (recommended)

* Auth: JWT (via flask-jwt-extended) or server sessions (choose one)

# Quick Start

1. git clone <this_repo_url> && cd <repo_dir>

2. python -m venv .venv
source .venv/bin/activate(For Windows)

3. pip install -r backend/requirements.txt

4. pip install -r frontend/requirements.txt

5. cp .env.example .env

6. createdb ecommerce_app

7. python backend/app.py

8. python frontend/main.py




