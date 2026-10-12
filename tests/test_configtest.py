"""
Pytest configuration file
This file sets up the test environment and fixtures.
"""
import sys
import os

#  Add the project root and src directory to the Python path:
def test_root_path():

    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    result = root_path

    if root_path not in sys.path:
        sys.path.insert(0, root_path)
    assert result in sys.path

def test_src_path():
    root_path =  os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    src_path = os.path.join(root_path, 'src')

    result = src_path
    if result not in sys.path:
        sys.path.insert(0, src_path)

    assert root_path in sys.path
    assert src_path in sys.path

