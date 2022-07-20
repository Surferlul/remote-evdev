from evdev import UInput
from socket import socket
import json
from typing import Generator


def receive_devices(s: socket) -> Generator[tuple[int, UInput], None, None]:
    while buf_size := int.from_bytes(s.recv(4), byteorder='big'):
        fd = int.from_bytes(s.recv(4), byteorder='big')
        cap = json.loads(s.recv(buf_size).decode())
        cap = {int(key): cap[key] for key in cap}
        del cap[0]
        yield fd, UInput(cap, name=f"web-evdev-device-fd{fd}")


def receive_event(s: socket) -> tuple[int, tuple[int, int, int]]:
    fd = int.from_bytes(s.recv(4), byteorder='big')
    event_type = int.from_bytes(s.recv(4), byteorder='big')
    code = int.from_bytes(s.recv(4), byteorder='big')
    value = int.from_bytes(s.recv(8), byteorder='big', signed=True)
    return fd, (event_type, code, value)


def handle_client(s: socket):
    devices = {}
    for fd, device in receive_devices(s):
        devices[fd] = device

    while True:
        fd, event = receive_event(s)
        if fd == 4294967295:
            break
        elif event[0] == 0:
            devices[fd].syn()
        else:
            devices[fd].write(*event)