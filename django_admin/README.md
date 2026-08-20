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

For a non-interactive superuser setup, run this entire block in the same
terminal. The password is not displayed by PowerShell when you type it:

```powershell
$env:DJANGO_SUPERUSER_USERNAME = "admin"
$env:DJANGO_SUPERUSER_EMAIL = "admin@example.com"
$env:DJANGO_SUPERUSER_PASSWORD = "UseYourOwnStrongPassword"
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
