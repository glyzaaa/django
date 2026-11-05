# Database

`models.py`: Workspace, Membership, Ticket, Comment, Event, Invitation and
LoginThrottle. `admin.py`: configured Django admin. `migrations/`: schema history.
The custom User model has its own Django app/migration in `backend/accounts/`.

Local data is generated in `data/flowdesk.sqlite3`, together with a private local
development signing key. Both are excluded from the archive and Git.

Run `manage.py migrate`; never manually create tables. `config/production.py`
uses PostgreSQL with the same ORM schema and row locks. Read `docs/DEPLOYMENT.md`
for backups and production validation. An old anonymous-edition SQLite database
is not a drop-in replacement for this edition's account schema.
