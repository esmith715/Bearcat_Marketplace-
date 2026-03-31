# bearcat-marketplace/conftest.py  ← Note: project ROOT, not inside server/
import sys
import os

# Adds the project root to Python's path so "server" can be found
sys.path.insert(0, os.path.dirname(__file__))