
import numpy as np
import pickle
from . import utils
from collections import deque

# TODO: Check for loops and duplicate nodes in the Scene graph
class SceneNode(object):

    def __init__(self, parent=None, children=None):
        """A Node of the Scenegraph.  Has children, but no parent."""
        self._children = []
        self._parent = None
        if parent:
            self.parent = parent
        if children:
            self.add_children(children)

    def __iter__(self):
        """Returns an iterator that walks through the scene graph,
         starting with the current object."""
        def walk_tree_breadthfirst(obj):
            """tree walking algorithm, using algorithm from
            http://kmkeen.com/python-trees/"""
            order = deque([obj])
            while len(order) > 0:
                order.extend(order[0]._children)
                yield order.popleft()

        return walk_tree_breadthfirst(self)

    @property
    def parent(self):
        """A SceneNode object that is this object's parent in the scene graph."""
        return self._parent

    @parent.setter
    def parent(self, value):
        assert isinstance(value, SceneNode)
        if self._parent is not None:
            self._parent._children.remove(self)
        self._parent = value
        self._parent._children.append(self)

    def add_children(self, children=list()):
        """Adds a list of objects as children in the scene graph."""

        for child in children:
            assert isinstance(child, SceneNode)
            child._parent = self
            self._children.append(child)

    def remove_children(self, children):
        for child in children:
            child._parent = None
            self._children.remove(child)

    @property
    def children(self):
        return tuple(self._children)


class Physical(object):

    def __init__(self, position=(0., 0., 0.), rotation=(0., 0., 0.), scale=1., *args, **kwargs):
        """XYZ Position, Scale and XYZEuler Rotation Class.

        Args:
            position (list): (x, y, z) translation values.
            rotation (list): (x, y, z) rotation values
            scale (float): uniform scale factor. 1 = no scaling.
        """
        super(Physical, self).__init__(*args, **kwargs)
        self.x, self.y, self.z = position
        self.rot_x, self.rot_y, self.rot_z = rotation
        self._rot_matrix = None
        self.scale = scale
        self.model_matrix = np.zeros((4,4))
        self.normal_matrix = np.zeros((4,4))
        self.view_matrix = np.zeros((4,4))

        self.update()

    @property
    def position(self):
        """xyz local position"""
        return self.x, self.y, self.z

    @position.setter
    def position(self, value):
        self.x, self.y, self.z = value

    @property
    def rotation(self):
        """XYZ Euler rotation, in degrees"""
        return self.rot_x, self.rot_y, self.rot_z

    @rotation.setter
    def rotation(self, value):
        self.rot_x, self.rot_y, self.rot_z = value

    def update(self):
        """Calculate model, normal, and view matrices from position, rotation, and scale data."""
        self.model_matrix = utils.orienting.calculate_model_matrix(self.position, self.rotation, self.scale)
        self.normal_matrix = np.linalg.inv(self.model_matrix.T)
        self.view_matrix = utils.orienting.calculate_view_matrix(self.position, self.rotation)


class PhysicalNode(Physical, SceneNode):

    def __init__(self, *args, **kwargs):
        """Object with xyz position and rotation properties that are relative to its parent."""
        self.model_matrix_global = np.zeros((4,4))
        self.normal_matrix_global = np.zeros((4,4))
        self.view_matrix_global = np.zeros((4,4))
        super(PhysicalNode, self).__init__(*args, **kwargs)


    def update(self):
        super(PhysicalNode, self).update()

        """Calculate world matrix values from the dot product of the parent."""
        if self.parent:
            self.model_matrix_global = np.dot(self.parent.model_matrix_global, self.model_matrix)
            self.normal_matrix_global = np.dot(self.parent.normal_matrix_global, self.normal_matrix)
            self.view_matrix_global = np.dot(self.parent.normal_matrix_global, self.normal_matrix)
        else:
            self.model_matrix_global = self.model_matrix
            self.normal_matrix_global = self.normal_matrix
            self.view_matrix_global = self.view_matrix

    @property
    def position_global(self):
        self.update()
        return tuple(self.model_matrix_global[:3, -1].tolist())


class Picklable(object):

    def save(self, filename):
        """Save the object to a file.  Will be Pickled in the process, but can be loaded easily with Class.load()"""
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, filename):
        """Load the object from a pickle file."""
        with open(filename) as f:
            obj = pickle.load(f)
            assert isinstance(obj, cls), "File's object is {}, but should be {}".format(type(obj), cls)
        return obj
