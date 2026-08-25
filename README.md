# Coderr Backend

Coderr is a Django REST Framework API for a service marketplace. Customers can
request offers from business users, manage orders, and leave reviews.

This repository contains the backend only. The API contract is defined in the
[Coderr endpoint documentation](https://cdn.developerakademie.com/courses/Backend/EndpointDoku/index.html?name=coderr).

## Requirements

- Python 3.12 or newer
- pip

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
set -a
source .env
set +a
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The development server is available at `http://127.0.0.1:8000/`. Django admin
is available at `http://127.0.0.1:8000/admin/` after creating a superuser.

Environment variables may be exported in the shell or loaded by the process
manager. Django deliberately does not parse `.env` files itself.

## Quality checks

```bash
python manage.py check
python manage.py test
ruff check .
coverage run manage.py test
coverage report --fail-under=95
```

## Planned API areas

- Authentication: registration and login
- Profiles: customer and business profiles
- Offers and offer details
- Orders and order statistics
- Reviews
- Aggregated base information

## Project structure

The Django project package is named `core`. Each domain app uses the required
`_app` suffix and owns an `api/` package for serializers, views, permissions,
and routes.
