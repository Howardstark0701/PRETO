#!/usr/bin/env python
"""Install auth dependencies"""

import subprocess
import sys

packages = [
    'passlib',
    'bcrypt',
]

for package in packages:
    print(f"Installing {package}...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        print(f"✓ {package} installed")
    except Exception as e:
        print(f"✗ Failed to install {package}: {e}")

print("\nAll dependencies installed!")
