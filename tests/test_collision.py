import unittest
import numpy as np
from numpy.linalg import norm
from ratcave import SphereCollisionChecker, CylinderCollisionChecker
from ratcave import resources, WavefrontReader, Mesh


class TestCollision(unittest.TestCase):
    """
    Run tests from main project folder.
    """
    def setUp(self):
        self.reader = WavefrontReader(resources.obj_primitives)
        self.mesh = self.reader.get_mesh("Cube", position=(0,0,0))


    def test_sphere_collides_with(self):
        col_sphere = SphereCollisionChecker(parent=self.mesh)
        self.assertTrue( col_sphere.collides_with(xyz=(0,0,0)) )

        for _ in range(200):
            xyz = np.random.normal(loc=0.0, scale=1.5, size=3)

            if (col_sphere.collision_radius > norm(xyz)):
                self.assertTrue( col_sphere.collides_with(xyz=xyz) )
            else:
                self.assertFalse( col_sphere.collides_with(xyz=xyz) )


    def test_cylinder_collides_with_yaxis(self):
        col_cylinder = CylinderCollisionChecker(parent=self.mesh, up_axis='y')
        self.assertTrue( col_cylinder.collides_with(xyz=(0,0,0)) )

        for _ in range(100):
            y = np.random.normal(loc=0.0, scale=100, size=1)
            xz = np.random.normal(loc=0.0, scale=1.5, size=2)

            self.assertTrue( col_cylinder.collides_with(xyz=(0,y,0)) )

            if (col_cylinder.collision_radius > norm(xz)):
                self.assertTrue( col_cylinder.collides_with(xyz=(xz[0],y,xz[1])) )
            else:
                self.assertFalse( col_cylinder.collides_with(xyz=(xz[0],y,xz[1])) )


    def test_cylinder_collides_with_xaxis(self):
        col_cylinder = CylinderCollisionChecker(parent=self.mesh, up_axis='x')
        self.assertTrue( col_cylinder.collides_with(xyz=(0,0,0)) )

        for _ in range(100):
            x = np.random.normal(loc=0.0, scale=100, size=1)
            yz = np.random.normal(loc=0.0, scale=1.5, size=2)

            self.assertTrue( col_cylinder.collides_with(xyz=(x,0,0)) )

            if (col_cylinder.collision_radius > norm(yz)):
                self.assertTrue( col_cylinder.collides_with(xyz=(x,yz[0],yz[1])) )
            else:
                self.assertFalse( col_cylinder.collides_with(xyz=(x,yz[0],yz[1])) )


    def test_cylinder_collides_with_zaxis(self):
        col_cylinder = CylinderCollisionChecker(parent=self.mesh, up_axis='z')
        self.assertTrue( col_cylinder.collides_with(xyz=(0,0,0)) )

        for _ in range(100):
            z = np.random.normal(loc=0.0, scale=100, size=1)
            xy = np.random.normal(loc=0.0, scale=1.5, size=2)
            self.assertTrue( col_cylinder.collides_with(xyz=(0,0,z)) )

            if (col_cylinder.collision_radius > norm(xy)):
                self.assertTrue( col_cylinder.collides_with(xyz=(xy[0],xy[1],z)) )
            else:
                self.assertFalse( col_cylinder.collides_with(xyz=(xy[0],xy[1],z)) )
