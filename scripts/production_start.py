"""Collect versioned static assets, then replace this process with Gunicorn."""
import os
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
os.chdir(root)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.production")
subprocess.run([sys.executable, "manage.py", "check", "--deploy", "--fail-level", "WARNING"], check=True)
subprocess.run([sys.executable, "manage.py", "collectstatic", "--noinput"], check=True)
os.execvp("gunicorn", ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", os.environ.get("WEB_CONCURRENCY", "3"), "--timeout", "45", "--access-logfile", "-", "--error-logfile", "-"])
