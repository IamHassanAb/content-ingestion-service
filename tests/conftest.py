# tests/conftest.py
import os
import sys

# Resolve absolute paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")

# Add both the root and src folders to sys.path
for path in [PROJECT_ROOT, SRC_PATH]:
    if path not in sys.path:
        sys.path.insert(0, path)
