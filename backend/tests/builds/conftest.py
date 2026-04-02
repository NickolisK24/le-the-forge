"""
Conftest for builds/ sub-test package.
Ensures the backend root is on sys.path so `builds.*` imports resolve.
"""
import sys
import os

# Add backend root so `builds`, `encounter`, `app` are all importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
