from typing import Any
import pygame
from sys import exit
from time import time
import pygame._sdl2.controller
from random import choice

pygame.init()

clock = pygame.Clock()

screen = pygame.display.set_mode((1000,1000))

pygame._sdl2.controller.init()

controllers = [pygame._sdl2.controller.Controller(x) for x in range(pygame._sdl2.controller.get_count())]
if len(controllers) == 0:
    controller_mode = False
else:
    controller_mode = True

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
        self.turret_speed = 2

    def update(self):

        self.get_input()
        self.turret.update(self.rect.center)
        self.animation()

    def animation(self):

        rotation = self.vector.angle_to(self.vector_base)
        self.image = pygame.transform.rotate(self.image_source, rotation)
        self.rect = self.image.get_frect(center=self.rect.center)

    def move(self, dir: str):

        if dir == 'forward':
            self.rect.center += self.vector*self.speed
        elif dir == 'backward':
            self.rect.center -= self.vector*self.speed

    def turn(self, dir: str):

        if dir == 'pos':
            self.vector = self.vector.rotate(-self.rotation_speed)
        elif dir == 'neg':
            self.vector = self.vector.rotate(self.rotation_speed)

    def turn_turret(self, dir:str):
        
        if dir == 'pos':
            self.turret.vector.rotate_ip(- self.turret_speed)
        elif dir == 'neg':
            self.turret.vector.rotate_ip(self.turret_speed)

    def get_input(self):

        keys = pygame.key.get_pressed()

        # move
        if controller_mode:
            if keys[pygame.K_UP] or controllers[0].get_axis(pygame.CONTROLLER_AXIS_LEFTY) < -joystick_deadzone:
                self.move('forward')
            if keys[pygame.K_DOWN] or controllers[0].get_axis(pygame.CONTROLLER_AXIS_LEFTY) > joystick_deadzone:
                self.move('backward')
            if keys[pygame.K_LEFT] or controllers[0].get_axis(pygame.CONTROLLER_AXIS_LEFTX) < -joystick_deadzone:
                self.turn('pos')
            if keys[pygame.K_RIGHT] or controllers[0].get_axis(pygame.CONTROLLER_AXIS_LEFTX) > joystick_deadzone:
                self.turn('neg')
        else:
            if keys[pygame.K_UP]:
                self.move('forward')
            if keys[pygame.K_DOWN]:
                self.move('backward')
            if keys[pygame.K_LEFT]:
                self.turn('pos')
            if keys[pygame.K_RIGHT]:
                self.turn('neg')
            if keys[pygame.K_q]:
                self.turn_turret('pos')
            if keys[pygame.K_d]:
                self.turn_turret('neg')
            if keys[pygame.K_SPACE]:
                self.turret.shoot()

        # # turret
        # mouse_cursor = pygame.mouse.get_pos()
        # mouse_vector = pygame.math.Vector2(
        #     mouse_cursor[0] - self.turret.rect.centerx,
        #     mouse_cursor[1] - self.turret.rect.centery)
        
        # if controller_mode:
        #     controller_vector = pygame.math.Vector2(
        #         controllers[0].get_axis(pygame.CONTROLLER_AXIS_RIGHTX),
        #         controllers[0].get_axis(pygame.CONTROLLER_AXIS_RIGHTY))
        
        #     if controller_vector.magnitude() < joystick_deadzone:
        #         # self.turn_turret(controller_vector)
        #         pass

        #     if controllers[0].get_axis(pygame.CONTROLLER_AXIS_TRIGGERRIGHT) > 10000:
        #         self.turret.shoot()

        # else:
        #     # self.turn_turret(mouse_vector)
        #     self.turn_turret('pos')
        #     if pygame.mouse.get_pressed()[0]:
        #         self.turret.shoot()   


class AiTank(Tank):

    def __init__(self, pos):
        super().__init__(pos)

        self.possible_actions = [
            (self.move, ('forward')),
            (self.move, ('backward')),
            (self.turn, ('pos')),
            (self.turn, ('neg')),
            (self.turn_turret, ('pos')),
            (self.turn_turret, ('neg')),
            (self.turret.shoot, ()),
        ]

    def get_input(self):
        
        action = choice(self.possible_actions)

        if action[1]:
            action[0](action[1])
        else:
            action[0]()


class Turret(pygame.sprite.Sprite):

    def __init__(self, pos, vector:pygame.math.Vector2):
        super().__init__()

        self.vector_base = pygame.math.Vector2(vector)
        self.vector = pygame.math.Vector2(self.vector_base)

        self.image_source = pygame.image.load("turret.png").convert_alpha()
        self.image = self.image_source
        self.rect = self.image.get_frect(center=pos)

        self.lenght = 50

        self.timer = Timer(0.5)

    def update(self, pos):

        self.rect.center = pos
        self.animation()

    def animation(self):

        rotation = self.vector.angle_to(self.vector_base)
        self.image = pygame.transform.rotate(self.image_source, rotation)
        self.rect = self.image.get_frect(center=self.rect.center)        

    def shoot(self):
        if self.timer.check():
            spawn_point = (
                self.rect.centerx + self.vector.x * self.lenght,
                self.rect.centery + self.vector.y * self.lenght)
            group_projectiles.add(Bullet(spawn_point, self.vector))

            if controller_mode:
                controllers[0].rumble(1,0,250)


class Bullet(pygame.sprite.Sprite):

    def __init__(self, pos, vector):
        super().__init__()

        self.image = pygame.Surface((10,10))
        self.image.fill("red")
        self.rect = self.image.get_frect(center=pos)

        group_projectiles.add(self)

        self.vector = pygame.math.Vector2(vector)
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


group_tank = pygame.sprite.Group()
group_turret = pygame.sprite.Group()
group_projectiles = pygame.sprite.Group()

while True:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                group_tank.add(AiTank((screen.get_width()/5, screen.get_height()/5)))
                group_tank.add(Tank((screen.get_width()*(4/5), screen.get_height()*(4/5))))

    screen.fill("grey")

    group_tank.update()
    group_projectiles.update()
        
    for tank in group_tank.sprites():
        if tank.rect.x < 0:
            tank.rect.x = 0
        elif tank.rect.x > screen.get_width() - tank.rect.width:
            tank.rect.x = screen.get_width() - tank.rect.width
        if tank.rect.y < 0:
            tank.rect.y = 0
        elif tank.rect.y > screen.get_height() - tank.rect.height:
            tank.rect.y = screen.get_height() - tank.rect.height

    for projectile in group_projectiles.sprites():
        if projectile.rect.centerx < 0:
            projectile.kill()
        elif projectile.rect.centerx > screen.get_width():
            projectile.kill()
        if projectile.rect.centery < 0:
            projectile.kill()
        elif projectile.rect.centery > screen.get_height():
            projectile.kill()

    group_tank.draw(screen)
    group_turret.draw(screen)
    group_projectiles.draw(screen)

    pygame.display.flip()

    clock.tick(60)
    # print(clock.get_fps())
