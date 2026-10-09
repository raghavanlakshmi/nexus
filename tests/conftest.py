"""Make the agents importable offline: no API keys, no Pinecone connection."""
import os
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Agents construct an Anthropic client at import time; a placeholder key is enough
# because these tests never make a real call.
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

# tools.pinecone_store connects to Pinecone on import, so replace it with a stub.
_pinecone_stub = types.ModuleType("tools.pinecone_store")
_pinecone_stub.__getattr__ = lambda name: (lambda *a, **k: None)  # any store/retrieve call is a no-op
sys.modules["tools.pinecone_store"] = _pinecone_stub
