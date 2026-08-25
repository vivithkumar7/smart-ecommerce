# Database migrations

The FastAPI project uses SQLAlchemy `create_all()` for its base tables and
checked-in SQL files for changes to existing tables.

Apply the user-management migration from a MySQL client before starting the
Django admin for the first time:

```sql
SOURCE migrations/001_user_roles_and_activation.sql;
```

This adds `role` (customer, staff, or admin) and `is_active` to `users`.
Existing users are assigned the customer role and remain active.
