import argparse
import json
import os
from pathlib import Path
import socket


def socket_path():
    return Path(os.environ.get("XDG_RUNTIME_DIR",f"/run/user/{os.getuid()}"))/"fruitfly"/"control.sock"


def request(command):
    with socket.socket(socket.AF_UNIX) as connection:
        connection.settimeout(2)
        connection.connect(str(socket_path()))
        connection.sendall((json.dumps({"command":command})+"\n").encode())
        data=b""
        while b"\n" not in data:
            part=connection.recv(4096)
            if not part:raise RuntimeError("Control connection closed")
            data+=part
            if len(data)>65536:raise RuntimeError("Control reply too large")
        return json.loads(data.split(b"\n",1)[0])


def main():
    parser=argparse.ArgumentParser(description="FruitFly experimental desktop pet")
    parser.add_argument("command",choices=["run","status","enable","disable","quit"],nargs="?",default="run")
    args=parser.parse_args()
    if args.command=="run":
        from .app import run
        return run()
    try:
        print(json.dumps(request(args.command),ensure_ascii=False,indent=2))
        return 0
    except (OSError,RuntimeError) as exc:
        parser.exit(1,f"FruitFly não está disponível: {exc}\n")


if __name__=="__main__":raise SystemExit(main())
