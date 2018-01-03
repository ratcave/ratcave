import pyglet.gl as gl


class GLStateManager(object):

    def __init__(self, states=(gl.GL_DEPTH_TEST, gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_2D)):
        self.states = states

    def __enter__(self):
        self.enable()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disable()

    def enable(self):
        for state in self.states:
            gl.glEnable(state)

    def disable(self):
        for state in self.states:
            gl.glDisable(state)


default_states = GLStateManager()