#!/usr/bin/env python3
"""Bounded visible smoke test: off -> on -> off; always closes its own instance."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from fruitfly.__main__ import request,socket_path


def process_stats(pid):
    pids=[pid];result={}
    while pids:
        current=pids.pop()
        try:
            stat=Path(f"/proc/{current}/stat").read_text().rsplit(")",1)[1].split()
            children=Path(f"/proc/{current}/task/{current}/children").read_text().split()
            pids.extend(int(p) for p in children)
            result[current]={"cpu_s":(int(stat[11])+int(stat[12]))/os.sysconf("SC_CLK_TCK"),
                             "rss_mib":int(stat[21])*os.sysconf("SC_PAGE_SIZE")/(1024**2)}
            for line in Path(f"/proc/{current}/smaps_rollup").read_text().splitlines():
                if line.startswith("Pss:"):result[current]["pss_mib"]=int(line.split()[1])/1024
        except (OSError,ValueError):pass
    return result


def power():
    paths=Path("/sys/class/drm").glob("card[0-9]/device/hwmon/hwmon*/power1_average")
    for p in paths:
        try:return int(p.read_text())/1_000_000
        except OSError:continue
    return None


def sample(pid,seconds):
    before=process_stats(pid);start=time.monotonic();powers=[];maxrss=0.;maxpss=0.
    for _ in range(seconds):
        time.sleep(1);powers.append(power())
        stats=process_stats(pid)
        maxrss=max(maxrss,sum(p["rss_mib"] for p in stats.values()))
        maxpss=max(maxpss,sum(p.get("pss_mib",0) for p in stats.values()))
    after=process_stats(pid);elapsed=time.monotonic()-start
    cpu=sum(v["cpu_s"]-before.get(k,{"cpu_s":0})["cpu_s"] for k,v in after.items())
    return {"duration_s":elapsed,"cpu_percent_one_core":100*cpu/elapsed,
            "rss_mib_peak_sampled":maxrss,"pss_mib_peak_sampled":maxpss,"gpu_board_power_w_samples":powers,
            "processes":len(after)}


def main():
    try:
        request("status")
        raise SystemExit("An instance already exists; smoke test will not change it")
    except (OSError,RuntimeError):pass
    (ROOT/"reports").mkdir(exist_ok=True)
    report={"scope":"alpha runtime including supervisor/worker/overlay; GPU power is whole-board, not isolated pet power"}
    with (ROOT/"reports/desktop-smoke.log").open("w") as log:
        process=subprocess.Popen([str(ROOT/"run.sh"),"run"],stdout=log,stderr=log)
        try:
            for _ in range(60):
                if process.poll() is not None:raise RuntimeError("App exited during startup; see log")
                try:request("status");break
                except (OSError,RuntimeError):time.sleep(.1)
            else:raise RuntimeError("No control socket")
            report["off_before"]=sample(process.pid,3)
            report["enable"]=request("enable")
            time.sleep(2)
            state=request("status")
            if not state["enabled"] or state["error"]:raise RuntimeError(str(state))
            report["active"]=sample(process.pid,8)
            report["active_state"]=request("status")
            if not report["active_state"]["enabled"] or report["active_state"]["error"]:
                raise RuntimeError("Runtime failed while active")
            if not report["active_state"]["metrics"].get("image_ready"):
                raise RuntimeError("Overlay did not confirm sprite image loaded")
            request("disable");time.sleep(.5)
            report["off_state_before"]=request("status")
            report["off_after"]=sample(process.pid,3)
            report["off_state_after"]=request("status")
            if report["off_state_after"]["enabled"] or report["off_state_after"]["error"]:
                raise RuntimeError("Runtime did not remain disabled and healthy")
            a,b=report["off_state_before"]["metrics"],report["off_state_after"]["metrics"]
            if (a["ticks"],a["queries"])!=(b["ticks"],b["queries"]):raise RuntimeError("Work continued while disabled")
            report["disabled_counters_stable"]=True
        except Exception as exc:
            report["error"]=str(exc)
        finally:
            if process.poll() is None:
                try:request("quit")
                except (OSError,RuntimeError):process.terminate()
                try:process.wait(timeout=4)
                except subprocess.TimeoutExpired:process.kill();process.wait()
            report["exit_code"]=process.returncode
            (ROOT/"reports/desktop-smoke.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(report,indent=2,ensure_ascii=False))
    return 1 if "error" in report else 0


if __name__=="__main__":raise SystemExit(main())
