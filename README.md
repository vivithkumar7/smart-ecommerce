# Smart E-Commerce

Smart E-Commerce is a React storefront backed by a FastAPI API with MySQL,
JWT authentication, products, carts, orders, and Stripe or mock checkout.

## Project folders

- `fastapi_backend/`: FastAPI application, SQLAlchemy models, seed script, and backend tests.
- `frontend/`: React and Vite storefront.
- `postman/`: Importable API collection for manual endpoint testing.
- `django_admin/`: Reserved integration area and design notes for a future Django admin service.

## Run locally

### Backend

From `fastapi_backend`:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Configure the backend `.env` first. Use `CHECKOUT_MODE=mock` for local checkout
without Stripe. The API is available at `http://127.0.0.1:8000`; interactive
docs are at `/docs`.

### Sample catalog

With the backend running, from `fastapi_backend` run:

```powershell
python seed.py
```

### Frontend

From `frontend`:

```powershell
npm install
npm run dev
```

Open the Vite URL, normally `http://localhost:5173`.

## Verification

Backend smoke tests are in `fastapi_backend/test_*.py`. Frontend checks:

```powershell
npm run lint
npm run build
```

For manual API testing, import the collection from
`postman/Smart-Ecommerce.postman_collection.json`, run authentication first,
and then use the protected cart and checkout requests.

## Configuration and security

Never commit `.env`, database passwords, JWT secrets, or Stripe keys. See
`fastapi_backend/readme.txt` for the complete environment variable reference,
Stripe webhook setup, route list, and troubleshooting notes.
