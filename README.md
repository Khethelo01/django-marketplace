# Marketplace - Django assignment

## Setup

Use Python 3.10 or newer. This project was verified with Python 3.14. Extract
the archive before running commands. From the folder containing manage.py:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8021
```

If activation is blocked, replace python with `.\.venv\Scripts\python.exe`.
For macOS/Linux, use `source .venv/bin/activate`. mysqlclient may require the
platform's MariaDB/MySQL client development libraries and compiler. An SQLite
quick trial needs only requirements.txt. The capstone's required MariaDB setup
is described below and was actually performed, not merely configured.

## MariaDB

The local verification used MariaDB 13.0.2, port 3307, with an isolated,
password-protected instance and dedicated users. Credentials and database
files are not included. On another machine, create an utf8mb4 database and
a dedicated account, grant that account privileges on its own database and
on `test_marketplace` for Django's temporary test database, then set:

```powershell
$env:DB_ENGINE = "mariadb"
$env:DB_NAME = "marketplace"
$env:DB_USER = "YOUR_LOCAL_DATABASE_USER"
$env:DB_PASSWORD = "YOUR_LOCAL_DATABASE_PASSWORD"
$env:DB_HOST = "127.0.0.1"
$env:DB_PORT = "3307"
python manage.py migrate
python manage.py check --database default
python manage.py test shop -v 2
```

The SQLite fallback is for easy preview. Keep DB_ENGINE=mariadb when reviewing
the actual capstone database. See mariadb_verification.txt for recorded migration
and test output. Migration files are included and must not be deleted.

## Accounts and email

No real credentials, private tokens or user databases are in the submission.
Register a normal account through /register/. The application uses Django
sessions for browser login. Optional admin is at /admin/ after createsuperuser.
Passwords use Django hashing and validation. Password recovery is at
/accounts/password_reset/ with a 15-minute, invalidated-after-use token.

Console email is the safe default: messages appear in the server terminal.
To use real SMTP, set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend,
EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_USE_TLS and
DEFAULT_FROM_EMAIL as environment variables. Do not commit real credentials.
No real recipients were emailed during verification.

## Tests and development checks

```text
python manage.py test shop -v 2
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py collectstatic --noinput
python -m flake8 .
```

Tests use isolated databases; external HTTP and email failures are mocked.
The suite was run on both SQLite and MariaDB. Manual browser checks and live
integration results are recorded in verification.txt. CSS and templates work
without remote fonts or CDNs. Source is split into models, forms, views,
services, serializers, routing, policies where applicable, and tests.

## Planning and submission

Planning/design.md maps requirements to workflows, authorisation and data.
Planning/design_diagrams.pdf includes use case, sequence and class/relational
diagrams. requirements files pin runtime and development dependencies.
Generated databases, virtual environments, caches, static collection copies
and private configuration are excluded from the ZIP.

This is local coursework, not a deployed production service. Production needs
HTTPS, a private DJANGO_SECRET_KEY, DJANGO_DEBUG=0, approved hosts, suitable
deployment infrastructure, rate limiting and backups. Do not expose the
development server publicly.

## eCommerce Part 1 and Part 2

The Part 1 archive covers the complete storefront, buyer/vendor permissions,
session carts, checkout, invoices, reviews and password reset. The Part 2 archive
is a cumulative extension and also includes its protected REST API and the
JSONPlaceholder integration. Both snapshots include the complete working app;
extra Part 2 functionality does not remove any Part 1 feature.

Register as either buyer or vendor. Vendor dashboard manages stores/products.
Buyer dashboard lists invoices. Checkout records a coursework order; it does
not charge money. Purchase verification is derived from OrderItem records.
Invoice prices are historical snapshots. Failed email can be retried from the
invoice screen without placing another order. No payment gateway is required.

The research_answers.md file answers all three research questions and lists
four advantages and four disadvantages each for JSON, XML and RESTful APIs.
Part 2 routes are documented in Planning/design.md. Get a token with
POST /api/token/ (username/password) then send Authorization: Token YOUR_TOKEN.

Visit /external-posts/ for real JSONPlaceholder sample posts, or
/external-posts/?user_id=1 for filtering. The helper is in
shop/functions/jsonplaceholder.py. Network/status/JSON failures show a fallback.
pip-system-certs uses the operating system certificate store; TLS verification
remains enabled. Live testing returned ten posts, all with user ID 1.
