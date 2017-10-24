import sys
import pygame
from pygame.locals import *
import ratcave as rc

pygame.init()
win = pygame.display.set_mode((800, 600), pygame.OPENGL)

shader = rc.Shader.from_file(*rc.resources.genShader)

player_3d = rc.WavefrontReader(rc.resources.obj_primitives).get_mesh('Cube', scale=.1, position=(0, 0, -1))
player_3d.uniforms['diffuse'] = 1., 1., 0.

scene = rc.Scene(meshes=[player_3d])

held_keys = set()
while True:
    speed, dt = .1, .016
    dist = speed * dt
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
            player_3d.position.x -= dist
        elif key == K_RIGHT:
            player_3d.position.x += dist
        elif key == K_DOWN:
            player_3d.position.y -= dist
        elif key == K_UP:
            player_3d.position.y += dist

    player_3d.rotation.z += 30 * dt

    with shader:
        scene.draw()
    pygame.display.flip()
