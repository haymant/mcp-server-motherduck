"""
Vercel Python Functions entrypoint.

Re-exports the ASGI app from the backend module so Vercel's Python runtime
can discover the `app` callable at the expected location.
"""
import sys
from pathlib import Path

# Ensure the project root and the src/ directory are on sys.path so the
# local (modified) mcp_server_motherduck package is found *before* any
# PyPI-installed version.
_project_root = str(Path(__file__).resolve().parent.parent)
_src_path = str(Path(__file__).resolve().parent.parent / "src")
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)

from backend.main import app  # noqa: E402, F401
