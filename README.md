# Marketplace - eCommerce Part 1 and Part 2

## Windows setup: copy and paste in PowerShell

Install Python 3.10+ and Git first. Open **Windows Terminal > PowerShell**
from the Start menu. Run all commands below in that same PowerShell window.

### 1. Clone and enter the project

```powershell
git clone https://github.com/Khethelo01/django-marketplace.git
cd django-marketplace
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

Activation is not necessary because every command uses the virtual environment
interpreter explicitly. If reviewing the submission ZIP, extract it and open
PowerShell inside the extracted marketplace folder instead of cloning.

### 2. Install and start MariaDB

```powershell
winget install --id MariaDB.Server --exact --source winget
```

Complete the installer, choose and remember a root password, and enable its
database service. Use the port shown by the installer (normally 3306).
If already installed, skip installation. Locate the client executable:

```powershell
$MariaDB = (Get-ChildItem "C:\Program Files\MariaDB*\bin\mariadb.exe" | Select-Object -First 1).FullName
& $MariaDB -u root -p
```

Enter the root password when prompted. You are now at the **MariaDB SQL prompt**,
not PowerShell. Copy these SQL statements; replace the sample password with
your own local development password in both this SQL and the next section.

```sql
CREATE DATABASE marketplace CHARACTER SET utf8mb4;
CREATE USER 'marketplace_app'@'127.0.0.1' IDENTIFIED BY 'ReplaceWithYourLocalPassword';
GRANT ALL PRIVILEGES ON marketplace.* TO 'marketplace_app'@'127.0.0.1';
GRANT ALL PRIVILEGES ON test_marketplace.* TO 'marketplace_app'@'127.0.0.1';
EXIT;
```

The test database grant allows Django to create and remove its isolated test
database. Use these names only for this project. If a database/user already
exists, reuse it rather than deleting it or blindly repeating CREATE.

### 3. Set credentials in the SAME PowerShell window

```powershell
$env:DB_NAME = "marketplace"
$env:DB_USER = "marketplace_app"
$env:DB_PASSWORD = "ReplaceWithYourLocalPassword"
$env:DB_HOST = "127.0.0.1"
$env:DB_PORT = "3306"
```

Use your actual password and port. These are PowerShell environment variables,
read directly by config/settings.py. They last for this window and its child
processes; repeat this section when opening another terminal. No DB_ENGINE
switch is needed: MariaDB is the sole configured database. There is no SQLite
fallback. Never commit passwords or credentials to GitHub.

### 4. Migrate, test and run (still in PowerShell)

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py check --database default
.\.venv\Scripts\python.exe manage.py test shop -v 2
.\.venv\Scripts\python.exe manage.py collectstatic --noinput
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8021
```

Open http://127.0.0.1:8021/ in your browser. Register as a buyer or vendor.
Press Ctrl+C in PowerShell to stop the server. Optional admin creation:

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

An access-denied error means the password or host account differs from the SQL
setup. Connection refused means MariaDB is stopped or DB_PORT is wrong. A missing
table means migrate has not completed. Do not switch databases to hide errors.
The local verification used MariaDB on port 3307; use your own installation's
port as shown above. Linux/macOS reviewers need their platform's MariaDB server,
client development packages and equivalent shell environment-variable syntax.

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
The revised suite is verified against MariaDB only. Manual browser checks and live
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


## Part 2 review update

Buyer menu: Vendors -> vendor stores -> store products; Stores -> store
products; Products -> all products. Vendor menu: Stores -> owned stores and
their products; Products -> all owned products; Reviews -> feedback across
all owned stores in one place. The protected /api/reviews/ endpoint continues
to provide the same vendor-wide review retrieval for API clients.

The assessor requires a successful Part 1 review before Part 2 resubmission.
This update uses the corrected Part 1 code, but do not request Part 2 review
until Part 1 has been approved. No successful review is claimed here.
