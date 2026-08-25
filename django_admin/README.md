# Django Admin

This is a standalone Django admin service for the existing FastAPI and
SQLAlchemy application. It maps the existing MySQL tables without taking
ownership of the customer-facing API.

## Run locally

From the repository root, open a terminal and run:

```powershell
cd django_admin
..\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py check
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8001
```

Before opening Store users, apply
`fastapi_backend/migrations/001_user_roles_and_activation.sql` to the shared
MySQL database. The migration adds `role` and `is_active` to storefront users.
The Store users form supports Customer, Staff, and Admin roles and account
activation/deactivation. Deactivated users cannot use the FastAPI storefront.

For a non-interactive superuser setup, run this entire block in the same
terminal. The password is not displayed by PowerShell when you type it:

```powershell
$env:DJANGO_SUPERUSER_USERNAME = "admin"
$env:DJANGO_SUPERUSER_EMAIL = "admin@example.com"
$env:DJANGO_SUPERUSER_PASSWORD = "Admin@12345"
python manage.py createsuperuser --noinput
Remove-Item Env:DJANGO_SUPERUSER_USERNAME, Env:DJANGO_SUPERUSER_EMAIL, Env:DJANGO_SUPERUSER_PASSWORD
```

If the user already exists, Django will report that it already exists; start
the server and log in with that account instead.

Open `http://127.0.0.1:8001/admin/`. The admin reads `DATABASE_URL` from
`fastapi_backend/.env`, so start MySQL and make sure the FastAPI environment
file is configured first. Use a different port from FastAPI if the API is
already running on port 8000.

Log in with the Django admin username created by `createsuperuser` (for the
default setup this is `admin`, not the storefront email or storefront user
name). Storefront users in the `users` table are not Django staff accounts and
cannot log in to `/admin/`.

The Django auth tables are used only for admin login. The storefront `users`
table is shown as `StoreUser`; its email and password can be edited from the
admin form. Passwords are hashed with `pbkdf2_sha256`, matching FastAPI.

## Analytics and reports

Open `http://127.0.0.1:8001/admin/analytics/` while logged in as staff. The
dashboard shows total sales, revenue trends, top-selling products, and low
stock alerts using Chart.js. It also provides Orders, Sales, and Users exports
as CSV and PDF.

Product creation supports name, description, category, price, stock,
popularity, active status, image URL, and local image upload. Uploaded images
are stored under `django_admin/media/products/`.

## Planned responsibilities

- Manage products, stock, and active catalog status.
- Review users, orders, and payment status.
- Use the same database only after the SQLAlchemy and Django model mappings
  have been reviewed and migrations are defined.

## Integration rules

1. Keep customer-facing API behavior in `fastapi_backend/app`.
2. Add Django models with an explicit migration strategy before connecting this
   service to the production database.
3. Do not commit database credentials or Django `SECRET_KEY` values. Store them
   in environment variables.
4. Protect the admin service separately with staff authentication and network
   access controls.

See the root README for the FastAPI and frontend setup.
