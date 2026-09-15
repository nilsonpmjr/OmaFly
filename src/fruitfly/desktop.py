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
                        "workspace":m.get("activeWorkspace",{}).get("id"),
                        "special_workspace":m.get("specialWorkspace",{}).get("id",0),"focused":m.get("focused",False)})
        return out

    def cursor(self):
        pos=self.query("cursorpos")
        return float(pos["x"]),float(pos["y"])

    def windows(self,include_hidden=False):
        """Opt-in geometry snapshot. Never retain titles, classes or contents.

        These rectangles are not a guarantee of opacity or stacking order.
        WindowCache limits acquisition in normal execution.
        """
        return [{"id":w["address"],"pid":w.get("pid"),
                 "rect":(*w["at"],*w["size"]),"workspace":w["workspace"]["id"],
                 "pinned":w.get("pinned",False)}
                for w in self.query("clients") if w.get("mapped") and (include_hidden or not w.get("hidden"))]


class WindowCache:
    """Event-coalesced snapshots: <=5 Hz tracking, 0.5 Hz fallback when idle.

    socket2 is drained once per existing worker cycle, never a separate wakeup.
    Geometry-changing drags need bounded polling because events are incomplete.
    """
    relevant={b'openwindow',b'closewindow',b'movewindow',b'movewindowv2',b'workspace',
              b'workspacev2',b'activespecial',b'activespecialv2',b'monitoradded',
              b'monitorremoved',b'changefloatingmode',b'fullscreen',b'pin'}

    def __init__(self,desktop):
        self.desktop=desktop;self.events=None;self.buffer=b'';self.dirty=True
        self.next_refresh=0.;self.last_refresh=float('-inf');self.windows=[];self.monitors=[]
        self.refreshes=0

    def enable(self):
        self.close();self.dirty=True;self.next_refresh=0.;self.last_refresh=float('-inf')
        sock=socket.socket(socket.AF_UNIX)
        try:
            sock.settimeout(.04);sock.connect(str(self.desktop.path.with_name('.socket2.sock')))
            sock.setblocking(False);self.events=sock
        except OSError:sock.close()  # Bounded polling remains available without events.

    def close(self):
        if self.events:self.events.close();self.events=None
        self.buffer=b''

    def refresh(self,now,tracking=False):
        if self.events:
            try:
                data=self.events.recv(8192)
                if not data:self.close();self.dirty=True
                else:
                    self.buffer+=data
                    lines=self.buffer.split(b'\n');self.buffer=lines.pop()
                    if len(self.buffer)>8192:self.buffer=b'';self.dirty=True
                    if any(line.split(b'>>',1)[0] in self.relevant for line in lines):self.dirty=True
            except BlockingIOError:pass
            except OSError:self.close();self.dirty=True
        due=self.dirty or now-self.last_refresh>=(.2 if tracking else 2.)
        if due and now>=self.next_refresh:
            # Workspace and geometry are refreshed together; never retain window text.
            monitors=self.desktop.monitors();windows=self.desktop.windows()
            self.monitors=monitors;self.windows=windows
            self.last_refresh=now;self.next_refresh=now+.2;self.dirty=False;self.refreshes+=1
            return True
        return False
