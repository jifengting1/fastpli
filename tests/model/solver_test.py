import unittest
import numpy as np

import fastpli


class MainTest(unittest.TestCase):

    def setUp(self):
        self.fiber = fastpli.objects.Fiber([0, 0, 0, 0, 0, 1], [1, 2])
        self.fiberbundles = [[self.fiber]]
        self.solver = fastpli.model.Solver()
        self.solver.set_fiber_bundles(self.fiberbundles)

    def test_number_of_fibers(self):
        self.solver.set_parameters(drag=0, obj_min_radius=0, obj_mean_length=0)
        self.solver.step()
        fb = self.solver.get_fiber_bundles()
        self.assertTrue(np.array_equal(self.fiber.points, fb[0][0].points))
        self.assertTrue(np.array_equal(self.fiber.radii, fb[0][0].radii))

    def test_split(self):
        self.solver.set_parameters(
            drag=0, obj_min_radius=0, obj_mean_length=0.5)
        self.solver.step()
        fb = self.solver.get_fiber_bundles()
        self.assertTrue(fb[0][0].radii[1] == 1.5)

    def test_combine(self):
        self.fiber = fastpli.objects.Fiber(
            [0, 0, 0, 0, 0, 1, 0, 0, 2], [1, 1, 1])
        self.fiberbundles = [[self.fiber]]
        self.solver.set_fiber_bundles(self.fiberbundles)
        self.solver.set_parameters(drag=0, obj_min_radius=0, obj_mean_length=2)
        self.solver.step()
        fb = self.solver.get_fiber_bundles()
        self.assertTrue(fb[0][0].radii.shape[0] == 2)


if __name__ == '__main__':
    unittest.main()
