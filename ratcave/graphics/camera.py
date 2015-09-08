import numpy as np
import mixins as mixins


class Camera(mixins.Physical):
    """A convenient object for controlling the scene viewing angle."""

    def __init__(self, position=(0., 0., 0.), rotation=(0., 0., 0.), fov_y=60., aspect=16. / 9., z_near=.01, z_far=4.5, x_shift=0., y_shift=0., ortho_mode=False):

        """Returns a new Camera object.
        Optional Keyword Arguments:
            -position: [x, y, z]
            -rot_vector: [x, y, z]
            -int rot_amount: degrees of rotation about rot_vector axis
            -float fov_y: vertical field of view
            -float aspect: screen width/height
            -float z_near:  near clipping distance
            -float z_far:   far clipping distance
            -float xshift: horizontal lens shift
            -float yshift: vertical lens shift
        """
        mixins.Physical.__init__(self, position, rotation)

        # Set intrinsic Camera attributes (must be manually applied using update() method during Scene.draw())
        self.__fov_y = fov_y
        self.__aspect = aspect
        self.__zNear = z_near
        self.__zFar = z_far
        self.__x_shift = x_shift
        self.__y_shift = y_shift
        self._shift_matrix = np.zeros(16)  # Will be Transposed Lens-shift matrix (because OpenGL is in column-major order)
        self._set_shift_matrix()


        # Enable 2D Camera Mode.
        self.__ortho_mode = ortho_mode

        # Save projection matrix
        self._projection_matrix = np.zeros(16)
        self._projection_view_matrix = np.zeros(16)
        self.update()

    @property
    def ortho_mode(self):
        return self.__ortho_mode

    @ortho_mode.setter
    def ortho_mode(self, value):
        self.__ortho_mode = value
        self.update()

    @property
    def fov_y(self):
        return self.__fov_y

    @fov_y.setter
    def fov_y(self, value):
        self.__fov_y = value
        self.update()

    @property
    def aspect(self):
        return self.__aspect

    @aspect.setter
    def aspect(self, value):
        self.__aspect = value
        self.update()

    @property
    def zNear(self):
        return self.__zNear

    @zNear.setter
    def zNear(self, value):
        self.__zNear = value
        self.update()

    @property
    def zFar(self):
        return self.__zFar

    @zFar.setter
    def zFar(self, value):
        self.__zFar = value
        self.update()

    @property
    def x_shift(self):
        return self.__x_shift

    @x_shift.setter
    def x_shift(self, value):
        self.__x_shift = value
        self._set_shift_matrix()

    @property
    def y_shift(self):
        return self.__y_shift

    @y_shift.setter
    def y_shift(self, value):
        self.__y_shift = value
        self._set_shift_matrix()

    def _set_shift_matrix(self):
        """Create Transposed Lens-shift matrix (because OpenGL is in column-major order)"""
        self._shift_matrix = np.array([[1.,           0.,           self.x_shift, 0.],
                                       [0.,           1.,           self.y_shift, 0.],
                                       [0.,           0.,                     1., 0.],
                                       [0.,           0.,                     0., 1.]])

    def update(self):
        """Applies perspective changes to rendering during Scene.draw() loop."""

        rom = lambda x,y: -float(x+y)/(x-y)
        zN, zF = self.zNear, self.zFar

        if self.ortho_mode == True:  # Use orthographic projection if enabled, else use a perspective projection.
            # replace glOrtho (https://www.opengl.org/sdk/docs/man2/xhtml/glOrtho.xml)

            persp_mat = np.array([[(2.)/(2),      0.,         0., 0.], #  2/(right-left), x
                                  [                   0., 2./(2./self.aspect),         0., 0.], #  2/(top-bottom), y
                                  [                   0.,      0., -2/(zF-zN), 0.], # -2/(zFar-zNear), z
                                  [                   0.,      0.,         0., 1.]])

        else:
            # replace gluPerspective (https://www.opengl.org/sdk/docs/man2/xhtml/gluPerspective.xml)
            ff = 1./np.tan(np.radians(self.fov_y / 2.)) # cotangent(fovy/2)
            persp_mat =  np.array([[ff/self.aspect,    0.,              0.,                 0.],
                                  [             0.,    ff,              0.,                 0.],
                                  [             0.,    0., (zF+zN)/(zN-zF), (2.*zF*zN)/(zN-zF)],
                                  [             0.,    0.,             -1.,                 0.]])
            persp_mat = np.dot(persp_mat, self._shift_matrix)  # Apply lens shift


        self._projection_matrix = persp_mat.transpose().flatten()



