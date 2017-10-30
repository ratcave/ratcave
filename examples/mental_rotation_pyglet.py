import pyglet
from pyglet.window import key
from pyglet.image import SolidColorImagePattern
import ratcave as rc

class Player(pyglet.sprite.Sprite):

    def __init__(self, speed=300, *args, **kwargs):
        color = SolidColorImagePattern(color=(255, 255, 0, 255))
        img = color.create_image(100, 100)
        img.anchor_x = img.width // 2
        img.anchor_y = img.height // 2
        super(self.__class__, self).__init__(img, *args, **kwargs)

        self.speed = speed
        pyglet.clock.schedule(self.update)

    def update(self, dt):
        self.rotation += 30 * dt


class Player3D:

    def __init__(self, speed=10, x=0, y=0, z=-1):
        self.mesh = rc.WavefrontReader(rc.resources.obj_primitives).get_mesh('Cube', scale=.1, position=(x, y, z))
        self.mesh.uniforms['diffuse'] = 1, 1., 0.
        self.speed = speed
        pyglet.clock.schedule(self.update)

    @property
    def x(self):
        return self.mesh.position.x

    @x.setter
    def x(self, value):
        self.mesh.position.x = value

    @property
    def y(self):
        return self.mesh.position.y

    @y.setter
    def y(self, value):
        self.mesh.position.y = value

    @property
    def rotation(self):
        return self.mesh.rotation.z

    @rotation.setter
    def rotation(self, value):
        self.mesh.rotation.z = value

    def update(self, dt):
        self.rotation += -30 * dt


class App(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)
        pyglet.clock.schedule(self.check_keystate)

        self.batch = pyglet.graphics.Batch()

        self.player = Player(batch=self.batch, x=300, y=200, speed=300)
        self.player_3d = Player3D(x=0, y=0, speed=3)
        self.game_scene = rc.Scene(meshes=[self.player_3d.mesh])
        self.shader = rc.Shader.from_file(*rc.resources.genShader)

    def on_draw(self):
        self.clear()

        with self.shader:
            self.game_scene.draw()

        self.batch.draw()


    def check_keystate(self, dt):
        player, keys = self.player_3d, self.keys
        dist = player.speed * dt
        if keys[key.RIGHT]:
            player.x += dist
        if keys[key.LEFT]:
            player.x -= dist
        if self.keys[key.UP]:
            player.y += dist
        if self.keys[key.DOWN]:
            player.y -= dist



if __name__ == '__main__':
    app = App()
    pyglet.app.run()