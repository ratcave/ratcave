from __future__ import print_function
import unittest
from fruitloop import Physical
import numpy as np


np.set_printoptions(suppress=True, precision=2)

class TestPhysical(unittest.TestCase):
    """
    Run tests from main project folder.
    """

    def test_position_update_to_modelmatrix(self):


        for pos in [(4,5, 6), (5, 4, 1)]:
            phys = Physical(position=pos)
            self.assertEqual(phys.position.xyz, pos)
            self.assertTrue(np.isclose(phys.model_matrix[:3, 3], pos).all())

        for pos in [(4,5, 6), (5, 4, 1)]:
            phys.position.xyz = pos
            self.assertEqual(phys.position.xyz, pos)
            self.assertTrue(np.isclose(phys.model_matrix[:3, 3], pos).all())

    def test_rotation_update(self):

        for rot in [(4, 5, 6), (5, 4, 1)]:
            phys = Physical(rotation=rot)
            self.assertEqual(phys.rotation.xyz, rot)

        for rot in [(4, 5, 6), (5, 4, 1)]:
            phys.rotation.xyz = rot
            self.assertEqual(phys.rotation.xyz, rot)

    def test_scale_update_to_modelmatrix(self):

        for scale in (5, 6, 7):
            phys = Physical(scale=scale)
            self.assertTrue(np.isclose(phys.model_matrix[0, 0], scale))
            self.assertTrue(np.isclose(phys.model_matrix[1, 1], scale))
            self.assertTrue(np.isclose(phys.model_matrix[2, 2], scale))


class TestModelViewNormalMatrices(unittest.TestCase):

    def setUp(self):
        self.phys = Physical(position=[10, 20, 30], rotation=(90, 0, 0), scale=3)

    def test_correct_modelmatrix(self):

        correct_modelmat = np.array([[3., 0., 0., 10.],
                            [0., 0., -3., 20.],
                            [0., 3., 0., 30.],
                            [0., 0., 0., 1.]], dtype=np.float32)

        self.assertTrue(np.isclose(self.phys.model_matrix, correct_modelmat, rtol=1e-3, atol=1e-3).all())

    def test_correct_normalmatrix(self):

        correct_normalmat = np.linalg.inv(self.phys.model_matrix.T)
        self.assertTrue(np.isclose(self.phys.normal_matrix, correct_normalmat, rtol=1e-3, atol=1e-3).all())


    def test_correct_viewmatrix(self):

        correct_modelmat_without_scale = np.array([[1., 0., 0., 10.],
                                                    [0., 0., -1., 20.],
                                                    [0., 1., 0., 30.],
                                                    [0., 0., 0., 1.]], dtype=np.float32)

        correct_viewmat = np.linalg.inv(correct_modelmat_without_scale)
        self.assertTrue(np.isclose(self.phys.view_matrix, correct_viewmat, rtol=1e-3, atol=1e-3).all())


    def test_update_doesnt_alter_mats(self):

        modelmat, normalmat, viewmat = self.phys.model_matrix, self.phys.normal_matrix, self.phys.view_matrix
        self.phys.update()
        self.assertTrue((modelmat == self.phys.model_matrix).all())
        self.assertTrue((normalmat == self.phys.normal_matrix).all())
        self.assertTrue((viewmat == self.phys.view_matrix).all())


class TestOrientation(unittest.TestCase):

    def test_orientation0_is_unitlength(self):

        phys = Physical()
        for ori in [(1, 2, 3), (-10, 5, 0), (0, 0, .1)]:
            phys.orientation0 = ori
            self.assertAlmostEqual(np.linalg.norm(phys.orientation0), 1.)

    def test_orientation_is_updated(self):

        phys = Physical()

        for ori0, ori1 in [[(0, 0, -1), (0, 1, 0)], [(1, 0, 0), (1, 0, 0)]]:
            phys.orientation0 = ori0
            phys.rotation.x = 90
            self.assertTrue(np.isclose(phys.orientation, ori1, atol=1e-4).all())

