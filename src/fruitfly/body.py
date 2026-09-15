"""Kinematics and sprite poses; behavioural commands belong to Brain.

Flight animation is a stylized 8 Hz cycle, not a biological wingbeat rate.
No animation clock runs independently of the bounded worker loop.
"""
import math


class Body:
    def __init__(self,x=0.,y=0.,angle=0.):
        self.x=x;self.y=y;self.angle=angle;self.effort=0.
        self.mode="rest";self.phase=0.

    def step(self,command,bounds,dt):
        left,top,width,height=bounds
        self.angle=(self.angle+command["yaw"]*dt)%(2*math.pi)
        old_x,old_y=self.x,self.y
        self.x=max(left+32,min(left+width-32,self.x+math.cos(self.angle)*command["speed"]*dt))
        self.y=max(top+32,min(top+height-32,self.y+math.sin(self.angle)*command["speed"]*dt))
        distance=math.hypot(self.x-old_x,self.y-old_y)
        self.effort=max(0.,min(1.,self.effort+dt*(command["speed"]*.0004-.012)))
        # Hysteresis prevents chattering as the motor activation crosses a threshold.
        flying=command["flight"]>(.12 if self.mode=="flight" else .22)
        mode="flight" if flying else ("walk" if distance>dt*2 else "rest")
        if mode!=self.mode:self.phase=0.
        self.mode=mode
        if mode=="flight":self.phase=(self.phase+dt*8)%1
        elif mode=="walk":self.phase=(self.phase+distance/8)%1
        else:self.phase=0.
        return {"mode":mode,"frame":int(self.phase*2),"faceLeft":math.cos(self.angle)<0}
