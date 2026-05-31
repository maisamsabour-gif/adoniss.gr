#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def _guard_destructive_commands():
    env = os.getenv('ENV', 'development').lower()
    if env != 'production':
        return

    if len(sys.argv) < 2:
        return

    dangerous_commands = {
        'flush',
        'sqlflush',
        'reset_db',
        'resetdb',
        'dropdb',
        'cleardb',
    }
    command = sys.argv[1].lower()
    if command in dangerous_commands and os.getenv('ALLOW_DESTRUCTIVE_COMMANDS') != '1':
        raise SystemExit(
            f'Blocked dangerous command "{command}" in production. '
            'Set ALLOW_DESTRUCTIVE_COMMANDS=1 only for controlled maintenance windows.'
        )


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonis.settings')
    _guard_destructive_commands()
    # Install .pyc fallback loader (recovery mode when .py source is absent)
    try:
        from adonis.pyc_loader import install as _install_pyc
        _install_pyc()
    except Exception:
        pass
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
