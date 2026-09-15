import unittest
from fruitfly.pacing import Budget


class BudgetTests(unittest.TestCase):
    def test_normal_device_keeps_sensory_period(self):
        self.assertAlmostEqual(Budget().deadline(1,1.0004,.0003,True),1.04)

    def test_overloaded_device_must_sleep_instead_of_catching_up(self):
        b=Budget();deadline=b.deadline(1,1.2,.05,True)
        self.assertGreater(deadline,1.2)
        self.assertLessEqual(.05/(deadline-1),b.worker_cpu_fraction)

    def test_rest_reduces_wakeups_without_stopping_neural_time(self):
        self.assertAlmostEqual(Budget().deadline(1,1.0001,.0001,False),1.1)


if __name__=="__main__":unittest.main()
