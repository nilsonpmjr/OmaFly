#!/usr/bin/env python3
"""Paced CPU measurement, selective ablation and input for the optional HIP probe."""
import argparse
import ctypes
import json
import resource
import struct
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "src"))
from fruitfly.core import Circuit


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--seconds",type=float,default=5)
    args=parser.parse_args()
    if not 0.1<=args.seconds<=60:parser.error("seconds must be in [0.1, 60]")
    (ROOT/"reports").mkdir(exist_ok=True)
    with Circuit() as c:
        sensory=[i for i,n in enumerate(c.neurons) if n["type"] in {"LC4","LPLC2"}]
        outputs=[i for i,n in enumerate(c.neurons) if n["type"]=="DNp01"]
        current=[0.0]*c.n
        for i in sensory:current[i]=0.09
        def run(stim):
            c.reset()
            for _ in range(25):r=c.step(stim,40)
            return sum(r[i] for i in outputs)/len(outputs)
        evoked=run(current)
        silent=run([0.0]*c.n)
        c.reset()
        cycles=round(args.seconds*25);times=[]
        cpu=time.process_time();start=time.monotonic()
        for i in range(cycles):
            before=time.perf_counter();c.step(current,40);times.append(time.perf_counter()-before)
            time.sleep(max(0,start+(i+1)*.04-time.monotonic()))
        elapsed=time.monotonic()-start;used=time.process_time()-cpu
        report={"backend":"native-cpu","neurons":c.n,"edges":len(c.sources),
                "duration_s":elapsed,"cpu_s":used,"cpu_percent_one_core":100*used/elapsed,
                "cycle_ms_mean":sum(times)/len(times)*1000,
                "cycle_ms_p95":sorted(times)[int(.95*(len(times)-1))]*1000,
                "peak_rss_mib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
                "gf_rate_stimulated_hz":evoked,"gf_rate_sensory_silenced_hz":silent,
                "scope":"core+ctypes only; excludes UI, compositor and power measurement"}
        (ROOT/"reports/core-benchmark.json").write_text(json.dumps(report,indent=2)+"\n")
        with (ROOT/"build/gpu-input.bin").open("wb") as f:
            f.write(struct.pack("=ii",c.n,len(c.sources)))
            for v in [c.offsets,c.sources,c.weights]:f.write(bytes(v))
            f.write(struct.pack(f"={c.n}f",*current))
        c.reset()
        for _ in range(125):reference=c.step(current,40)
        (ROOT/"build/cpu-reference.bin").write_bytes(struct.pack(f"={c.n}f",*reference))
        print(json.dumps(report,indent=2))


if __name__=="__main__":main()
