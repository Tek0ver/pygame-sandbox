from typing import Any
import pygame
from sys import exit
from time import time
import pygame._sdl2.controller

pygame.init()

clock = pygame.Clock()

screen = pygame.display.set_mode((1000,1000))

pygame._sdl2.controller.init()

controllers = [pygame._sdl2.controller.Controller(x) for x in range(pygame._sdl2.controller.get_count())]

joystick_deadzone = 15000


class Tank(pygame.sprite.Sprite):

    def __init__(self, pos):
        super().__init__()

        self.image_source = pygame.image.load("tank.png").convert_alpha()
        self.image = self.image_source
        self.rect = self.image.get_frect(center=pos)

        self.vector_base = pygame.math.Vector2(-1,0)
        self.vector = self.vector_base

        self.turret = Turret(self.rect.center, self.vector_base)
        group_turret.add(self.turret)

        self.speed = 3
        self.rotation_speed = 1

    def update(self):

        self.get_input()
        self.turret.update(self.rect.center)
        self.animation()

    def animation(self):

        rotation = self.vector.angle_to(self.vector_base)
        self.image = pygame.transform.rotate(self.image_source, rotation)
        self.rect = self.image.get_frect(center=self.rect.center)

    def get_input(self):

        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP] or controllers[0].get_axis(pygame.CONTROLLER_AXIS_LEFTY) < -joystick_deadzone:
            self.rect.center += self.vector*self.speed
        if keys[pygame.K_DOWN] or controllers[0].get_axis(pygame.CONTROLLER_AXIS_LEFTY) > joystick_deadzone:
            self.rect.center -= self.vector*self.speed
        if keys[pygame.K_LEFT]  or controllers[0].get_axis(pygame.CONTROLLER_AXIS_LEFTX) < -joystick_deadzone:
            self.vector = self.vector.rotate(-self.rotation_speed)
        if keys[pygame.K_RIGHT] or controllers[0].get_axis(pygame.CONTROLLER_AXIS_LEFTX) > joystick_deadzone:
            self.vector = self.vector.rotate(self.rotation_speed)


class Turret(pygame.sprite.Sprite):

    def __init__(self, pos, vector:pygame.math.Vector2):
        super().__init__()

        self.vector_base = vector
        self.vector = self.vector_base

        self.image_source = pygame.image.load("turret.png").convert_alpha()
        self.image = self.image_source
        self.rect = self.image.get_frect(center=pos)

        self.lenght = 50

        self.timer = Timer(0.5)

    def update(self, pos):

        self.rect.center = pos
        self.get_input()
        self.animation()

    def animation(self):

        rotation = self.vector.angle_to(self.vector_base)
        self.image = pygame.transform.rotate(self.image_source, rotation)
        self.rect = self.image.get_frect(center=self.rect.center)

    def get_input(self):

        mouse_cursor = pygame.mouse.get_pos()
        mouse_vector = pygame.math.Vector2(
            mouse_cursor[0] - self.rect.centerx,
            mouse_cursor[1] - self.rect.centery)

        self.vector = self.vector.rotate(self.vector.angle_to(mouse_vector))

        if pygame.mouse.get_pressed()[0] or controllers[0].get_button(pygame.CONTROLLER_BUTTON_A):
            self.shoot()            

    def shoot(self):
        if self.timer.check():
            spawn_point = (
                self.rect.centerx + self.vector.x * self.lenght,
                self.rect.centery + self.vector.y * self.lenght)
            group_projectiles.add(Bullet(spawn_point, self.vector))
            controllers[0].rumble(1,0,250)



class Bullet(pygame.sprite.Sprite):

    def __init__(self, pos, vector):
        super().__init__()

        self.image = pygame.Surface((10,10))
        self.image.fill("red")
        self.rect = self.image.get_frect(center=pos)

        group_projectiles.add(self)

        self.vector = vector
        self.speed = 10

    def update(self):

        self.rect.center += self.vector * self.speed


class Timer():

    def __init__(self, delay):

        self.delay = delay
        self.last_call = 0

    def check(self):

        if time() - self.last_call >= self.delay:
            self.last_call = time()
            return True
        return False


group_tank = pygame.sprite.GroupSingle()
group_turret = pygame.sprite.GroupSingle()
group_projectiles = pygame.sprite.Group()

while True:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                group_tank.add(Tank((screen.get_width()/2, screen.get_height()/2)))

    screen.fill("grey")

    group_tank.update()
    group_projectiles.update()

    group_tank.draw(screen)
    group_turret.draw(screen)
    group_projectiles.draw(screen)

    pygame.display.flip()

    clock.tick(60)
    # print(clock.get_fps())
