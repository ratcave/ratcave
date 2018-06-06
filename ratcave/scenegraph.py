from collections import deque

# TODO: Check for loops and duplicate nodes in the Scene graph
class SceneGraph(object):

    def __init__(self, parent=None, children=None, **kwargs):
        """A Node of the Scenegraph.  Has children, but no parent."""
        super(SceneGraph, self).__init__(**kwargs)
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
        # TODO: change to set_parent
        """A SceneNode object that is this object's parent in the scene graph."""
        return self._parent

    @parent.setter
    def parent(self, value):
        assert isinstance(value, SceneGraph)
        if self._parent is not None:
            self._parent._children.remove(self)
        self._parent = value
        self._parent._children.append(self)

    def add_child(self, child):
        """Adds an object as a child in the scene graph."""
        if not issubclass(child.__class__, SceneGraph):
            raise TypeError("child must have parent/child iteration implemented to be a node in a SceneGraph.")
        # if not hasattr(child, 'update'):
            # raise TypeError("child must have an attribute update()")

        child._parent = self
        self._children.append(child)

    def add_children(self, *children, **kwargs):
        """Conveniience function: Adds objects as children in the scene graph."""
        for child in children:
            self.add_child(child, **kwargs)

    def remove_children(self, *children):
        for child in children:
            child._parent = None
            self._children.remove(child)

    @property
    def children(self):
        return tuple(self._children)
