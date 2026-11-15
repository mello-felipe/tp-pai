"""Backend HTTP (FastAPI) do PSE-Image: expõe o core para o frontend React."""
from .app import create_app

__all__ = ["create_app"]
