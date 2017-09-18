import sys
import pygame
from pygame.locals import *



class Player(pygame.sprite.Sprite):

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        self.image = pygame.Surface([100, 100])
        self.image.fill((255, 255, 0))
        self.image.set_colorkey((255, 0, 0))
        self.rect = self.image.get_rect()

    @property
    def x(self):
        return self.rect.x

    @x.setter
    def x(self, value):
        self.rect.x = value

    @property
    def y(self):
        return self.rect.y

    @y.setter
    def y(self, value):
        self.rect.y = value

    @property
    def pos(self):
        return self.rect.x, self.rect.y

    @pos.setter
    def pos(self, value):
        self.rect.x, self.rect.y = value

    def rotate(self, angle):
        loc = self.rect.center
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()
        self.rect.center = loc



pygame.init()
win = pygame.display.set_mode((800, 600))

player = Player()
held_keys = set()
while True:
    dist = 10
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            held_keys.add(event.key)
        elif event.type == pygame.KEYUP:
            try:
                held_keys.remove(event.key)
            except KeyError:
                pass

    for key in held_keys:
        if key == K_ESCAPE:
            pygame.quit()
            sys.exit()
        elif key == K_LEFT:
            player.x -= dist
        elif key == K_RIGHT:
            player.x += dist
        elif key == K_DOWN:
            player.y += dist
        elif key == K_UP:
            player.y -= dist

    win.fill((0, 0, 0))
    win.blit(player.image, (player.rect.x, player.rect.y))
    pygame.display.flip()
    pygame.time.wait(60)