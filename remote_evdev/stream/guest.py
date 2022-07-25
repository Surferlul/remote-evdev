from evdev import UInput
from socket import socket
import json
from typing import Generator
from ..config import DeviceType


class EventSequence:
    def __init__(self, name: str = "", sequence: list[tuple[int, int, int]] = None):
        if sequence is None:
            sequence = []
        self.name = name
        self.sequence = sequence
        self.curr = {}

    def add(self, event_type: int, event_code: int, event_value: int):
        self.sequence.append((event_type, event_code, event_value))

    def next(self, fd: int, event_type: int, event_code: int, event_value: int):
        if len(self.sequence) == 0:
            return True
        if fd not in self.curr:
            self.curr[fd] = 0
        if self.sequence[self.curr[fd]] == (event_type, event_code, event_value):
            self.curr[fd] += 1
            if self.curr[fd] == len(self.sequence):
                self.curr[fd] = 0
                return True
        else:
            self.curr[fd] = 0
        return False

    def reset(self):
        self.curr = {}


class SequenceCollection:
    def __init__(self, name: str = "", sequences: list[EventSequence] = None):
        if sequences is None:
            sequences = []
        self.name = name
        self.sequences = sequences

    def add(self, sequence: EventSequence):
        self.sequences.append(sequence)

    def next(self, *args):
        return sum([sequence.next(*args) for sequence in self.sequences])

    def reset(self):
        for sequence in self.sequences:
            sequence.reset()


def get_double_control_sequences() -> SequenceCollection:
    return SequenceCollection("doublecontrol", [
        EventSequence("rllr", [
            (4, 4, 29),
            (1, 29, 1),
            (0, 0, 0),
            (4, 4, 29),
            (0, 0, 0),
            (4, 4, 157)
        ]),
        EventSequence("lrrl", [
            (4, 4, 157),
            (1, 97, 1),
            (0, 0, 0),
            (4, 4, 157),
            (0, 0, 0),
            (4, 4, 29)
        ]),
        EventSequence("rlrl", [
            (4, 4, 29),
            (1, 29, 1),
            (0, 0, 0),
            (4, 4, 157),
            (0, 0, 0),
            (4, 4, 29)
        ]),
        EventSequence("lrlr", [
            (4, 4, 157),
            (1, 97, 1),
            (0, 0, 0),
            (4, 4, 29),
            (0, 0, 0),
            (4, 4, 157)
        ])
    ])


def receive_devices(s: socket) -> Generator[tuple[int, UInput], None, None]:
    while buf_size := int.from_bytes(s.recv(4), byteorder='big'):
        fd = int.from_bytes(s.recv(4), byteorder='big')
        device_type = DeviceType(int.from_bytes(s.recv(1), byteorder='big'))
        cap = json.loads(s.recv(buf_size).decode())
        cap = {int(key): cap[key] for key in cap}
        del cap[0]
        yield fd, UInput(cap, name=f"web-evdev-device-fd{fd}"), device_type


def receive_event(s: socket) -> tuple[int, tuple[int, int, int]]:
    fd = int.from_bytes(s.recv(4), byteorder='big')
    event_type = int.from_bytes(s.recv(4), byteorder='big')
    code = int.from_bytes(s.recv(4), byteorder='big')
    value = int.from_bytes(s.recv(8), byteorder='big', signed=True)
    return fd, (event_type, code, value)


def reset_control(d: dict[int: tuple[UInput, DeviceType]]):
    print("trying to reset controls")
    for fd in d:
        if d[fd][1] != DeviceType.KEYBOARD:
            continue
        print(f"resetting control keys on keyboard {fd}")
        for key in [29, 97]:
            d[fd][0].write(1, key, 0)
            d[fd][0].syn()


def handle_client(s: socket):
    control_sequences = get_double_control_sequences()
    d = {}
    for fd, device, device_type in receive_devices(s):
        d[fd] = (device, device_type)

    got_control = False
    while True:
        fd, event = receive_event(s)
        if fd == 4294967295:
            s.close()
            for fd in d:
                d[fd][0].close()
            print("Exiting")
            exit()
        elif fd == 4278124286:
            got_control = True
            control_sequences.reset()
            print("Control was given")
        elif fd == 4261281277:
            reset_control(d)
            print("Control was taken")
        else:
            if not got_control:
                if event[0] == 0:
                    d[fd][0].syn()
                else:
                    d[fd][0].write(*event)
            else:
                if d[fd][1] == DeviceType.KEYBOARD:
                    if control_sequences.next(fd, *event):
                        got_control = False
