from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.resources import resource_find
from kivy.graphics.transformation import Matrix
from kivy.graphics.opengl import *
from kivy.graphics import *
from objloader import ObjFile
import ratcave as rc

class Renderer(Widget):
    def __init__(self, **kwargs):
        self.canvas = RenderContext(compute_normal_mat=True)
        self.scene = rc.Scene(meshes=[rc.WavefrontReader(rc.resources.obj_primitives).get_mesh('Monkey', position=(0, 0, -3))])

        super(Renderer, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_glsl, 1 / 60.)

    def update_glsl(self, *largs):
        with self.canvas:
            # with self.shader:
            #     self.scene.draw()
            pass
            # self.scene.meshes[0].draw()
        # pass


    # def setup_scene(self):
    #     Color(1, 1, 1, 1)
    #     PushMatrix()
    #     Translate(0, 0, -3)
    #     self.rot = Rotate(1, 0, 1, 0)
    #     m = list(self.scene.objects.values())[0]
    #     UpdateNormalMatrix()
    #     self.mesh = Mesh(vertices=m.vertices, indices=m.indices, fmt=m.vertex_format, mode='triangles')
    #     PopMatrix()


class RendererApp(App):
    def build(self):
        return Renderer()


if __name__ == "__main__":
    RendererApp().run()