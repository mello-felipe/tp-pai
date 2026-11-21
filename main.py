from __future__ import annotations

import socket
import threading
import webbrowser

import uvicorn

from pse.api import create_app
from pse.api.static import frontend_dist

HOST = "127.0.0.1"
PREFERRED_PORT = 8000


def pick_port(preferred: int = PREFERRED_PORT) -> int:
    for port in (preferred, 0):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((HOST, port))
            except OSError:
                continue
            return s.getsockname()[1]
    raise OSError("nenhuma porta livre")


def main() -> None:
    static = frontend_dist()
    port = pick_port()
    url = f"http://{HOST}:{port}"
    if static:
        print(f"PSE-Image em {url} (feche esta janela para encerrar)")
        threading.Timer(1.5, webbrowser.open, args=(url,)).start()
    else:
        print("Frontend não compilado: rode 'npm run build' em frontend/ "
              f"ou use 'npm run dev'. Backend em {url}")
    uvicorn.run(create_app(static_dir=static), host=HOST, port=port)


if __name__ == "__main__":
    main()
