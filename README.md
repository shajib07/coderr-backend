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

## Environment variables

| Variable | Purpose | Development default |
|---|---|---|
| `DJANGO_SECRET_KEY` | Django cryptographic signing key | Development-only fallback |
| `DJANGO_DEBUG` | Enables Django debug mode | `True` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated accepted hosts | `localhost,127.0.0.1` |
| `DJANGO_CORS_ALLOWED_ORIGINS` | Comma-separated frontend origins | `http://localhost:4200` |

Never commit a real `.env` file, production secret, local SQLite database, or
uploaded media. These paths are excluded by `.gitignore`.

## API endpoints

All protected endpoints use token authentication:

```http
Authorization: Token <token>
```

### Authentication and profiles

| Method | Endpoint | Access |
|---|---|---|
| `POST` | `/api/registration/` | Public |
| `POST` | `/api/login/` | Public |
| `GET` | `/api/profile/{user_id}/` | Authenticated |
| `PATCH` | `/api/profile/{user_id}/` | Profile owner |
| `GET` | `/api/profiles/business/` | Authenticated |
| `GET` | `/api/profiles/customer/` | Authenticated |

### Offers

| Method | Endpoint | Access |
|---|---|---|
| `GET` | `/api/offers/` | Public |
| `POST` | `/api/offers/` | Business users |
| `GET` | `/api/offers/{id}/` | Authenticated |
| `PATCH` | `/api/offers/{id}/` | Offer owner |
| `DELETE` | `/api/offers/{id}/` | Offer owner |
| `GET` | `/api/offerdetails/{id}/` | Authenticated |

The offer list supports `creator_id`, `min_price`, `max_delivery_time`,
`search`, `ordering`, and `page_size`. Ordering is available for `updated_at`
and `min_price`.

### Orders

| Method | Endpoint | Access |
|---|---|---|
| `GET` | `/api/orders/` | Authenticated |
| `POST` | `/api/orders/` | Customer users |
| `PATCH` | `/api/orders/{id}/` | Associated business user |
| `DELETE` | `/api/orders/{id}/` | Staff users |
| `GET` | `/api/order-count/{business_user_id}/` | Authenticated |
| `GET` | `/api/completed-order-count/{business_user_id}/` | Authenticated |

### Reviews and platform information

| Method | Endpoint | Access |
|---|---|---|
| `GET` | `/api/reviews/` | Authenticated |
| `POST` | `/api/reviews/` | Customer users |
| `PATCH` | `/api/reviews/{id}/` | Review author |
| `DELETE` | `/api/reviews/{id}/` | Review author |
| `GET` | `/api/base-info/` | Public |

Reviews support `business_user_id` and `reviewer_id` filters, with ordering by
`updated_at` or `rating`.

## Quality checks

Install the development tools before running the full quality suite:

```bash
python -m pip install -r requirements-dev.txt
```

```bash
python manage.py check
python manage.py test
ruff check .
coverage run manage.py test
coverage report --fail-under=95
```

The repository test suite covers authentication, permissions, validation,
filtering, aggregation, CRUD behavior, HTTP status codes, and migration-backed
model behavior. The configured minimum coverage threshold is 95%.

## Production notes

Set a strong `DJANGO_SECRET_KEY`, disable debug mode, configure the deployed
host and frontend origin, and serve the application over HTTPS. Before a real
deployment, run `python manage.py check --deploy` and configure SSL redirect,
secure cookies, and HSTS in coordination with the reverse proxy. HSTS should
only be enabled after HTTPS is working correctly for the complete domain.

## Project structure

The Django project package is named `core`. Each domain app uses the required
`_app` suffix and owns an `api/` package for serializers, views, permissions,
and routes.

```text
core/          Django settings and central URL routing
auth_app/      Registration, login, and custom users
profile_app/   Customer and business profiles
offers_app/    Offers, tiers, filtering, and pagination
orders_app/    Order snapshots, workflow, and statistics
reviews_app/   Customer reviews and filtering
base_app/      Public platform aggregation
```
