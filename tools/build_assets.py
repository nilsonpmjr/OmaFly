#!/usr/bin/env python3
"""Generate cached poses from the supplied SVG; keep the source untouched."""
from pathlib import Path
from copy import deepcopy
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
PALETTE={"k":"#211d26","b":"#544650","h":"#aa8270","e":"#e94735",
         "s":"#f6b58c","w":"#c6dee4","l":"#879da6"}
HEAD=[
"................",
"...k........k...",
"....k......k....",
".....kkkkkk.....",
"...kkhhbbhhkk...",
"..keeesbbseeek..",
"..keeesbbseeek..",
".keeeesbbseeeek.",
".keeeebbbbeeeek.",
"..keebbbbbbeek..",
"...kkbbbbbbkk...",
".....khhhhk.....",
"......kkkk......",
".......kk.......",
"................",
"................",
]


def svg(grid,palette):
    rects=[]
    for y,row in enumerate(grid):
        for x,ch in enumerate(row):
            if ch in palette:rects.append(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{palette[ch]}"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{len(grid[0])}" height="{len(grid)}" viewBox="0 0 {len(grid[0])} {len(grid)}" shape-rendering="crispEdges">'+''.join(rects)+'</svg>\n'


def main():
    dest=ROOT/"assets";dest.mkdir(exist_ok=True)
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    source=ET.parse(dest/"fly-source.svg").getroot()
    source.set("width","64");source.set("height","64")
    source.set("shape-rendering","crispEdges")
    def save(root,name):
        ET.ElementTree(root).write(dest/name,encoding="unicode")
    save(source,"fly.svg")
    for frame in range(2):
        walk=deepcopy(source)
        groups={g.get("id"):g for g in walk.iter() if g.get("id")}
        if frame:
            for name,shift in (("leg-front-right",2),("leg-mid-right",-2),("leg-hind-right",2),("legs-far",-1)):
                groups[name].set("transform",f"translate({shift} 0)")
        save(walk,f"fly-walk-{frame}.svg")
        flight=deepcopy(source)
        groups={g.get("id"):g for g in flight.iter() if g.get("id")}
        for name in ("legs-near","legs-far"):
            groups[name].set("transform","matrix(1 0 0 0.5 0 16)")
        groups["ground-shadow"].set("opacity","0.12")
        # Both frames keep the same tucked legs; only the wings change pose.
        if frame:
            for name in ("wing-near","wing-far"):
                groups[name].set("transform","matrix(1 0 0 -1 0 56)")
        save(flight,f"fly-flight-{frame}.svg")
    (dest/"tray.svg").write_text(svg(HEAD,PALETTE))
    off={k:"#929292" for k in PALETTE};off["k"]="#414141"
    (dest/"tray-off.svg").write_text(svg(HEAD,off))


if __name__=="__main__":main()
