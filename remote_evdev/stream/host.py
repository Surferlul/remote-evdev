from socket import socket
from evdev import InputDevice, InputEvent
from select import select
import json

from ..config import DeviceInfo


def send_device(s: socket, device: InputDevice):
    buf = json.dumps(device.capabilities()).encode()
    s.sendall(len(buf).to_bytes(4, byteorder='big'))
    s.sendall(device.fd.to_bytes(4, byteorder='big'))
    s.sendall(buf)


def send_input_event(s: socket, fd: int, input_event: InputEvent):
    s.sendall(fd.to_bytes(4, byteorder='big'))
    s.sendall(input_event.type.to_bytes(4, byteorder='big'))
    s.sendall(input_event.code.to_bytes(4, byteorder='big'))
    s.sendall(input_event.value.to_bytes(8, byteorder='big', signed=True))


def handle_client(s: socket, devices_info: list[DeviceInfo]):
    devices = []
    for device_info in devices_info:
        devices.append(InputDevice(device_info.path))
        devices[-1].grab()
        send_device(s, devices[-1])
    s.sendall((0).to_bytes(4, byteorder='big'))
    devices = {device.fd: device for device in devices}
    while True:
        r, w, x = select(devices, [], [])
        for fd in r:
            for event in devices[fd].read():
                send_input_event(s, fd, event)
    s.sendall(b'\xff'*20)
    for device in devices:
       device.ungrab()
