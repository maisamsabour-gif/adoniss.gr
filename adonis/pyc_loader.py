"""
Import hook: loads compiled .pyc files when the corresponding .py source is
missing.  This is a recovery mechanism for cases where source files are lost
but the __pycache__ bytecode files are still present.

Install this hook BEFORE django.setup() by importing it in wsgi.py / asgi.py.
"""

import importlib.abc
import importlib.machinery
import importlib.util
import os
import sys

# Modules whose .py source files may be absent — loaded from __pycache__ instead
_SOURCELESS_MODULES = {
    'core.models',
    'core.admin',
    'core.views',
    'core.urls',
    'core.context_processors',
    'core.sitemaps',
}


class _PycFallbackFinder(importlib.abc.MetaPathFinder):
    """Fall back to the compiled .pyc when the .py source is absent."""

    def find_spec(self, fullname, path, target=None):
        if fullname not in _SOURCELESS_MODULES:
            return None
        if path is None:
            return None
        for search_path in path:
            module_name = fullname.rsplit('.', 1)[-1]
            py_path = os.path.join(search_path, f'{module_name}.py')
            # Only use .pyc fallback when the .py source is absent
            if os.path.exists(py_path):
                return None
            pyc_path = os.path.join(
                search_path, '__pycache__',
                f'{module_name}.cpython-312.pyc',
            )
            if os.path.exists(pyc_path):
                loader = importlib.machinery.SourcelessFileLoader(fullname, pyc_path)
                spec = importlib.util.spec_from_loader(fullname, loader, origin=pyc_path)
                return spec
        return None


def install():
    """Install the pyc fallback finder (idempotent)."""
    for finder in sys.meta_path:
        if isinstance(finder, _PycFallbackFinder):
            return  # already installed
    sys.meta_path.insert(0, _PycFallbackFinder())
