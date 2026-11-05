# Backend

- `accounts/`: actual Django accounts, custom User, registration/login, password
  reset, profiles, workspace switching and email-bound team invitations.
- `workspace/`: Django routes/views/forms, role guards, tenant middleware,
  context processors, transaction services and management commands.
- `dsa/`: the two student implementation files. The website calls these directly.

Start by tracing a queue form from `frontend/templates/queue.html` to
`workspace/urls.py`, `views.queue_serve`, `services.serve_next`, `dsa.queue`,
and the ORM models under `database/`.
