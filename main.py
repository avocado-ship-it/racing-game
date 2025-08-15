import pygame
import time
import math
from utils import scale_image, blit_rotate_center

pygame.init()  

GRASS = scale_image(pygame.image.load("assets/grass.jpg"), 2.5)
TRACK = scale_image(pygame.image.load("assets/track.png"), 0.9)
TRACK_BORDER = scale_image(pygame.image.load("assets/track-border.png"), 0.9)
FINISH = pygame.image.load("assets/finish.png")
RED_CAR = scale_image(pygame.image.load("assets/red-car.png"), 0.55)
GREEN_CAR = scale_image(pygame.image.load("assets/green-car.png"), 0.55)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("generic racing game")
FPS = 60

class AbstractCar:
    

    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.41

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_foreward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        
    def move (self):
        

class PlayerCar(AbstractCar):
    IMG = RED_CAR
    START_POS = (180, 200)

def draw(win, images, player_car):
    for img, pos in images:
        win.blit(img, pos)

    player_car.draw(win)
    pygame.display.update()

images = [(GRASS, (0, 0)), (TRACK, (0, 0)), (FINISH, (0, 0))]
run = True
clock = pygame.time.Clock()
player_car =  PlayerCar(6, 7)

while run:
    clock.tick(FPS)
    
    
    draw(WIN, images, player_car)
    pygame.display.update()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

    keys = pygame.key.get_pressed()

    if keys[pygame.K_a]:
        player_car.rotate(left=True)
    if keys[pygame.K_d]:
        player_car.rotate(right=True)

pygame.quit()