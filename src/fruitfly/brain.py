"""Prototype neural control: extracted escape circuit + explicit engineered rate cells.

Only an early flee/explore experiment, not the ten-behaviour release model.
The rate cell weights below are designed, not measured Drosophila physiology.
"""
import math
import random
from .core import Circuit
from .shelter_network import ShelterNetwork


class Brain:
    names=("walk","escape","left","right","rest","phase_a","phase_b")
    bias=(.34,0,.05,.05,0,0,0)
    # Recurrent projections (post, pre, weight).
    edges=((0,4,-1.2),(0,1,-.3),(1,1,.15),(2,3,-.6),(3,2,-.6),
           (2,5,.18),(3,5,-.18),(5,5,1.6),(6,6,1.6),
           (5,6,-1.8),(6,5,1.8),(4,4,.2))
    tau=(.4,.045,.08,.08,5,1.5,1.5)

    def __init__(self,seed=7,model_path=None):
        self.circuit=Circuit(model_path)
        self.state=[0]*7;self.state[5]=.1
        self.rng=random.Random(seed)
        self.inputs=[i for i,n in enumerate(self.circuit.neurons) if n["type"] in {"LC4","LPLC2"}]
        self.gf=[i for i,n in enumerate(self.circuit.neurons) if n["type"]=="DNp01"]
        self.last_cursor=None
        self.fraction_ms=0.
        self.gf_rate=0.
        self.shelter_network=ShelterNetwork()

    def step(self,x,y,angle,cursor,bounds,effort,dt,entries=(),attached=None,exposure=1.):
        dx,dy=cursor[0]-x,cursor[1]-y
        distance=max(1.,math.hypot(dx,dy))
        bearing=math.atan2(dy,dx)-angle
        radial=0.
        if self.last_cursor:
            # Cursor motion in the fly's direction; distance derivative is a sensory feature.
            vx=(cursor[0]-self.last_cursor[0])/dt;vy=(cursor[1]-self.last_cursor[1])/dt
            radial=max(0.,-(vx*dx+vy*dy)/distance)
        self.last_cursor=cursor
        angular=2*math.atan2(18.,distance)
        expansion=min(1.,radial/(distance+40.))
        stimulus=min(1.,angular*.7+expansion*.5)*(.1+.9*exposure)
        currents=[0.]*self.circuit.n
        for i in self.inputs:
            side=self.circuit.neurons[i].get("side")
            lateral=math.sin(bearing)*(1 if side=="left" else -1)
            currents[i]=stimulus*.11*(.65+.35*lateral)
        total=dt*1000+self.fraction_ms
        steps=max(1,int(total));self.fraction_ms=total-steps
        rates=self.circuit.step(currents,min(steps,200))
        self.gf_rate=sum(rates[i] for i in self.gf)/len(self.gf)
        danger=min(1.,self.gf_rate/120.)
        # Egocentric edge range: geometric sensor, not an avoidance command.
        left,top,width,height=bounds
        def proximity(offset):
            px=x+math.cos(angle+offset)*65;py=y+math.sin(angle+offset)*65
            margin=min(px-left,left+width-px,py-top,top+height-py)
            return max(0.,min(1.,(24-margin)/50))
        a,b=proximity(-.6),proximity(.6)
        # Bilateral edge input amplifies the ongoing neural turning phase. This
        # breaks the head-on symmetry without a wall-triggered movement override.
        turn=self.state[5]*max(a,b)*1.4
        inputs=[0.,danger*1.8,max(0.,math.sin(bearing))*stimulus*.8+b*.9,
                max(0.,-math.sin(bearing))*stimulus*.8+a*.9,effort*1.1-danger,0.,0.]
        inputs[2]+=turn;inputs[3]-=turn
        drive=[bias+v for bias,v in zip(self.bias,inputs)]
        for post,pre,w in self.edges:drive[post]+=self.state[pre]*w
        drive[5]+=self.rng.uniform(-.13,.13)
        for i in range(7):
            target=math.tanh(drive[i]) if i>=5 else max(0.,min(1.,drive[i]))
            self.state[i]+=(target-self.state[i])*(-math.expm1(-dt/self.tau[i]))
        base={"speed":max(0.,self.state[0]-.10)*75+self.state[1]*300,
                "yaw":(self.state[3]-self.state[2])*5,
                "flight":self.state[1],"gf_hz":self.gf_rate}
        return self.shelter_network.step(x,y,angle,entries,attached,danger,dt,base)

    def close(self):self.circuit.close()
