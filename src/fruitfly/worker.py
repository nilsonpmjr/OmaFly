"""Sleeps in select between bounded neural/sensor cycles; completely dormant when off."""
import json
import os
import selectors
import sys
import time
from .brain import Brain
from .body import Body
from .desktop import Hyprland
from .pacing import Budget


def emit(payload):
    print(json.dumps(payload,separators=(",",":")),flush=True)


def main():
    sel=selectors.DefaultSelector();sel.register(sys.stdin,selectors.EVENT_READ)
    os.set_blocking(sys.stdin.fileno(),False)
    pending=b"";enabled=False;brain=None;desktop=Hyprland()
    body=Body();ticks=0;next_tick=0.;monitor_deadline=0.;last=0.
    monitors=[];last_snapshot=None;budget=Budget()
    try:
        while True:
            timeout=max(0,next_tick-time.monotonic()) if enabled else None
            for _,_mask in sel.select(timeout):
                data=os.read(sys.stdin.fileno(),4096)
                if not data:return
                pending+=data
                if len(pending)>8192:raise ValueError("Control message too large")
                while b"\n" in pending:
                    line,pending=pending.split(b"\n",1)
                    command=json.loads(line).get("command")
                    if command=="quit":return
                    if command=="enable":
                        if not brain:brain=Brain()
                        brain.last_cursor=None;last_snapshot=None
                        enabled=True;monitor_deadline=0.;next_tick=last=time.monotonic()
                    elif command=="disable":
                        enabled=False
                        emit({"type":"state","enabled":False,"ticks":ticks,"queries":desktop.queries})
            if not enabled or time.monotonic()<next_tick:continue
            now=time.monotonic();cpu_start=time.process_time()
            dt=max(.001,min(.1,now-last));last=now
            try:
                if now>=monitor_deadline:
                    monitors=desktop.monitors();monitor_deadline=now+2
                    if not monitors:raise ValueError("No active monitors")
                    if ticks==0:
                        m=next((m for m in monitors if m["focused"]),monitors[0])
                        body.x=m["x"]+m["width"]*.6;body.y=m["y"]+m["height"]*.6
                cursor=desktop.cursor()
                x,y=body.x,body.y
                m=next((m for m in monitors if m["x"]<=x<m["x"]+m["width"] and m["y"]<=y<m["y"]+m["height"]),monitors[0])
                bounds=(m["x"],m["y"],m["width"],m["height"])
                command=brain.step(x,y,body.angle,cursor,bounds,body.effort,dt)
                pose=body.step(command,bounds,dt)
                x,y=body.x,body.y
                ticks+=1
                snapshot={"type":"frame","visible":True,"x":round(x),"y":round(y),
                          "monitor":m["name"],"localX":round(x-m["x"]),"localY":round(y-m["y"]),
                          **pose}
                # No duplicate redraws or animation timer while the body is still.
                if snapshot!=last_snapshot:emit(snapshot);last_snapshot=snapshot
                if ticks%25==0:emit({"type":"metrics","ticks":ticks,"queries":desktop.queries,
                                    "gf_hz":round(command["gf_hz"],2),"backend":"native-cpu",
                                    "mode":body.mode,"speed":round(command["speed"],2),
                                    "flight":round(command["flight"],3),"yaw":round(command["yaw"],3)})
                next_tick=budget.deadline(now,time.monotonic(),time.process_time()-cpu_start,body.mode!="rest")
            except (OSError,ValueError,KeyError) as exc:
                enabled=False;last_snapshot=None
                emit({"type":"error","error":str(exc)})
    finally:
        if brain:brain.close()
        sel.close()


if __name__=="__main__":main()
