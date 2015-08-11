__author__ = 'nickdg'

import math

class PositionMixin(object):

    def __init__(self):
        super(PositionMixin, self).__init__()
        self.x, self.y, self.z = (0, 0, 0)

    @property
    def position(self):
        return (self.x, self.y, self.z)

    @position.setter
    def position(self, value):
        if value is not None:
            self.x, self.y, self.z = value


class Marker(PositionMixin):

    def __init__(self, position=(0,0,0), name='', id=None, size=None):
        super(Marker, self).__init__()
        self.name = name
        self.id = id
        self.size = size
        self.position = position

        # Optitrack-Provided attributes for labelled markers.
        self.occluded = None
        self.pc_solved = None
        self.model_solved = None

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "Marker at [{:3.2f}, {:3.2f}, {:3.2f}]".format(self.position[0], self.position[1], self.position[2])


class MarkerSet(object):

    def __init__(self, name='', id=None):
        self.name = name
        self.id = id
        self.markers = []


class RigidBody(PositionMixin):

    def __init__(self, name='', markers=[], id=None, parent_id=None, offset=(0., 0., 0.)):
        super(RigidBody, self).__init__()
        self.name = name
        self.id = id
        self.markers = markers
        self.error = None  # Mean marker error
        self.seen = True  # Indicates that Tracking was successful this frame.
        self.offset = offset  # (x, y, z) offset

        self.rot_x, self.rot_y, self.rot_z = (0, 0, 0)

    @property
    def rotation(self):
        return self.rot_x, self.rot_y, self.rot_z

    @rotation.setter
    def rotation(self, value):
        if len(value) == 3:
            self.rot_x, self.rot_y, self.rot_z = value
        elif len(value) == 4:
            self.rot_x, self.rot_y, self.rot_z = self.quaternion_to_euclid(*value)

    def quaternion_to_euclid(self, qx, qy, qz, qw):
        """Convert quaternion (qx, qy, qz, qw) angle to euclidean (x, y, z) angles, in degrees"""
        #o_x, o_y, o_z, o_w = qx, qy, qz, qw
        qx, qy, qz, qw = qz, qy, -qx, -qw


        len_q = math.sqrt(qw**2 + qx**2 + qy**2 + qz**2)
        qw, qx, qy, qz = [el/len_q for el in [qw, qx, qy, qz]]

        # Equation from http://www.euclideanspace.com/maths/geometry/rotations/conversions/quaternionToEuler/
        heading = math.atan2(2*qy*qw-2*qx*qz , 1 - 2*qy**2 - 2*qz**2)
        attitude = math.asin(2*qx*qy + 2*qz*qw)
        bank = math.atan2(2*qx*qw-2*qy*qz , 1 - 2*qx**2 - 2*qz**2)

        # Correct the axis assignment, and correct for left-handed orientation.
        y, x, z = -heading, -attitude, bank
        x, y, z = -x, y, -z
        # Convert from radians to degrees and return new rotation list

        x, y, z = [math.degrees(angle) for angle in [x, y, z]]

        return x, y, z







