import pyglet
from pyglet.window import key
from pyglet.image import SolidColorImagePattern


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


class App(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)
        pyglet.clock.schedule(self.check_keystate)

        self.batch = pyglet.graphics.Batch()
        self.player = Player(batch=self.batch, x=300, y=200, speed=300)

    def on_draw(self):
        self.clear()
        self.batch.draw()

    def check_keystate(self, dt):
        player, keys = self.player, self.keys
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