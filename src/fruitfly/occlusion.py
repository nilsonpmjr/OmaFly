"""Rectangular drawing geometry, independent of behavioural decisions.

The caller supplies an already selected shelter. This module never selects one.
Coordinates are logical desktop pixels; rectangles are half-open.
"""
import math


def visible_rects(x,y,shelter=None,size=64):
    """Subtract one global shelter from a sprite centred at x,y.

    Return at most four disjoint rectangles local to the sprite. No texture,
    framebuffer, per-pixel mask, or full-monitor surface is allocated.
    """
    whole=[{"x":0,"y":0,"width":size,"height":size}]
    if shelter is None:return whole
    left,top,width,height=shelter
    if not all(math.isfinite(v) for v in (x,y,left,top,width,height)):
        raise ValueError("Non-finite occlusion geometry")
    if width<=0 or height<=0:return whole
    # Align with the integer position actually sent to the overlay.
    origin_x,origin_y=round(x)-size/2,round(y)-size/2
    a=max(0,min(size,left-origin_x));b=max(0,min(size,top-origin_y))
    c=max(0,min(size,left+width-origin_x));d=max(0,min(size,top+height-origin_y))
    if a>=c or b>=d:return whole
    pieces=((0,0,size,b),(0,d,size,size-d),(0,b,a,d-b),(c,b,size-c,d-b))
    return [{"x":px,"y":py,"width":w,"height":h} for px,py,w,h in pieces if w>0 and h>0]
