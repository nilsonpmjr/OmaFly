import unittest
from fruitfly.pacing import Budget,FrameGate


class BudgetTests(unittest.TestCase):
    def test_normal_device_keeps_sensory_period(self):
        self.assertAlmostEqual(Budget().deadline(1,1.0004,.0003,True),1.04)

    def test_overloaded_device_must_sleep_instead_of_catching_up(self):
        b=Budget();deadline=b.deadline(1,1.2,.05,True)
        self.assertGreater(deadline,1.2)
        self.assertLessEqual(.05/(deadline-1),b.worker_cpu_fraction)

    def test_rest_reduces_wakeups_without_stopping_neural_time(self):
        self.assertAlmostEqual(Budget().deadline(1,1.0001,.0001,False),1.1)

    def test_walking_frames_are_coalesced_without_queuing_stale_positions(self):
        gate=FrameGate();accepted=[]
        for i in range(100):
            if gate.accept({'visible':True,'mode':'walk','x':i},i/100):accepted.append(i)
        self.assertLessEqual(len(accepted),11)
        latest={'visible':True,'mode':'walk','x':999}
        self.assertTrue(gate.accept(latest,1.1));self.assertEqual(gate.last,latest)

    def test_flight_and_visibility_transitions_bypass_render_limit(self):
        gate=FrameGate()
        self.assertTrue(gate.accept({'visible':True,'mode':'walk'},0))
        self.assertTrue(gate.accept({'visible':True,'mode':'flight'},.01))
        self.assertTrue(gate.accept({'visible':False},.02))
        self.assertFalse(gate.accept({'visible':False},.03))
        self.assertTrue(gate.accept({'visible':True,'mode':'walk'},.04))


if __name__=="__main__":unittest.main()
