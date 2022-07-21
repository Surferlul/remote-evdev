from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from typing import Generator

from . import guest
from . import host
from ..config import NetConfig, DeviceInfo


def get_streams(cfg: NetConfig) -> Generator[socket, None, None]:
    while True:
        with socket(AF_INET, SOCK_STREAM) as s:
            s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            if cfg.is_server:
                s.bind((cfg.ip_address, cfg.port))
                s.listen()
                while True:
                    conn, addr = s.accept()
                    with conn:
                        print(f"Connection established to {addr}")
                        yield conn
            else:
                s.connect((cfg.ip_address, cfg.port))
                print(f"Connection established to {cfg.ip_address}")
                yield s


def handle_client(s: socket, cfg: NetConfig, devices_info: list[DeviceInfo]):
    if cfg.is_host:
        host.handle_client(s, devices_info)
    else:
        guest.handle_client(s)
