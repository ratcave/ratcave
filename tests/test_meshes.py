import unittest
from ratcave import resources, WavefrontReader


class TestMesh(unittest.TestCase):
    """
    Run tests from main project folder.
    """

    def setUp(self):
        self.reader = WavefrontReader(resources.obj_primitives)
        self.mesh = self.reader.get_mesh("Cube")

    def tearDown(self):
        pass

    def test_position_update(self):

        mesh = self.mesh
        for pos in [(4,5, 6), (5, 4, 1)]:
            mesh.x, mesh.y, mesh.z = pos
            self.assertEqual(mesh.position, pos)

    def test_rotation_update(self):

        mesh = self.mesh
        for rot in [(4, 5, 6), (5, 4, 1)]:
            mesh.rot_x, mesh.rot_y, mesh.rot_z = rot
            self.assertEqual(mesh.rotation, rot)
