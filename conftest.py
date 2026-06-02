"""Root conftest — runs before any test module is imported.

1. Adds the project root to sys.path so `import src.*` resolves.
2. Installs a lightweight streamlit mock so @st.cache_data in src/fetch.py
   acts as a pass-through and does not require a running Streamlit server.
"""

import os
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(__file__))

if "streamlit" not in sys.modules:
    _st = MagicMock()
    _st.cache_data = lambda *args, **kwargs: (lambda f: f)
    sys.modules["streamlit"] = _st
