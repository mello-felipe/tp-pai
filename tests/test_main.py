import socket

import main


def test_pick_port_prefers_free_port():
    free = main.pick_port(0)
    assert main.pick_port(free) == free


def test_pick_port_falls_back_when_busy():
    with socket.socket() as s:
        s.bind((main.HOST, 0))
        s.listen()
        busy = s.getsockname()[1]
        port = main.pick_port(busy)
    assert port != busy and port > 0
