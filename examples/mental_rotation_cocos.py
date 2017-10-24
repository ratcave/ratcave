import pyglet
from pyglet.window import key
from pyglet.image import SolidColorImagePattern
import cocos
import ratcave as rc


class Player(cocos.sprite.Sprite):

    def __init__(self, speed=300, *args, **kwargs):
        color = SolidColorImagePattern(color=(255, 255, 0, 255))
        img = color.create_image(100, 100)
        img.anchor_x = img.width // 2
        img.anchor_y = img.height // 2
        super(self.__class__, self).__init__(img, *args, **kwargs)

        self.speed = speed
        self.schedule(self.update)

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


class HelloWorld(cocos.layer.Layer):

    is_event_handler = True

    def __init__(self):
        super(self.__class__, self).__init__()

        self.player = Player()
        self.add(self.player)

        self.player_3d = Player3D(x=0, y=0, speed=3)
        self.game_scene = rc.Scene(meshes=[self.player_3d.mesh])
        self.shader = rc.Shader.from_file(*rc.resources.genShader)

        self.keys_pressed = set()#
        self.schedule(self.check_keystate)

    def on_key_press(self, key, mod):
        self.keys_pressed.add(key)

    def on_key_release(self, key, mod):
        try:
            self.keys_pressed.remove(key)
        except KeyError:
            pass

    def check_keystate(self, dt):
        player, keys = self.player_3d, self.keys_pressed
        dist = player.speed * dt
        if key.RIGHT in keys:
            player.x += dist
        if key.LEFT in keys:
            player.x -= dist
        if key.UP in keys:
            player.y += dist
        if key.DOWN in keys:
            player.y -= dist

    def draw(self):
        with self.shader:
            self.game_scene.draw()

class IntroMenu(cocos.layer.Layer):

    is_event_handler = True

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        text = """Press Space to Begin."""
        label = cocos.text.Label(text)
        self.add(label)

    def on_key_press(self, pressed, mod):
        if pressed == key.SPACE:
            print('Space Pressed.')
            cocos.director.director.replace(main_scene)



cocos.director.director.init()


hello_layer = HelloWorld()
main_scene = cocos.scene.Scene(hello_layer)

intro_layer = IntroMenu()
intro_scene = cocos.scene.Scene(intro_layer)

if __name__ == '__main__':
    print([el for el in dir(cocos.director.director) if not '_' in el[0]])

    cocos.director.director.run(intro_scene)

