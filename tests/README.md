# Application checks

Run `manage.py check_application` or `RUN_TESTS.bat`.

57 checks cover page rendering, real accounts/password reset, role enforcement,
workspace isolation, revoked membership, invitation lifecycle, request CRUD,
assignment ownership, notes/escaping, CSRF, archive/restore, optimistic edits,
queue persistence/real class calls/stale submissions, rollback, workflow methods,
filters/pagination, reports and safe CSV export.

These checks pass for both the runnable starter and instructor implementations.
Test users/data/passwords are disposable fixtures in Django's isolated test DB.
The MD5 hasher override is scoped to test fixtures; the application uses Django's
normal secure password hashing defaults. The goal tests in `challenge/` are
separate and intentionally fail until students implement both algorithms.
