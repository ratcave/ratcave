orig_keys = set(globals().keys())

import sys
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Material, DirectionalLight


class CubeDemo(ShowBase):

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.models = loader.loadModel('models.egg')
        self.accept('escape', sys.exit)
        self.models.reparentTo(render)
        self.models.setPos(0, 4, 0)

        dlight = DirectionalLight('dlight')
        dlight.setColor((1, 0, 0, 0))
        self.dlnp = render.attachNewNode(dlight)
        render.setLight(self.dlnp)


        myMaterial = Material()
        myMaterial.setShininess(50.0)  # Make this material shiny
        # myMaterial.setAmbient((0, 0, 1, 1))  # Make this material blue
        self.models.setMaterial(myMaterial)  # Apply the material to this nodePath


        self.models.setScale(.2)
        self.pressed_keys = set()
        self.accept("arrow_left", self.pressed_keys.add, ["left"])
        self.accept("arrow_left-up", self.pressed_keys.remove, ['left'])
        self.accept("arrow_right", self.pressed_keys.add, ["right"])
        self.accept("arrow_right-up", self.pressed_keys.remove, ['right'])
        self.accept("arrow_up", self.pressed_keys.add, ['up'])
        self.accept("arrow_up-up", self.pressed_keys.remove, ['up'])
        self.accept("arrow_down", self.pressed_keys.add, ['down'])
        self.accept("arrow_down-up", self.pressed_keys.remove, ['down'])

        self.accept("j", self.pressed_keys.add, ['light_left'])
        self.accept("j-up", self.pressed_keys.remove, ['light_left'])
        self.accept("k", self.pressed_keys.add, ['light_right'])
        self.accept("k-up", self.pressed_keys.remove, ['light_right'])

        taskMgr.add(self.rotate_models, "rotateTask")
        taskMgr.add(self.rotate_light, "rotateLightTask")

    def rotate_models(self, task):
        dt = globalClock.getDt()

        speed = 100. * dt
        if 'left' in self.pressed_keys:
            self.models.setHpr(self.models.getHpr() + (speed, 0, 0))
        if 'right' in self.pressed_keys:
            self.models.setHpr(self.models.getHpr() + (-speed, 0, 0))
        if 'up' in self.pressed_keys:
            self.models.setHpr(self.models.getHpr() + (0, speed, 0))
        if 'down' in self.pressed_keys:
            self.models.setHpr(self.models.getHpr() + (0, -speed, 0))

        return task.cont

    def rotate_light(self, task):

        dt = globalClock.getDt()
        speed = 100. * dt
        if 'light_left' in self.pressed_keys:
            self.dlnp.setPos(self.dlnp.getPos() + (-speed, 0, 0))
            render.setLight(self.dlnp)
        if 'light_right' in self.pressed_keys:
            self.dlnp.setPos(self.dlnp.getPos() + (speed, 0, 0))

        return task.cont

demo = CubeDemo()
demo.run()

new_keys = set(globals().keys())
