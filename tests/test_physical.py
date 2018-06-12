from __future__ import print_function
import unittest
import pytest
from ratcave import Physical
import numpy as np
import pickle
from tempfile import NamedTemporaryFile
import sys



np.set_printoptions(suppress=True, precision=2)
np.random.seed(100)

class TestPhysical(unittest.TestCase):
    """
    Run tests from main project folder.
    """

    def test_position_update_to_modelmatrix(self):

        for pos in [(4,5, 6), (5, 4, 1)]:
            phys = Physical(position=pos)
            self.assertTrue(np.isclose(phys.position.xyz, pos).all())
            self.assertTrue(np.isclose(phys.position.zyx, pos[::-1]).all())
            self.assertTrue(np.isclose(phys.model_matrix[:3, 3], pos).all())

        for pos in [(4,5, 6), (5, 4, 1)]:
            phys = Physical()
            phys.position.xyz = pos
            self.assertTrue(np.isclose(phys.position.xyz, pos).all())
            self.assertTrue(np.isclose(phys.position.zyx, pos[::-1]).all())
            self.assertTrue(np.isclose(phys.model_matrix[:3, 3], pos).all())

        for pos in [4, 5]:
            phys = Physical()
            phys.position.xxx = pos
            self.assertTrue(np.isclose(phys.model_matrix[:3, 3], (pos, 0, 0)).all())

    def test_position_property_routing_causes_update_to_modelmatrix(self):

        for pos in [(4, 5, 6), (5, 4, 1)]:
            phys = Physical()
            phys.position = pos
            self.assertEqual(phys.position.xyz, pos)
            self.assertTrue(np.isclose(phys.model_matrix[:3, 3], pos).all())

    def test_rotation_update(self):

        for rot in [(4, 5, 6), (5, 4, 1)]:
            phys = Physical(rotation=rot)
            self.assertTrue(np.isclose(phys.rotation.xyz, rot).all())

        for rot in [(4, 5, 6), (5, 4, 1)]:
            phys.rotation.xyz = rot
            self.assertTrue(np.isclose(phys.rotation.xyz, rot).all())

    def test_rotation_property_routing_causes_update_to_modelmatrix(self):

        for rot in [(4, 5, 6), (5, 4, 1)]:
            phys = Physical()
            phys.rotation = rot
            self.assertEqual(phys.rotation.xyz, rot)

    def test_scale_update_to_modelmatrix(self):

        for scale in (5, 6, 7):
            phys = Physical(scale=scale)
            self.assertTrue(np.isclose(phys.model_matrix[0, 0], scale))
            self.assertTrue(np.isclose(phys.model_matrix[1, 1], scale))
            self.assertTrue(np.isclose(phys.model_matrix[2, 2], scale))

        with pytest.raises(ValueError):
            phys = Physical(scale=0)

        with pytest.raises(ValueError):
            phys = Physical(scale=(0, 0, 0))

        with pytest.raises(ValueError):
            phys = Physical(scale=(0, 1, 1))


    def test_scale_property_routing_causes_update_to_modelmatrix(self):

        for scale in (5, 6, 7):
            phys = Physical()
            phys.scale = scale
            self.assertTrue(np.isclose(phys.model_matrix[0, 0], scale))
            self.assertTrue(np.isclose(phys.model_matrix[1, 1], scale))
            self.assertTrue(np.isclose(phys.model_matrix[2, 2], scale))

        phys = Physical()
        with pytest.raises(ValueError):
            phys.scale = 0

        with pytest.raises(ValueError):
            phys.scale = 0, 0, 0

        with pytest.raises(ValueError):
            phys.scale = (0, 1, 1)



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

        modelmat, normalmat, viewmat = self.phys.model_matrix.copy(), self.phys.normal_matrix.copy(), self.phys.view_matrix.copy()
        self.phys.update()
        self.assertTrue((modelmat == self.phys.model_matrix).all())
        self.assertTrue((normalmat == self.phys.normal_matrix).all())
        self.assertTrue((viewmat == self.phys.view_matrix).all())

    def test_look_at_makes_correct_viewmatrix(self):
        """Makes sure that the projection of a looked-at point is centered onscreen."""
        for _ in range(200):
            phys = Physical(position=np.random.uniform(-3, 3, size=3), rotation=np.random.uniform(-3, 3, size=3), scale=np.random.uniform(-5, 5, size=3))
            x, y, z = np.random.uniform(-5, 5, size=3)
            phys.look_at(x, y, z)
            view_projection = np.dot(phys.view_matrix, np.matrix([x, y, z, 1]).T)
            self.assertTrue(np.isclose(view_projection[:2], 0, atol=1e-4).all())



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


if sys.platform == 'linux':
    def test_physical_is_picklable():
        for _ in range(10):
            phys = Physical(position=np.random.uniform(-5, 5, 3),
                            rotation=np.random.uniform(-5, 5, 3),
                            scale=np.random.uniform(1, 5, 3))
            with NamedTemporaryFile('wb', delete=False) as f:
                pickle.dump(phys, f)
            with open(f.name, 'rb') as f:
                phys2 = pickle.load(f)
            assert phys.position.xyz == phys2.position.xyz
            assert phys.rotation.xyz == phys2.rotation.xyz
            assert phys.scale.xyz == phys2.scale.xyz
            assert np.isclose(phys.model_matrix[:3, -1], phys2.model_matrix[:3, -1]).all()

            phys.position.xyz = 5, 5, 5
            assert not np.isclose(phys.position.xyz, phys2.position.xyz).all()
            assert not np.isclose(phys.model_matrix[:3, -1], phys2.model_matrix[:3, -1]).all()

            phys2.position.xyz = 5, 5, 5
            assert np.isclose(phys.position.xyz, phys2.position.xyz).all()
            assert np.isclose(phys2.position.xyz, phys2.model_matrix[:3, -1]).all()
            assert np.isclose(phys.normal_matrix, phys2.normal_matrix).all()
            assert np.isclose(phys.view_matrix, phys2.view_matrix).all()
            print(phys2.model_matrix)
            assert np.isclose(phys.model_matrix[:3, -1], phys2.model_matrix[:3, -1]).all()