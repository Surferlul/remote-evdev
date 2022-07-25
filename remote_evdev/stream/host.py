from socket import socket
from evdev import InputDevice, InputEvent
from select import select
import json
from time import time

from ..config import DeviceInfo, DeviceType


def send_device(s: socket, device: InputDevice, device_type: DeviceType):
    buf = json.dumps(device.capabilities()).encode()
    s.sendall(len(buf).to_bytes(4, byteorder='big'))
    s.sendall(device.fd.to_bytes(4, byteorder='big'))
    s.sendall(device_type.value.to_bytes(1, byteorder='big'))
    s.sendall(buf)


def send_input_event(s: socket, fd: int, input_event: InputEvent):
    s.sendall(fd.to_bytes(4, byteorder='big'))
    s.sendall(input_event.type.to_bytes(4, byteorder='big'))
    s.sendall(input_event.code.to_bytes(4, byteorder='big'))
    s.sendall(input_event.value.to_bytes(8, byteorder='big', signed=True))


def exit_nice(s: socket, d: dict[int: InputDevice], guest_input: bool):
    s.sendall(b'\xff' * 20)
    if guest_input:
        for fd in d:
            d[fd].ungrab()
    s.close()
    print("Exiting")
    exit()


def give_control(s: socket, d: dict[int: InputDevice]):
    s.sendall(b'\xfe' * 20)
    print("Giving up control")
    prnt = time()
    while True:
        for fd in d:
            if d[fd].active_keys():
                break
        else:
            break
        if time() > prnt:
            print("Let go of all keys!")
            prnt += 1
        continue
    for fd in d:
        d[fd].grab()
    print("Ready")


def take_control(s: socket, d: dict[int: InputDevice]):
    print("Taking control")
    s.sendall(b'\xfd' * 20)
    for fd in d:
        d[fd].ungrab()


def double_control(s: socket,
                   d: dict[int: InputDevice],
                   active_keys: list[int],
                   guest_input: bool,
                   ctrl2: bool) -> bool:
    if 14 in active_keys:
        exit_nice(s, d, guest_input)
    elif not ctrl2:
        guest_input = not guest_input
        if guest_input:
            give_control(s, d)
        else:
            take_control(s, d)
    return guest_input


def handle_client(s: socket, devices_info: list[DeviceInfo]):
    ctrl2 = False
    guest_input = True
    d = []
    device_types = {}
    for device_info in devices_info:
        device = InputDevice(device_info.path)
        d.append(device)
        device_types[device.fd] = device_info.device_type
        send_device(s, device, device_info.device_type)
    s.sendall((0).to_bytes(4, byteorder='big'))
    d = {device.fd: device for device in d}
    give_control(s, d)
    while True:
        r, w, x = select(d, [], [])
        for fd in r:
            events = [event for event in d[fd].read()]
            if device_types[fd] == DeviceType.KEYBOARD:
                active_keys = d[fd].active_keys()
                if 29 in active_keys and 97 in active_keys:
                    guest_input = double_control(s, d, active_keys, guest_input, ctrl2)
                    ctrl2 = True
                else:
                    ctrl2 = False
            if guest_input:
                for event in events:
                    send_input_event(s, fd, event)
