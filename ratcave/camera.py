

import numpy as np
from . import mixins
import pyglet.gl as gl

class Camera(mixins.PhysicalNode, mixins.Picklable):
    """A convenient object for controlling the scene viewing angle."""

    def __init__(self, fov_y=60., aspect=1.778, z_near=.01, z_far=4.5, x_shift=0., y_shift=0.,
                 ortho_mode=False, **kwargs):
        """
        Returns a Camera instance, which determines the world-to-screen perspective transformation.

        Args:
            fov_y (float): vertical field of view (degrees)
            aspect (float): screen width/height
            z_near (float): near clipping distance
            z_far (float): far clipping distance
            x_shift (float): horizontal lens shift
            y_shift (float): vertical lens shift
            ortho_mode (bool): Whether to use orthographic projection instead of perpective projection.

        Return:
            Camera instance
        """


        # Set intrinsic Camera attributes (must be manually applied using update() method during Scene.draw())
        self.fov_y = fov_y
        self.aspect = aspect
        self.zNear = z_near
        self.zFar = z_far
        self.x_shift = x_shift
        self.y_shift = y_shift
        self.ortho_mode = ortho_mode

        # Assign matrix attributes, then set them with the update_matrices() method.
        self.projection_matrix = None
        self.shift_matrix = None

        super(Camera, self).__init__(**kwargs)
        self.update()

    def _update_shift_matrix(self):
        """np.array: The Camera's lens-shift matrix."""
        self.shift_matrix =  np.array([[1.,           0.,           self.x_shift, 0.],
                         [0.,           1.,           self.y_shift, 0.],
                         [0.,           0.,                     1., 0.],
                         [0.,           0.,                     0., 1.]])

    def _update_projection_matrix(self):
        """np.array: The Camera's Projection Matrix.  Will be an Orthographic matrix if ortho_mode is set to True."""

        zn, zf = self.zNear, self.zFar

        # Use orthographic projection if enabled, else use a perspective projection.
        if self.ortho_mode == True:
            # replace glOrtho (https://www.opengl.org/sdk/docs/man2/xhtml/glOrtho.xml)

            persp_mat = np.array([[(2.)/(2),                  0.,         0., 0.], #  2/(right-left), x
                                  [      0., 2./(2./self.aspect),         0., 0.], #  2/(top-bottom), y
                                  [      0.,                  0., -2/(zf-zn), 0.], # -2/(zFar-zNear), z
                                  [      0.,                  0.,         0., 1.]])

        else:
            # replace gluPerspective (https://www.opengl.org/sdk/docs/man2/xhtml/gluPerspective.xml)
            ff = 1./np.tan(np.radians(self.fov_y / 2.)) # cotangent(fovy/2)
            persp_mat =  np.array([[ff/self.aspect,    0.,              0.,                 0.],
                                  [             0.,    ff,              0.,                 0.],
                                  [             0.,    0., (zf+zn)/(zn-zf), (2.*zf*zn)/(zn-zf)],
                                  [             0.,    0.,             -1.,                 0.]])
            persp_mat = np.dot(persp_mat, self.shift_matrix)  # Apply lens shift

        self.projection_matrix = persp_mat

    def update(self):
        super(Camera, self).update()
        self._update_shift_matrix()
        self._update_projection_matrix()

    def reset_aspect(self):
        """Gets the viewport size, and matches the camera aspect ratio to it."""
        viewport_size = (gl.GLint * 4)()
        gl.glGetIntegerv(gl.GL_VIEWPORT, viewport_size)
        self.aspect = float(viewport_size[2]) / viewport_size[3]


