"""
Run script for the scheduler application
This script sets up the Python path correctly and runs the application
"""

import os
import sys

# Add the parent directory to the Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import and run the application
from scheduler_app.myapp import run_server

if __name__ == '__main__':
    run_server()

