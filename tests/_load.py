"""Test helpers.

The upstream tests loaded scripts from skill folders. The tooling now lives
in tools/replkit, so this shim keeps the old call sites working while adding
the package to sys.path.
"""

import importlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)


def load(folder, name):
    """Return a replkit module. The folder argument is kept for compatibility."""
    return importlib.import_module("replkit." + name)
