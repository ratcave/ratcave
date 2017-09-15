import pyglet
from pyglet.window import key
from pyglet.image import SolidColorImagePattern

import cocos
from cocos.actions import *

class Player(cocos.sprite.Sprite):

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


class HelloWorld(cocos.layer.Layer):

    is_event_handler = True

    def __init__(self):
        super(self.__class__, self).__init__()

        self.player = Player()
        self.add(self.player)

        self.keys_pressed = set()#
        pyglet.clock.schedule(self.check_keystate)

    def on_key_press(self, key, mod):
        self.keys_pressed.add(key)

    def on_key_release(self, key, mod):
        self.keys_pressed.remove(key)

    def check_keystate(self, dt):
        player, keys = self.player, self.keys_pressed
        dist = player.speed * dt
        if key.RIGHT in keys:
            player.x += dist
        if key.LEFT in keys:
            player.x -= dist
        if key.UP in keys:
            player.y += dist
        if key.DOWN in keys:
            player.y -= dist




cocos.director.director.init()
hello_layer = HelloWorld()

main_scene = cocos.scene.Scene(hello_layer)

if __name__ == '__main__':
    cocos.director.director.run(main_scene)

