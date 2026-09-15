import random
import unittest
from fruitfly.occlusion import visible_rects


class OcclusionTests(unittest.TestCase):
    def test_subtraction_matches_pixel_reference(self):
        rng=random.Random(4)
        cases=[None,(-100,-100,200,200),(0,-50,100,100),(-50,0,100,100),
               (-8,-8,16,16),(32,32,12,12),(-5,-5,0,30)]
        cases += [(rng.randrange(-70,70),rng.randrange(-70,70),rng.randrange(1,100),rng.randrange(1,100)) for _ in range(100)]
        for shelter in cases:
            pieces=visible_rects(0,0,shelter)
            self.assertLessEqual(len(pieces),4)
            for y in range(64):
                for x in range(64):
                    count=sum(p["x"]<=x+.5<p["x"]+p["width"] and p["y"]<=y+.5<p["y"]+p["height"] for p in pieces)
                    covered=shelter is not None and shelter[0]<=x+.5-32<shelter[0]+shelter[2] and shelter[1]<=y+.5-32<shelter[1]+shelter[3]
                    self.assertEqual(count,0 if covered else 1)

    def test_translation_and_fractional_coordinates(self):
        rect=(-10.5,2.25,30.75,20.5)
        self.assertEqual(visible_rects(0,0,rect),visible_rects(-1200,300,(-1210.5,302.25,30.75,20.5)))
        self.assertEqual(visible_rects(0,0,None),[{"x":0,"y":0,"width":64,"height":64}])
        with self.assertRaises(ValueError):visible_rects(0,0,(float("nan"),0,1,1))


if __name__=="__main__":unittest.main()
