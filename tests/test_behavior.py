"""Closed-loop checks of neural influence and movement, with no real desktop."""
import json
import math
from pathlib import Path
import tempfile
import unittest
from fruitfly.brain import Brain
from fruitfly.body import Body
from fruitfly.core import ROOT


BOUNDS=(0,0,1000,800)


class BehaviorTests(unittest.TestCase):
    def test_explores_and_leaves_edges_without_cursor_threat(self):
        for seed,dt in ((7,.04),(21,.1)):
            for start in ((600,480,0),(968,768,0),(32,32,math.pi)):
                with self.subTest(seed=seed,dt=dt,start=start):
                    brain=Brain(seed=seed);body=Body(*start)
                    try:
                        # Every 30-second window must cover meaningful ground;
                        # a rotating body stuck at a corner does not pass.
                        for _ in range(6):
                            points=[]
                            for _ in range(round(30/dt)):
                                command=brain.step(body.x,body.y,body.angle,(-10000,-10000),BOUNDS,body.effort,dt)
                                body.step(command,BOUNDS,dt);points.append((body.x,body.y))
                                self.assertEqual(command["flight"],0)
                            span=math.hypot(max(p[0] for p in points)-min(p[0] for p in points),
                                            max(p[1] for p in points)-min(p[1] for p in points))
                            self.assertGreater(span,50)
                    finally:brain.close()

    def test_cutting_gf_inputs_removes_escape_in_same_scene(self):
        model=json.loads((ROOT/"models/escape.json").read_text())
        gf={n["id"] for n in model["neurons"] if n["type"]=="DNp01"}
        model["edges"]=[e for e in model["edges"] if e["post"] not in gf]
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"cut.json";path.write_text(json.dumps(model))
            results=[]
            for model_path in (None,path):
                brain=Brain(model_path=model_path);body=Body(400,400)
                speeds=[];flights=[];poses=set()
                try:
                    for _ in range(250):
                        command=brain.step(body.x,body.y,body.angle,(425,400),BOUNDS,body.effort,.04)
                        poses.add(body.step(command,BOUNDS,.04)["mode"])
                        speeds.append(command["speed"]);flights.append(command["flight"])
                    results.append((max(speeds),max(flights),poses))
                finally:brain.close()
            intact,cut=results
            self.assertGreater(intact[0],cut[0]*3)
            self.assertGreater(intact[1],.22)
            self.assertIn("flight",intact[2])
            self.assertEqual(cut[1],0)
            self.assertNotIn("flight",cut[2])

    def test_animation_uses_flight_command_and_freezes_at_rest(self):
        body=Body(500,400,math.pi/2)
        command={"speed":80,"yaw":0,"flight":0}
        self.assertEqual(body.step(command,BOUNDS,.04)["mode"],"walk")
        command["flight"]=.5
        frames={body.step(command,BOUNDS,.04)["frame"] for _ in range(20)}
        self.assertEqual(body.mode,"flight");self.assertEqual(frames,{0,1})
        command.update(speed=0,flight=0)
        first=body.step(command,BOUNDS,.04)
        self.assertEqual(first["mode"],"rest")
        for _ in range(20):self.assertEqual(body.step(command,BOUNDS,.1),first)

    def test_walking_animation_advances_on_diagonal_without_xy_cancellation(self):
        body=Body(500,400,-math.pi/4)
        frames={body.step({"speed":20,"yaw":0,"flight":0},BOUNDS,.04)["frame"] for _ in range(20)}
        self.assertEqual(frames,{0,1})


if __name__=="__main__":unittest.main()
