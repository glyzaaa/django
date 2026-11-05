# Goal checks

CHECK_QUEUE.bat runs 10 FIFO checks; 7 fail on the untouched baseline.
CHECK_LINKED_LIST.bat runs 17 behavioral/structural checks; 7 fail initially.
CHECK_ACTIVITY.bat runs all 27 goal checks; 14 failures are expected initially.

Use the launchers, or `manage.py test challenge` with `.venv` Python. The Django
runner is required because some tests exercise real HTTP routes and database
records. The pure class tests and website tests share the same acceptance suite.

Do not change these files to hide failures. The final state must pass the
application suite and both goals. Read the assignment's complexity requirement
too; functional tests alone do not prove asymptotic performance.
