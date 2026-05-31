"""
Optional production overrides that can be imported from adonis/settings.py
if you choose a split-settings approach in the future.
"""

from django.core.exceptions import ImproperlyConfigured


def enforce_production(db_engine: str):
    if db_engine != "postgres":
        raise ImproperlyConfigured("Production must use PostgreSQL (DB_ENGINE=postgres).")
