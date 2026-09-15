"""Sleeps in select between bounded neural/sensor cycles; completely dormant when off."""
import json
import os
import selectors
import sys
import time
from .brain import Brain
from .body import Body
from .desktop import Hyprland,WindowCache
from .shelter import Shelters
from .pacing import Budget,FrameGate


def emit(payload):
    print(json.dumps(payload,separators=(",",":")),flush=True)


def main():
    sel=selectors.DefaultSelector();sel.register(sys.stdin,selectors.EVENT_READ)
    os.set_blocking(sys.stdin.fileno(),False)
    pending=b"";enabled=False;brain=None;desktop=Hyprland()
    body=Body();world=Shelters();windows=WindowCache(desktop)
    ticks=0;next_tick=0.;last=0.;metrics_deadline=0.
    monitors=[];frames=FrameGate();budget=Budget()
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
                        brain.last_cursor=None;frames.reset()
                        windows.enable()
                        metrics_deadline=0.
                        enabled=True;next_tick=last=time.monotonic()
                    elif command=="disable":
                        enabled=False
                        windows.close()
                        emit({"type":"state","enabled":False,"ticks":ticks,"queries":desktop.queries,
                              "window_events":False,"window_refreshes":windows.refreshes})
            if not enabled or time.monotonic()<next_tick:continue
            now=time.monotonic();cpu_start=time.process_time()
            dt=max(.001,min(.1,now-last));last=now
            try:
                if windows.refresh(now,world.attached is not None or brain.shelter_network.selected is not None):
                    monitors=windows.monitors
                    if not monitors:raise ValueError("No active monitors")
                    if ticks==0:
                        m=next((m for m in monitors if m["focused"]),monitors[0])
                        body.x=m["x"]+m["width"]*.6;body.y=m["y"]+m["height"]*.6
                cursor=desktop.cursor()
                x,y=body.x,body.y
                m=next((m for m in monitors if m["x"]<=x<m["x"]+m["width"] and m["y"]<=y<m["y"]+m["height"]),monitors[0])
                bounds=(m["x"],m["y"],m["width"],m["height"])
                world.sync(windows.windows,m,body)
                x,y=body.x,body.y
                command=brain.step(x,y,body.angle,cursor,bounds,body.effort,dt,
                                   world.entries,world.attached,world.exposure(body))
                pose=body.step(command,bounds,dt)
                world.contact((x,y),body,command)
                x,y=body.x,body.y
                ticks+=1
                snapshot={"type":"frame","visible":True,"x":round(x),"y":round(y),
                          "monitor":m["name"],"localX":round(x-m["x"]),"localY":round(y-m["y"]),
                          **pose}
                clips=world.clips(body)
                if world.attached:snapshot["clips"]=clips
                if not clips:snapshot={"type":"frame","visible":False}
                # No duplicate redraws or animation timer while the body is still.
                if frames.accept(snapshot,now):emit(snapshot)
                if now>=metrics_deadline:
                    metrics_deadline=now+1
                    emit({"type":"metrics","ticks":ticks,"queries":desktop.queries,
                                    "gf_hz":round(command["gf_hz"],2),"backend":"native-cpu",
                                    "mode":body.mode,"speed":round(command["speed"],2),
                                    "flight":round(command["flight"],3),"yaw":round(command["yaw"],3),
                                    "sheltered":world.attached is not None,"exposure":round(world.exposure(body),3),
                                    "shelter_candidates":len(world.entries),"window_refreshes":windows.refreshes,
                                    "window_events":windows.events is not None,
                                    "threat_memory":round(command["threat_memory"],3),"exit":round(command["exit"],3)})
                next_tick=budget.deadline(now,time.monotonic(),time.process_time()-cpu_start,body.mode!="rest")
            except (OSError,ValueError,KeyError) as exc:
                enabled=False;frames.reset()
                windows.close()
                emit({"type":"error","error":str(exc)})
    finally:
        windows.close()
        if brain:brain.close()
        sel.close()


if __name__=="__main__":main()
