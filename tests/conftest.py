"""
Minimal conftest.py - path handled by pytest.ini (venv)
"""
import pytest

@pytest.fixture
def sample_data()-> dict[str, str]:
    return {"key": "value"}

try:
    from fastapi import FastAPI
    import gradio as gr
    if not hasattr(FastAPI, "close"):
        FastAPI.close = lambda self: gr.close_all()
except ImportError:
    pass 