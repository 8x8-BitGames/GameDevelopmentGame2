import pygame
import sys

from pygame.examples.moveit import WIDTH

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BROWN = (160, 82, 45)
GREEN = (0, 200, 100)
PURPLE = (150, 140, 255)

# --- Initialize ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("World's Hardest PyGame")
clock = pygame.time.Clock()
pygame.font.init()

# font for text
my_font = pygame.font.SysFont('Comic Sans MS', 30)
#image for the obstacles.
circle_image = pygame.image.load('circle.png').convert_alpha()
coin_image = pygame.image.load('coin.png').convert_alpha()
class Goal(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, is_final_goal=False):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(topleft=(x, y))

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(PURPLE)
        self.rect = self.image.get_rect(topleft=(x, y))

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = coin_image
        self.rect = self.image.get_rect(topleft=(x,y))
        self.mask = pygame.mask.from_surface(self.image)

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, vx=0, vy=0):
        super().__init__()
        self.vx = vx
        self.vy = vy
        self.image = circle_image #pygame.Surface((20, 20))
        self.rect = self.image.get_rect(topleft=(x,y))
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        if self.rect.x < 0 or self.rect.x > SCREEN_WIDTH-self.rect.w:
            self.vx *= -1
        hit = pygame.sprite.spritecollideany(self, walls)
        if hit:
            if self.vx != 0:  # moving sideways
                self.vx *= -1
                self.rect.x += self.vx  # push out so it doesn’t stick
            if self.vy != 0:  # moving vertically
                self.vy *= -1
                self.rect.y += self.vy

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

    def move(self, dx, dy):
        self.rect.x += dx
        while pygame.sprite.spritecollideany(self, walls):
            self.rect.x -= dx/abs(dx)
        self.rect.y += dy
        while pygame.sprite.spritecollideany(self, walls):
            self.rect.y -= dy/abs(dy)

# group set up.
obstacles = pygame.sprite.Group()
player_group = pygame.sprite.Group()
walls = pygame.sprite.Group()
goals = pygame.sprite.Group()
coins = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

tile_size = 40

player = Player(0, 0)
player_group.add(player)
player_speed = 2
spawn_pos = (0, 0)

# Level setup as dictionary.
LEVELS = [
    {
        'spawn': (160, 320),
        'walls': [
            (0, 0, 800, 160),
            (0, 480, 800, 120),
            (0, 0, 120, 600),
            (700, 0, 120, 600),
            (240, 160, 40, 280),
            (400, 480, 280, 40),
            (280, 160, 240, 40),
            (560, 240, 40, 280),
            (320, 440, 240, 40),
            (280, 200, 240, 40),
            (120, 160, 120, 40),
            (520, 160, 160, 40),
            (640, 160, 80, 40)
        ],
        'obstacles': [
            (410, 250, -3, 0),
            (410, 290, 3, 0),
            (410, 330, -3, 0),
            (410, 370, 3, 0),
            (410, 410, -3, 0),
        ],
        "goals": [
            (600, 160, 120, 320)
        ],
        "coins": {

        }
    }, # level 1 (index 0)

    {
        'spawn': (125, 285),
        'walls': [
            (0, 0, 800, 160),
            (0, 440, 800, 160),
            (0, 160, 200, 80),
            (0, 360, 200, 80),
            (0, 240, 80, 120),
            (160, 320, 40, 40),
            (160, 240, 40, 40),
            (600, 160, 40, 120),
            (600, 320, 40, 160),
            (640, 160, 160, 80),
            (720, 240, 80, 200),
            (640, 360, 80, 80)
        ],
        'obstacles':[
            (x, 290, 0, 3 * (1 if (x-10)%80==0 else -1)) for x in range(210, 610, 40)
        ]
        ,
        "goals": [
            (640, 240, 80, 120)
        ],
        "coins":{
            (364, 284), (384, 284), (404, 284), (424, 284),
            (364, 304), (384, 304), (404, 304), (424, 304)
            # (364, 324), (384, 324), (404, 324), (424, 324),
            # (364, 344), (384, 344), (404, 344), (424, 344)
        }
    }  # level 2 (index 1)
]

def load_level(index):
    global player, spawn_pos, all_sprites, walls, obstacles, goals, player_group

    # reset groups
    walls.empty()
    obstacles.empty()
    goals.empty()
    all_sprites.empty()
    player_group.empty()
    coins.empty()

    level = LEVELS[index]

    # player
    spawn_pos = level["spawn"]
    player = Player(spawn_pos[0], spawn_pos[1])
    player_group.add(player)

    # walls
    for x, y, w, h in level["walls"]:
        wall = Wall(x, y, w, h)
        walls.add(wall)

    # obstacles
    for x, y, vx, vy in level["obstacles"]:
        obs = Obstacle(x, y, vx, vy)
        obstacles.add(obs)

    # goals
    for x, y, w, h in level["goals"]:
        goal = Goal(x, y, w, h)
        goals.add(goal)

    # coins
    for x, y in level['coins']:
        coins.add(Coin(x, y))

    # combine
    all_sprites.add(walls, coins, obstacles, goals, player_group)

current_level = 1
load_level(current_level)
saved_pos = None  # for level design mouse tool

# --- Game Loop ---
running = True
while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            saved_pos = [0, 0]
            saved_pos[0] = tile_size * round(event.pos[0] / tile_size)
            saved_pos[1] = tile_size * round(event.pos[1] / tile_size)
        if event.type == pygame.MOUSEBUTTONUP:
            end_pos = [0, 0]
            end_pos[0] = tile_size * round(event.pos[0] / tile_size)
            end_pos[1] = tile_size * round(event.pos[1] / tile_size)
            w = abs(saved_pos[0] - end_pos[0])
            h = abs(end_pos[1] - saved_pos[1])
            print(f'({saved_pos[0]}, {saved_pos[1]}, {w}, {h}),')

    # --- Input ---
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.move(-player_speed, 0)
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.move(player_speed, 0)
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player.move(0, -player_speed)
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player.move(0, player_speed)

    # --- Update Game State ---
    obstacles.update()
    if pygame.sprite.groupcollide(player_group, obstacles, False, False):
        load_level(current_level)
    pygame.sprite.groupcollide(player_group, coins, False, True)

    for goal in goals:
        if goal.rect.contains(player.rect):
            if len(coins) == 0:
                current_level += 1
                load_level(current_level)
            else:
                pass
            current_level += 1
            load_level(current_level)


    # --- Drawing ---
    screen.fill((128, 128, 128))  # clear screen
    for x in range(0, SCREEN_WIDTH, tile_size):
        for y in range(0, SCREEN_WIDTH, tile_size):
            if (x + y) % (tile_size*2) == 0:
                pygame.draw.rect(screen, WHITE, pygame.rect.Rect(x, y, tile_size, tile_size))
            else:
                pygame.draw.rect(screen, (220, 220, 220), pygame.rect.Rect(x, y, tile_size, tile_size))
    all_sprites.draw(screen)

    # TODO: Level display, fail count
    # text_surface = my_font.render('Some Text', False, (0, 0, 0))
    # screen.blit(text_surface, (0, 0))

    pygame.display.flip()  # update display

    # --- Frame Rate ---
    clock.tick(FPS)

# --- Quit ---
pygame.quit()
sys.exit()