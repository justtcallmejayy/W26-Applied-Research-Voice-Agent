import os
import sys

# 1. Get the absolute path of the 'tests' folder
tests_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Go up one level to the root project folder
project_root = os.path.dirname(tests_dir)

# 3. Target the 'src/app' folder where 'agent' lives
app_dir = os.path.join(project_root, 'src', 'app')

# 4. Inject it into Python's path BEFORE any tests run
sys.path.insert(0, app_dir)

print(f"\n[conftest.py] Added {app_dir} to Python path.")