"""
Pytest configuration file
This file sets up the test environment and fixtures.
"""
import sys
import os

#  Add the project root and src directory to the Python path:
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

src_path = os.path.join(root_path, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)
