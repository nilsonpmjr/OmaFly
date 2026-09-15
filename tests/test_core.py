import math
import tempfile
import unittest
import json
from pathlib import Path
from fruitfly.core import Circuit,ROOT
from fruitfly.brain import Brain


class CoreTests(unittest.TestCase):
    def test_anatomical_ids_remain_exact_strings(self):
        with Circuit() as c:
            self.assertEqual(c.n,320)
            self.assertEqual(len(c.sources),1705)
            self.assertTrue(all(isinstance(n["id"],str) and int(n["id"])>2**53 for n in c.neurons))
            self.assertEqual(c.model["type_synapses"]["LC4->DNp01"],3080)
            self.assertEqual(c.model["type_synapses"]["LPLC2->DNp01"],1177)

    def test_batching_preserves_neural_time_and_output(self):
        with Circuit() as a,Circuit() as b:
            current=[.09 if n["type"]=="LC4" else 0 for n in a.neurons]
            one=a.step(current,200)
            for _ in range(200):many=b.step(current,1)
            self.assertEqual(one,many)
            a.reset()
            self.assertEqual(one,a.step(current,200))

    def test_selective_ablation_changes_gf_without_removing_stimulus(self):
        model=json.loads((ROOT/"models/escape.json").read_text())
        gf={n["id"] for n in model["neurons"] if n["type"]=="DNp01"}
        model["edges"]=[e for e in model["edges"] if e["post"] not in gf]
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"ablated.json";path.write_text(json.dumps(model))
            with Circuit() as normal,Circuit(path) as cut:
                stimulus=[.09 if n["type"] in {"LC4","LPLC2"} else 0 for n in normal.neurons]
                r=normal.step(stimulus,1000);s=cut.step(stimulus,1000)
                self.assertGreater(sum(r[i] for i,n in enumerate(normal.neurons) if n["id"] in gf),100)
                self.assertEqual(sum(s[i] for i,n in enumerate(normal.neurons) if n["id"] in gf),0)
                sensory=[i for i,n in enumerate(normal.neurons) if n["type"]=="LC4"]
                self.assertGreater(sum(s[i] for i in sensory),0)

    def test_no_spontaneous_spikes_in_unstimulated_extracted_core(self):
        with Circuit() as c:self.assertEqual(c.step([0]*c.n,1000),[0]*c.n)

    def test_unknown_nt_has_no_silent_excitatory_override(self):
        with Circuit() as c:
            unknown={i for i,n in enumerate(c.neurons) if not n["nt"]}
            self.assertEqual(len(unknown),5)
            self.assertTrue(all(w==0 for pre,w in zip(c.sources,c.weights) if pre in unknown))

    def test_invalid_inputs_do_not_reach_native_core(self):
        with Circuit() as c:
            for currents,steps in [([0]*c.n,0),([0]*c.n,1001),([0]*c.n,1.5),([math.nan]*c.n,1),([],1)]:
                with self.assertRaises(ValueError):c.step(currents,steps)
        with self.assertRaises(ValueError):c.step([0]*c.n)

    def test_brain_replays_with_fixed_seed(self):
        a,b=Brain(seed=9),Brain(seed=9)
        try:
            for step in range(100):
                args=(400,300,.2,(500-step*2,350),(0,0,1000,800),.1,.04)
                self.assertEqual(a.step(*args),b.step(*args))
        finally:a.close();b.close()


if __name__=="__main__":unittest.main()
