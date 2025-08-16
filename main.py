import pygame
import time
import math
from utils import scale_image, blit_rotate_center, blit_text_center
pygame.font.init()

GRASS = scale_image(pygame.image.load("assets/grass.jpg"), 2.5)
TRACK = scale_image(pygame.image.load("assets/track.png"), 0.9)

TRACK_BORDER = scale_image(pygame.image.load("assets/track-border.png"), 0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

FINISH = pygame.image.load("assets/finish.png")
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (130, 250)

RED_CAR = scale_image(pygame.image.load("assets/red-car.png"), 0.55)
GREEN_CAR = scale_image(pygame.image.load("assets/green-car.png"), 0.55)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("generic racing game")

MAIN_FONT = pygame.font.SysFont("comicsans", 44)
TITLE_FONT = pygame.font.SysFont("comicsans", 72, bold=True)
SUBTITLE_FONT = pygame.font.SysFont("comicsans", 36)
MENU_FONT = pygame.font.SysFont("comicsans", 28)

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
DARK_RED = (180, 0, 0)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

FPS = 60
PATH = [(175, 119), (110, 70), (56, 133), (70, 481), (318, 731), (404, 680), (418, 521), (507, 475), (600, 551), (613, 715), (736, 713),
        (734, 399), (611, 357), (409, 343), (433, 257), (697, 258), (738, 123), (581, 71), (303, 78), (275, 377), (176, 388), (178, 260)]

class GameState:
    HOME_SCREEN = 0
    PLAYING = 1
    LEVEL_START = 2
    GAME_OVER = 3
    VICTORY = 4

class GameInfo:
    LEVELS = 10

    def __init__(self, level=1):
        self.level = level
        self.started = False
        self.level_start_time = 0
        self.state = GameState.HOME_SCREEN
        self.total_time = 0
        self.best_time = float('inf')

    def next_level(self):
        self.level += 1
        self.started = False
        self.state = GameState.LEVEL_START

    def reset(self):
        if self.total_time < self.best_time and self.total_time > 0:
            self.best_time = self.total_time
        self.level = 1
        self.started = False
        self.level_start_time = 0
        self.total_time = 0
        self.state = GameState.HOME_SCREEN

    def game_finished(self):
        return self.level > self.LEVELS

    def start_level(self):
        self.started = True
        self.level_start_time = time.time()
        self.state = GameState.PLAYING

    def get_level_time(self):
        if not self.started:
            return 0
        return round(time.time() - self.level_start_time)

    def add_to_total_time(self):
        if self.started:
            self.total_time += self.get_level_time()

class AbstractCar:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel/2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0

class PlayerCar(AbstractCar):
    IMG = RED_CAR
    START_POS = (180, 200)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move()

class ComputerCar(AbstractCar):
    IMG = GREEN_CAR
    START_POS = (150, 200)

    def __init__(self, max_vel, rotation_vel, path=[]):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0
        self.vel = max_vel

    def draw_points(self, win):
        for point in self.path:
            pygame.draw.circle(win, (255, 0, 0), point, 5)

    def draw(self, win):
        super().draw(win)

    def calculate_angle(self):
        target_x, target_y = self.path[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if y_diff == 0:
            desired_radian_angle = math.pi / 2
        else:
            desired_radian_angle = math.atan(x_diff / y_diff)

        if target_y > self.y:
            desired_radian_angle += math.pi

        difference_in_angle = self.angle - math.degrees(desired_radian_angle)
        if difference_in_angle >= 180:
            difference_in_angle -= 360

        if difference_in_angle > 0:
            self.angle -= min(self.rotation_vel, abs(difference_in_angle))
        else:
            self.angle += min(self.rotation_vel, abs(difference_in_angle))

    def update_path_point(self):
        target = self.path[self.current_point]
        rect = pygame.Rect(
            self.x, self.y, self.img.get_width(), self.img.get_height())
        if rect.collidepoint(*target):
            self.current_point += 1

    def move(self):
        if self.current_point >= len(self.path):
            return

        self.calculate_angle()
        self.update_path_point()
        super().move()

    def next_level(self, level):
        self.reset()
        self.vel = self.max_vel + (level - 1) * 0.2
        self.current_point = 0

def draw_gradient_background(win, color1, color2):
    """Draw a vertical gradient background"""
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        pygame.draw.line(win, (r, g, b), (0, y), (WIDTH, y))

def draw_home_screen(win, game_info):
    # Gradient background
    draw_gradient_background(win, (30, 30, 50), (10, 10, 20))
    
    # Animated racing stripes
    stripe_offset = (time.time() * 100) % 40
    for i in range(0, WIDTH + 40, 40):
        x = i - stripe_offset
        pygame.draw.polygon(win, (100, 100, 100), [(x, 0), (x + 20, 0), (x + 10, HEIGHT), (x - 10, HEIGHT)])
    
    # Title with shadow effect
    title_text = "generic"
    title2_text = "racing game"
    
    # Shadow
    title_shadow = TITLE_FONT.render(title_text, True, BLACK)
    title2_shadow = TITLE_FONT.render(title2_text, True, BLACK)
    win.blit(title_shadow, (WIDTH//2 - title_shadow.get_width()//2 + 5, HEIGHT//4 + 5))
    win.blit(title2_shadow, (WIDTH//2 - title2_shadow.get_width()//2 + 5, HEIGHT//4 + 80 + 5))
    
    # Main title
    title_surface = TITLE_FONT.render(title_text, True, RED)
    title2_surface = TITLE_FONT.render(title2_text, True, WHITE)
    
    win.blit(title_surface, (WIDTH//2 - title_surface.get_width()//2, HEIGHT//4))
    win.blit(title2_surface, (WIDTH//2 - title2_surface.get_width()//2, HEIGHT//4 + 80))
    
    # Subtitle
    subtitle_text = "made by halia"
    subtitle_surface = SUBTITLE_FONT.render(subtitle_text, True, YELLOW)
    win.blit(subtitle_surface, (WIDTH//2 - subtitle_surface.get_width()//2, HEIGHT//4 + 160))
    
    # Menu options with boxes
    menu_y_start = HEIGHT//2 + 50
    
    # Start Game button
    start_text = "PRESS SPACE TO START"
    start_surface = MENU_FONT.render(start_text, True, GREEN)
    start_rect = pygame.Rect(WIDTH//2 - 150, menu_y_start, 300, 40)
    pygame.draw.rect(win, DARK_GRAY, start_rect)
    pygame.draw.rect(win, GREEN, start_rect, 3)
    win.blit(start_surface, (WIDTH//2 - start_surface.get_width()//2, menu_y_start + 8))
    
    # Controls
    controls_y = menu_y_start + 60
    controls_title = MENU_FONT.render("CONTROLS:", True, WHITE)
    win.blit(controls_title, (WIDTH//2 - controls_title.get_width()//2, controls_y))
    
    control_font = pygame.font.SysFont("arial", 20)
    controls = [
        "W - Accelerate",
        "S - Brake/Reverse",
        "A - Turn Left",
        "D - Turn Right"
    ]
    
    for i, control in enumerate(controls):
        control_surface = control_font.render(control, True, GRAY)
        win.blit(control_surface, (WIDTH//2 - control_surface.get_width()//2, controls_y + 30 + i * 25))
    
    # Best time display
    if game_info.best_time != float('inf'):
        best_time_text = f"Best Time: {game_info.best_time}s"
        best_time_surface = MENU_FONT.render(best_time_text, True, YELLOW)
        win.blit(best_time_surface, (WIDTH//2 - best_time_surface.get_width()//2, HEIGHT - 100))
    
    # Animated cars
    car_y = HEIGHT - 150
    red_car_x = 50 + math.sin(time.time() * 2) * 20
    green_car_x = WIDTH - 100 + math.sin(time.time() * 2 + math.pi) * 20
    
    blit_rotate_center(win, RED_CAR, (red_car_x, car_y), math.sin(time.time() * 3) * 5)
    blit_rotate_center(win, GREEN_CAR, (green_car_x, car_y), math.sin(time.time() * 3 + math.pi) * 5)
    
    pygame.display.update()

def draw_level_start_screen(win, game_info):
    # Semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(BLACK)
    win.blit(overlay, (0, 0))
    
    # Level announcement
    level_text = f"LEVEL {game_info.level}"
    level_surface = TITLE_FONT.render(level_text, True, RED)
    win.blit(level_surface, (WIDTH//2 - level_surface.get_width()//2, HEIGHT//2 - 100))
    
    # Ready text
    ready_text = "GET READY!"
    ready_surface = SUBTITLE_FONT.render(ready_text, True, WHITE)
    win.blit(ready_surface, (WIDTH//2 - ready_surface.get_width()//2, HEIGHT//2 - 20))
    
    # Start instruction
    start_text = "Press any key to start racing"
    start_surface = MENU_FONT.render(start_text, True, YELLOW)
    win.blit(start_surface, (WIDTH//2 - start_surface.get_width()//2, HEIGHT//2 + 40))
    
    pygame.display.update()

def draw_game(win, images, player_car, computer_car, game_info):
    for img, pos in images:
        win.blit(img, pos)

    # Game UI with better styling
    ui_font = pygame.font.SysFont("arial", 32, bold=True)
    
    # Level display
    level_text = ui_font.render(f"Level {game_info.level}", True, WHITE)
    level_rect = pygame.Rect(10, HEIGHT - 120, level_text.get_width() + 20, 35)
    pygame.draw.rect(win, (0, 0, 0, 180), level_rect)
    pygame.draw.rect(win, WHITE, level_rect, 2)
    win.blit(level_text, (20, HEIGHT - 115))

    # Time display
    time_text = ui_font.render(f"Time: {game_info.get_level_time()}s", True, WHITE)
    time_rect = pygame.Rect(10, HEIGHT - 80, time_text.get_width() + 20, 35)
    pygame.draw.rect(win, (0, 0, 0, 180), time_rect)
    pygame.draw.rect(win, WHITE, time_rect, 2)
    win.blit(time_text, (20, HEIGHT - 75))

    # Velocity display
    vel_text = ui_font.render(f"Speed: {round(player_car.vel, 1)}", True, WHITE)
    vel_rect = pygame.Rect(10, HEIGHT - 40, vel_text.get_width() + 20, 35)
    pygame.draw.rect(win, (0, 0, 0, 180), vel_rect)
    pygame.draw.rect(win, WHITE, vel_rect, 2)
    win.blit(vel_text, (20, HEIGHT - 35))

    player_car.draw(win)
    computer_car.draw(win)
    pygame.display.update()

def move_player(player_car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a]:
        player_car.rotate(left=True)
    if keys[pygame.K_d]:
        player_car.rotate(right=True)
    if keys[pygame.K_w]:
        moved = True
        player_car.move_forward()
    if keys[pygame.K_s]:
        moved = True
        player_car.move_backward()

    if not moved:
        player_car.reduce_speed()

def handle_collision(player_car, computer_car, game_info):
    if player_car.collide(TRACK_BORDER_MASK) != None:
        player_car.bounce()

    computer_finish_poi_collide = computer_car.collide(
        FINISH_MASK, *FINISH_POSITION)
    if computer_finish_poi_collide != None:
        game_info.state = GameState.GAME_OVER

    player_finish_poi_collide = player_car.collide(
        FINISH_MASK, *FINISH_POSITION)
    if player_finish_poi_collide != None:
        if player_finish_poi_collide[1] == 0:
            player_car.bounce()
        else:
            game_info.add_to_total_time()
            game_info.next_level()
            player_car.reset()
            computer_car.next_level(game_info.level)

def draw_game_over(win, game_info):
    # Semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((50, 0, 0))
    win.blit(overlay, (0, 0))
    
    # Game Over text
    game_over_text = "GAME OVER"
    game_over_surface = TITLE_FONT.render(game_over_text, True, RED)
    win.blit(game_over_surface, (WIDTH//2 - game_over_surface.get_width()//2, HEIGHT//2 - 100))
    
    # You Lost text
    lost_text = "The computer beat you!"
    lost_surface = SUBTITLE_FONT.render(lost_text, True, WHITE)
    win.blit(lost_surface, (WIDTH//2 - lost_surface.get_width()//2, HEIGHT//2 - 20))
    
    # Restart instruction
    restart_text = "Press R to restart or ESC to return to menu"
    restart_surface = MENU_FONT.render(restart_text, True, YELLOW)
    win.blit(restart_surface, (WIDTH//2 - restart_surface.get_width()//2, HEIGHT//2 + 40))
    
    pygame.display.update()

def draw_victory(win, game_info):
    # Semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 50, 0))
    win.blit(overlay, (0, 0))
    
    # Victory text
    victory_text = "VICTORY!"
    victory_surface = TITLE_FONT.render(victory_text, True, GREEN)
    win.blit(victory_surface, (WIDTH//2 - victory_surface.get_width()//2, HEIGHT//2 - 120))
    
    # Congratulations
    congrats_text = "You completed all levels!"
    congrats_surface = SUBTITLE_FONT.render(congrats_text, True, WHITE)
    win.blit(congrats_surface, (WIDTH//2 - congrats_surface.get_width()//2, HEIGHT//2 - 60))
    
    # Final time
    time_text = f"Total Time: {game_info.total_time}s"
    time_surface = MENU_FONT.render(time_text, True, YELLOW)
    win.blit(time_surface, (WIDTH//2 - time_surface.get_width()//2, HEIGHT//2 - 10))
    
    # Restart instruction
    restart_text = "Press R to play again or ESC to return to menu"
    restart_surface = MENU_FONT.render(restart_text, True, YELLOW)
    win.blit(restart_surface, (WIDTH//2 - restart_surface.get_width()//2, HEIGHT//2 + 40))
    
    pygame.display.update()

# Main game loop
run = True
clock = pygame.time.Clock()
images = [(GRASS, (0, 0)), (TRACK, (0, 0)),
          (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]
player_car = PlayerCar(4, 4)
computer_car = ComputerCar(2, 4, PATH)
game_info = GameInfo()

while run:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break
        
        if event.type == pygame.KEYDOWN:
            if game_info.state == GameState.HOME_SCREEN:
                if event.key == pygame.K_SPACE:
                    game_info.state = GameState.LEVEL_START
            elif game_info.state == GameState.LEVEL_START:
                game_info.start_level()
            elif game_info.state == GameState.GAME_OVER or game_info.state == GameState.VICTORY:
                if event.key == pygame.K_r:
                    game_info.reset()
                    player_car.reset()
                    computer_car.reset()
                elif event.key == pygame.K_ESCAPE:
                    game_info.reset()
                    player_car.reset()
                    computer_car.reset()
    
    # Handle different game states
    if game_info.state == GameState.HOME_SCREEN:
        draw_home_screen(WIN, game_info)
    elif game_info.state == GameState.LEVEL_START:
        draw_game(WIN, images, player_car, computer_car, game_info)
        draw_level_start_screen(WIN, game_info)
    elif game_info.state == GameState.PLAYING:
        draw_game(WIN, images, player_car, computer_car, game_info)
        move_player(player_car)
        computer_car.move()
        handle_collision(player_car, computer_car, game_info)
        
        if game_info.game_finished():
            game_info.add_to_total_time()
            game_info.state = GameState.VICTORY
    elif game_info.state == GameState.GAME_OVER:
        draw_game_over(WIN, game_info)
    elif game_info.state == GameState.VICTORY:
        draw_victory(WIN, game_info)

pygame.quit()