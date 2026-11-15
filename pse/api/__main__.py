"""Sobe o backend em desenvolvimento:  python -m pse.api [porta]"""
import sys

import uvicorn

from . import create_app

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    uvicorn.run(create_app(), host="127.0.0.1", port=port)
