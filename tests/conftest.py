"""
tests.conftest

Pytest configuration - adds project root and src/app to sys.path so
all test modules can import from src.app.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "src" / "app"))