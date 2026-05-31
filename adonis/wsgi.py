"""
WSGI config for Adonis project.
"""
import os
import sys

# Ensure the project root is on sys.path before any Django imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Install .pyc fallback loader so compiled bytecode is used when .py is absent
from adonis.pyc_loader import install as _install_pyc_loader
_install_pyc_loader()

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonis.settings')
application = get_wsgi_application()
