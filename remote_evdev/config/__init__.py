from dataclasses import dataclass
import sys
from os import path


@dataclass
class DeviceInfo:
    path: str
    device_type: str


@dataclass
class NetConfig:
    is_server: bool
    is_host: bool
    port: int
    ip_address: str


def get_config() -> tuple[NetConfig, list[DeviceInfo]]:
    args = sys.argv

    cfg = NetConfig(
        is_server=False,
        is_host=True,
        port=64654,
        ip_address="auto"
    )
    devices_info = []

    n = 1
    while n < len(args):
        match args[n]:
            case "-s" | "--server": cfg.is_server = True
            case "-c" | "--client": cfg.is_server = False
            case "-h" | "--host": cfg.is_host = True
            case "-g" | "--guest": cfg.is_host = False
            case "-p" | "--port":
                n += 1
                try:
                    cfg.port = int(args[n])
                except ValueError:
                    raise ValueError(f"Port must be a integer, not {args[n]}")
            case "-a" | "--ip-address":
                cfg.ip_address = args[n := n+1]
            case "-d" | "--device":
                devices_info.append(DeviceInfo(
                    path="",
                    device_type="other"
                ))
            case _:
                key = "path"
                value = ""
                match args[n]:
                    case "--id": value = "/dev/input/by-id/"
                    case "--path": value = "/dev/input/by-path/"
                    case "--event": value = "/dev/input/"
                    case "--full-path": pass
                    case "--type":
                        match args[n+1]:
                            case "pointer" | "keyboard": key = "type"
                            case _: raise ValueError(f"Invalid device type {args[n+1]}")
                n += 1
                match key:
                    case "path":
                        value = f"{value}{args[n]}"
                        if path.exists(value):
                            devices_info[-1].path = value
                    case "type": devices_info[-1].device_type = args[n]
        n += 1

    if cfg.ip_address == "auto":
        raise ValueError(f"Auto IP address not implemented yet")

    return cfg, devices_info
