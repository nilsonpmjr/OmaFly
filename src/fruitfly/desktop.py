"""Bounded Hyprland snapshots. Never spawn hyprctl in the sampling loop."""
import json
import os
import socket
from pathlib import Path


class Hyprland:
    def __init__(self):
        runtime=Path(os.environ["XDG_RUNTIME_DIR"])
        self.path=runtime/"hypr"/os.environ["HYPRLAND_INSTANCE_SIGNATURE"] / ".socket.sock"
        self.queries=0

    def query(self,command):
        with socket.socket(socket.AF_UNIX) as sock:
            sock.settimeout(.04)
            sock.connect(str(self.path));sock.sendall(("j/"+command).encode())
            chunks=[];size=0
            while True:
                chunk=sock.recv(65536)
                if not chunk:break
                size+=len(chunk)
                if size>2_000_000:raise ValueError("Compositor response exceeds limit")
                chunks.append(chunk)
        self.queries+=1
        return json.loads(b"".join(chunks))

    def monitors(self):
        out=[]
        for m in self.query("monitors"):
            width,height=m["width"],m["height"]
            if m.get("transform",0)%2:width,height=height,width
            out.append({"name":m["name"],"x":m["x"],"y":m["y"],
                        "width":width/m["scale"],"height":height/m["scale"],
                        "workspace":m.get("activeWorkspace",{}).get("id"),"focused":m.get("focused",False)})
        return out

    def cursor(self):
        pos=self.query("cursorpos")
        return float(pos["x"]),float(pos["y"])

    def windows(self):
        """Opt-in geometry snapshot. Never retain titles, classes or contents.

        These rectangles are not a guarantee of opacity or stacking order.
        Normal pet execution does not call this until shelter control is wired.
        """
        return [{"id":w["address"],"pid":w.get("pid"),
                 "rect":(*w["at"],*w["size"]),"workspace":w["workspace"]["id"],
                 "pinned":w.get("pinned",False)}
                for w in self.query("clients") if w.get("mapped") and not w.get("hidden")]
