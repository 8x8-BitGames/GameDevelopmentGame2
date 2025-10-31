import pygame
import random
import math

pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
SUNSET_SKY = (255, 140, 100)  # Warm sunset color
GROUND_COLOR = (100, 200, 100)
PLAYER_COLOR = (50, 150, 255)
ENEMY_COLOR = (255, 50, 50)
COIN_COLOR = (255, 215, 0)
CART_COLOR = (240, 240, 240)
POWERUP_COLOR = (255, 100, 255)
DASH_COLOR = (255, 165, 0)

# Physics
GRAVITY = 0.8
JUMP_FORCE = -15
GROUND_Y = HEIGHT - 100
SCROLL_SPEED = 6

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Infinite Runner")
clock = pygame.time.Clock()


class Player:
    def __init__(self):
        self.x = 150
        self.y = GROUND_Y - 50
        self.width = 40
        self.height = 50
        self.vel_y = 0
        self.jumping = False
        self.on_ground = True
        self.jumps_left = 2
        self.max_jumps = 2

        # Squash and stretch
        self.squash = 1.0
        self.stretch = 1.0
        self.target_squash = 1.0
        self.target_stretch = 1.0

        # Animation
        self.rotation = 0
        self.bounce_offset = 0

        # Double jump effect
        self.double_jump_particles = []

        # Score
        self.score = 0

        # Triple jump powerup
        self.triple_jump_active = False
        self.triple_jump_duration = 0
        self.triple_jump_max_duration = 300  # 5 seconds at 60 FPS
        self.normal_max_jumps = 2
        self.powerup_max_jumps = 3

        # Dash powerup
        self.dash_active = False
        self.dash_duration = 0
        self.dash_max_duration = 300  # 5 seconds at 60 FPS
        self.dash_cooldown = 0
        self.dash_cooldown_max = 45  # 0.75 seconds at 60 FPS
        self.is_dashing = False
        self.dash_time = 0
        self.dash_time_max = 30  # 0.5 seconds dash (doubled from 15)
        self.dash_speed_boost = 8  # Extra forward movement during dash

        # Powerup activation particles
        self.powerup_particles = []
        self.dash_trail = []

    def jump(self):
        if self.jumps_left > 0:
            self.vel_y = JUMP_FORCE
            self.jumping = True
            self.on_ground = False
            self.jumps_left -= 1

            # Different animation for triple jump
            if self.triple_jump_active and self.jumps_left == 0:  # Triple jump (third jump)
                self.target_stretch = 1.7
                self.target_squash = 0.4
                # Create extra fancy particles for triple jump
                for i in range(12):
                    angle = (i / 12) * math.pi * 2
                    self.double_jump_particles.append({
                        'x': self.x + self.width / 2,
                        'y': self.y + self.height / 2,
                        'angle': angle,
                        'distance': 0,
                        'life': 25,
                        'speed': 4,
                        'color': POWERUP_COLOR
                    })
            elif self.jumps_left == 0 or (
                    self.triple_jump_active and self.jumps_left == 1):  # Double jump (second jump)
                self.target_stretch = 1.5
                self.target_squash = 0.5
                # Create spin effect particles - always blue for double jump
                for i in range(8):
                    angle = (i / 8) * math.pi * 2
                    self.double_jump_particles.append({
                        'x': self.x + self.width / 2,
                        'y': self.y + self.height / 2,
                        'angle': angle,
                        'distance': 0,
                        'life': 20,
                        'speed': 3,
                        'color': PLAYER_COLOR  # Always blue for double jump
                    })
            else:  # First jump
                self.target_stretch = 1.3
                self.target_squash = 0.7

    def activate_powerup(self):
        self.triple_jump_active = True
        self.triple_jump_duration = self.triple_jump_max_duration
        self.max_jumps = self.powerup_max_jumps
        if self.on_ground:
            self.jumps_left = self.powerup_max_jumps

        # Explosion of particles
        for i in range(20):
            angle = (i / 20) * math.pi * 2
            self.powerup_particles.append({
                'x': self.x + self.width / 2,
                'y': self.y + self.height / 2,
                'angle': angle,
                'distance': 0,
                'life': 30,
                'speed': random.uniform(3, 6),
                'size': random.randint(4, 8),
                'color': POWERUP_COLOR
            })

    def activate_dash(self):
        self.dash_active = True
        self.dash_duration = self.dash_max_duration

        # Explosion of dash particles
        for i in range(20):
            angle = (i / 20) * math.pi * 2
            self.powerup_particles.append({
                'x': self.x + self.width / 2,
                'y': self.y + self.height / 2,
                'angle': angle,
                'distance': 0,
                'life': 30,
                'speed': random.uniform(3, 6),
                'size': random.randint(4, 8),
                'color': DASH_COLOR
            })

    def start_dash(self):
        if self.dash_active and not self.is_dashing and self.dash_cooldown == 0:
            self.is_dashing = True
            self.dash_time = self.dash_time_max
            self.dash_cooldown = self.dash_cooldown_max

    def update(self):
        # Apply gravity
        self.vel_y += GRAVITY
        self.y += self.vel_y

        # Update triple jump powerup
        if self.triple_jump_active:
            self.triple_jump_duration -= 1
            if self.triple_jump_duration <= 0:
                self.triple_jump_active = False
                self.max_jumps = self.normal_max_jumps
                if self.on_ground:
                    self.jumps_left = min(self.jumps_left, self.normal_max_jumps)

        # Update dash powerup
        if self.dash_active:
            self.dash_duration -= 1
            if self.dash_duration <= 0:
                self.dash_active = False
                self.is_dashing = False

        # Update dash state
        if self.is_dashing:
            self.dash_time -= 1
            if self.dash_time <= 0:
                self.is_dashing = False
            # Boost forward during dash
            self.x += self.dash_speed_boost
            # Create enhanced dash trail with streaks
            if random.random() < 0.8:  # More frequent trails
                self.dash_trail.append({
                    'x': self.x + self.width / 2,
                    'y': self.y + self.height / 2,
                    'life': 30,  # Longer lasting
                    'size': random.randint(10, 20),
                    'vx': random.uniform(-3, -1),  # Streak backward
                    'vy': random.uniform(-2, 2)
                })

        # Update dash cooldown
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1

        # Check ground collision
        if self.y >= GROUND_Y - self.height:
            self.y = GROUND_Y - self.height
            self.vel_y = 0
            self.on_ground = True
            self.jumping = False
            self.jumps_left = self.max_jumps  # Reset jumps
            # Squash on landing
            if self.target_stretch < 1.0:
                self.target_squash = 1.3
                self.target_stretch = 0.7
        else:
            self.on_ground = False

        # Smooth squash and stretch
        self.squash += (self.target_squash - self.squash) * 0.2
        self.stretch += (self.target_stretch - self.stretch) * 0.2

        # Return to normal
        if abs(self.squash - 1.0) < 0.05:
            self.target_squash = 1.0
        if abs(self.stretch - 1.0) < 0.05:
            self.target_stretch = 1.0

        # Bounce animation when running
        if self.on_ground:
            self.bounce_offset = math.sin(pygame.time.get_ticks() * 0.02) * 3

        # Rotation in air - extra spin for double jump
        if not self.on_ground:
            if (self.triple_jump_active and self.jumps_left == 0) or (
                    not self.triple_jump_active and self.jumps_left == 0):  # Used double/triple jump
                self.rotation = (pygame.time.get_ticks() * 0.5) % 360
            else:
                self.rotation = min(self.vel_y * 2, 45)
        else:
            self.rotation = 0

        # Update double jump particles
        for p in self.double_jump_particles[:]:
            p['distance'] += p['speed']
            p['life'] -= 1
            if p['life'] <= 0:
                self.double_jump_particles.remove(p)

        # Update powerup particles
        for p in self.powerup_particles[:]:
            p['distance'] += p['speed']
            p['life'] -= 1
            if p['life'] <= 0:
                self.powerup_particles.remove(p)

        # Update dash trail
        for t in self.dash_trail[:]:
            t['life'] -= 1
            t['x'] += t.get('vx', 0)
            t['y'] += t.get('vy', 0)
            if t['life'] <= 0:
                self.dash_trail.remove(t)

    def draw(self, screen):
        # Draw dash trail with streaks
        for t in self.dash_trail:
            alpha = t['life'] / 30
            size = int(t['size'] * alpha)
            if size > 0:
                # Draw streak effect with gradient
                for i in range(3):
                    streak_size = size - i * 2
                    if streak_size > 0:
                        color_alpha = int(255 * alpha * (1 - i * 0.3))
                        color = (255, 165, 0) if color_alpha > 128 else (255, 200, 100)
                        pygame.draw.circle(screen, color, (int(t['x'] + i * 5), int(t['y'])), streak_size)

        # Draw powerup particles
        for p in self.powerup_particles:
            x = self.x + self.width / 2 + math.cos(p['angle']) * p['distance']
            y = self.y + self.height / 2 + math.sin(p['angle']) * p['distance']
            alpha = p['life'] / 30
            size = int(p['size'] * alpha)
            if size > 0:
                color = p.get('color', POWERUP_COLOR)
                pygame.draw.circle(screen, color, (int(x), int(y)), size)

        # Draw double jump particles
        for p in self.double_jump_particles:
            x = self.x + self.width / 2 + math.cos(p['angle']) * p['distance']
            y = self.y + self.height / 2 + math.sin(p['angle']) * p['distance']
            alpha = p['life'] / 25 if 'color' in p and p['color'] == POWERUP_COLOR else p['life'] / 20
            size = int(8 * alpha)
            if size > 0:
                color = p.get('color', PLAYER_COLOR)
                pygame.draw.circle(screen, color, (int(x), int(y)), size)

        # Calculate squashed dimensions
        draw_width = self.width * self.squash
        draw_height = self.height * self.stretch

        # Center position
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2 + self.bounce_offset

        # Create surface for rotation
        surf = pygame.Surface((draw_width * 2, draw_height * 2), pygame.SRCALPHA)

        # Draw body with dash glow effect
        body_rect = pygame.Rect(draw_width / 2, draw_height / 2, draw_width, draw_height)

        # Glow when dashing
        if self.is_dashing:
            for i in range(3):
                glow_rect = body_rect.inflate(10 - i * 3, 10 - i * 3)
                glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (*DASH_COLOR, 100),
                                 pygame.Rect(0, 0, glow_rect.width, glow_rect.height), border_radius=10)
                surf.blit(glow_surface, (glow_rect.x, glow_rect.y))

        pygame.draw.rect(surf, PLAYER_COLOR, body_rect, border_radius=10)

        # Draw eyes
        eye_y = draw_height * 0.4
        pygame.draw.circle(surf, WHITE, (int(draw_width * 0.7), int(eye_y)), int(draw_width * 0.15))
        pygame.draw.circle(surf, WHITE, (int(draw_width * 1.3), int(eye_y)), int(draw_width * 0.15))
        pygame.draw.circle(surf, BLACK, (int(draw_width * 0.7), int(eye_y)), int(draw_width * 0.08))
        pygame.draw.circle(surf, BLACK, (int(draw_width * 1.3), int(eye_y)), int(draw_width * 0.08))

        # Rotate
        rotated = pygame.transform.rotate(surf, -self.rotation)
        rect = rotated.get_rect(center=(center_x, center_y))
        screen.blit(rotated, rect)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Enemy:
    def __init__(self, x):
        self.x = x
        self.y = GROUND_Y - 40
        self.width = 55
        self.height = 40
        self.alive = True

        # Squash and stretch
        self.squash = 1.0
        self.stretch = 1.0
        self.death_timer = 0

        # Animation
        self.wobble = random.uniform(0, math.pi * 2)

    def update(self):
        self.x -= SCROLL_SPEED
        self.wobble += 0.1

        # Death animation
        if not self.alive:
            self.death_timer += 1
            self.stretch = max(0, 1.0 - self.death_timer * 0.1)
            self.squash = 1.0 + self.death_timer * 0.1

    def draw(self, screen):
        if self.stretch <= 0:
            return

        # Calculate dimensions with wobble
        wobble_offset = math.sin(self.wobble) * 3
        draw_width = self.width * self.squash
        draw_height = self.height * self.stretch

        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2 + wobble_offset

        # Body
        rect = pygame.Rect(center_x - draw_width / 2, center_y - draw_height / 2,
                           draw_width, draw_height)
        pygame.draw.rect(screen, ENEMY_COLOR, rect, border_radius=8)

        # Eyes (angry)
        if self.alive:
            eye_y = center_y - draw_height * 0.2
            eye_size = int(draw_width * 0.12)
            pygame.draw.circle(screen, WHITE, (int(center_x - draw_width * 0.25), int(eye_y)), eye_size)
            pygame.draw.circle(screen, WHITE, (int(center_x + draw_width * 0.25), int(eye_y)), eye_size)
            pygame.draw.circle(screen, BLACK, (int(center_x - draw_width * 0.25), int(eye_y)), eye_size // 2)
            pygame.draw.circle(screen, BLACK, (int(center_x + draw_width * 0.25), int(eye_y)), eye_size // 2)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class GolfCart:
    def __init__(self):
        self.width = 120
        self.height = 80
        self.x = -self.width - 50
        self.y = GROUND_Y - self.height
        self.target_x = -100

        # Animation
        self.wheel_rotation = 0
        self.shake_offset = 0
        self.engine_rumble = 0

    def update(self, player_x):
        # Follow player, staying slightly behind
        # Slower catch-up speed when far away
        distance_to_target = (player_x - 150) - self.x
        catch_up_speed = 0.02 if abs(distance_to_target) > 200 else 0.05

        self.target_x = player_x - 150
        self.x += (self.target_x - self.x) * catch_up_speed

        # Animations
        self.wheel_rotation += SCROLL_SPEED * 2
        self.shake_offset = math.sin(pygame.time.get_ticks() * 0.1) * 1.5
        self.engine_rumble = random.uniform(-1, 1)

    def draw(self, screen):
        draw_x = self.x + self.shake_offset + self.engine_rumble
        draw_y = self.y

        # Cart body
        body_rect = pygame.Rect(draw_x, draw_y + 20, self.width, self.height - 30)
        pygame.draw.rect(screen, CART_COLOR, body_rect, border_radius=8)

        # Cart top/roof
        roof_rect = pygame.Rect(draw_x + 10, draw_y, self.width - 20, 30)
        pygame.draw.rect(screen, (220, 220, 220), roof_rect, border_radius=6)

        # Windshield
        windshield = pygame.Rect(draw_x + 15, draw_y + 5, 35, 20)
        pygame.draw.rect(screen, (150, 200, 255), windshield, border_radius=4)

        # Front grill
        grill_rect = pygame.Rect(draw_x + self.width - 15, draw_y + 30, 10, 25)
        pygame.draw.rect(screen, (40, 40, 40), grill_rect, border_radius=2)

        # Headlights
        pygame.draw.circle(screen, (255, 50, 50), (int(draw_x + self.width - 10), int(draw_y + 35)), 6)
        pygame.draw.circle(screen, (255, 100, 100), (int(draw_x + self.width - 10), int(draw_y + 35)), 4)

        # Wheels
        wheel_y = draw_y + self.height - 10

        # Back wheel
        pygame.draw.circle(screen, BLACK, (int(draw_x + 25), int(wheel_y)), 15)
        pygame.draw.circle(screen, (200, 200, 200), (int(draw_x + 25), int(wheel_y)), 12)
        for i in range(4):
            angle = math.radians(self.wheel_rotation + i * 90)
            x1 = draw_x + 25 + math.cos(angle) * 5
            y1 = wheel_y + math.sin(angle) * 5
            x2 = draw_x + 25 + math.cos(angle) * 10
            y2 = wheel_y + math.sin(angle) * 10
            pygame.draw.line(screen, (150, 150, 150), (x1, y1), (x2, y2), 2)

        # Front wheel
        pygame.draw.circle(screen, BLACK, (int(draw_x + self.width - 25), int(wheel_y)), 15)
        pygame.draw.circle(screen, (200, 200, 200), (int(draw_x + self.width - 25), int(wheel_y)), 12)
        for i in range(4):
            angle = math.radians(self.wheel_rotation + i * 90)
            x1 = draw_x + self.width - 25 + math.cos(angle) * 5
            y1 = wheel_y + math.sin(angle) * 5
            x2 = draw_x + self.width - 25 + math.cos(angle) * 10
            y2 = wheel_y + math.sin(angle) * 10
            pygame.draw.line(screen, (150, 150, 150), (x1, y1), (x2, y2), 2)

        # Exhaust smoke
        if random.random() < 0.3:
            smoke_x = draw_x - 5
            smoke_y = draw_y + self.height - 20
            pygame.draw.circle(screen, (100, 100, 100), (int(smoke_x), int(smoke_y)), random.randint(3, 6))


class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 20
        self.collected = False
        self.scale = 1.0
        self.rotation = 0

    def update(self):
        self.x -= SCROLL_SPEED
        self.rotation += 5
        self.scale = 1.0 + math.sin(pygame.time.get_ticks() * 0.01) * 0.1

    def draw(self, screen):
        if not self.collected:
            draw_size = int(self.size * self.scale)
            width_factor = abs(math.cos(math.radians(self.rotation)))
            draw_width = int(draw_size * width_factor)

            coin_rect = pygame.Rect(self.x + (self.size - draw_width) // 2,
                                    self.y, draw_width, draw_size)
            pygame.draw.ellipse(screen, COIN_COLOR, coin_rect)
            pygame.draw.ellipse(screen, (200, 160, 0), coin_rect, 2)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)


class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 30
        self.collected = False
        self.float_offset = 0
        self.rotation = 0
        self.pulse = 1.0

    def update(self):
        self.x -= SCROLL_SPEED
        self.float_offset = math.sin(pygame.time.get_ticks() * 0.005) * 10
        self.rotation += 3
        self.pulse = 1.0 + math.sin(pygame.time.get_ticks() * 0.01) * 0.2

    def draw(self, screen):
        if not self.collected:
            draw_x = self.x
            draw_y = self.y + self.float_offset
            draw_size = int(self.size * self.pulse)

            # Outer glow
            for i in range(3):
                glow_size = draw_size + (3 - i) * 5
                pygame.draw.circle(screen, POWERUP_COLOR,
                                   (int(draw_x + self.size // 2), int(draw_y + self.size // 2)),
                                   glow_size // 2)

            # Main star shape (triple jump symbol)
            center_x = draw_x + self.size // 2
            center_y = draw_y + self.size // 2

            # Draw three arrows pointing up
            for i in range(3):
                angle_offset = (i - 1) * 25
                arrow_base_y = center_y + 8
                arrow_tip_y = center_y - 10
                arrow_x = center_x + math.sin(math.radians(angle_offset)) * 8

                pygame.draw.line(screen, WHITE,
                                 (arrow_x, arrow_base_y),
                                 (arrow_x, arrow_tip_y), 3)

                pygame.draw.polygon(screen, WHITE, [
                    (arrow_x, arrow_tip_y),
                    (arrow_x - 4, arrow_tip_y + 6),
                    (arrow_x + 4, arrow_tip_y + 6)
                ])

    def get_rect(self):
        return pygame.Rect(self.x, self.y + self.float_offset, self.size, self.size)


class DashPowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 30
        self.collected = False
        self.float_offset = 0
        self.rotation = 0
        self.pulse = 1.0

    def update(self):
        self.x -= SCROLL_SPEED
        self.float_offset = math.sin(pygame.time.get_ticks() * 0.005) * 10
        self.rotation += 3
        self.pulse = 1.0 + math.sin(pygame.time.get_ticks() * 0.01) * 0.2

    def draw(self, screen):
        if not self.collected:
            draw_x = self.x
            draw_y = self.y + self.float_offset
            draw_size = int(self.size * self.pulse)

            # Outer glow
            for i in range(3):
                glow_size = draw_size + (3 - i) * 5
                pygame.draw.circle(screen, DASH_COLOR,
                                   (int(draw_x + self.size // 2), int(draw_y + self.size // 2)),
                                   glow_size // 2)

            # Main lightning bolt symbol
            center_x = draw_x + self.size // 2
            center_y = draw_y + self.size // 2

            # Draw lightning bolt
            bolt_points = [
                (center_x - 3, center_y - 10),
                (center_x + 2, center_y - 2),
                (center_x - 2, center_y + 2),
                (center_x + 5, center_y + 10),
                (center_x + 1, center_y + 2),
                (center_x + 3, center_y - 2),
            ]
            pygame.draw.polygon(screen, WHITE, bolt_points)

    def get_rect(self):
        return pygame.Rect(self.x, self.y + self.float_offset, self.size, self.size)


class ParticleEffect:
    def __init__(self, x, y, color):
        self.particles = []
        for _ in range(10):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 6)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - 3,
                'life': 30,
                'color': color
            })

    def update(self):
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.3
            p['life'] -= 1

        self.particles = [p for p in self.particles if p['life'] > 0]

    def draw(self, screen):
        for p in self.particles:
            alpha = p['life'] / 30
            size = int(6 * alpha)
            if size > 0:
                pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), size)

    def is_done(self):
        return len(self.particles) == 0


def lerp_color(color1, color2, t):
    """Linear interpolation between two colors"""
    t = max(0, min(1, t))  # Clamp t between 0 and 1
    return (
        int(color1[0] + (color2[0] - color1[0]) * t),
        int(color1[1] + (color2[1] - color1[1]) * t),
        int(color1[2] + (color2[2] - color1[2]) * t)
    )


def draw_gradient_sky(screen, distance):
    """Draw sky with gradient effect"""
    # Start transitioning at 12000, complete by 15000
    transition_start = 12000
    transition_end = 15000

    if distance < transition_start:
        # Clear blue sky
        screen.fill(SKY_BLUE)
    elif distance >= transition_end:
        # Full sunset gradient: pink at top, orange in middle, blue at bottom
        for y in range(HEIGHT):
            progress = y / HEIGHT
            if progress < 0.3:
                # Top third: pink to orange
                local_progress = progress / 0.3
                color = lerp_color((255, 150, 200), (255, 140, 100), local_progress)
            elif progress < 0.6:
                # Middle third: orange to light blue
                local_progress = (progress - 0.3) / 0.3
                color = lerp_color((255, 140, 100), (150, 180, 220), local_progress)
            else:
                # Bottom third: light blue to darker blue
                local_progress = (progress - 0.6) / 0.4
                color = lerp_color((150, 180, 220), (100, 150, 200), local_progress)
            pygame.draw.line(screen, color, (0, y), (WIDTH, y))
    else:
        # Transition from blue to gradient
        transition_progress = (distance - transition_start) / (transition_end - transition_start)

        for y in range(HEIGHT):
            progress = y / HEIGHT
            # Target gradient colors
            if progress < 0.3:
                local_progress = progress / 0.3
                target_color = lerp_color((255, 150, 200), (255, 140, 100), local_progress)
            elif progress < 0.6:
                local_progress = (progress - 0.3) / 0.3
                target_color = lerp_color((255, 140, 100), (150, 180, 220), local_progress)
            else:
                local_progress = (progress - 0.6) / 0.4
                target_color = lerp_color((150, 180, 220), (100, 150, 200), local_progress)

            # Interpolate from SKY_BLUE to target gradient color
            color = lerp_color(SKY_BLUE, target_color, transition_progress)
            pygame.draw.line(screen, color, (0, y), (WIDTH, y))


def draw_sun(screen, distance):
    """Draw sun that sets as distance increases"""
    # Sun is visible from 0 to 15000
    # At 0: sun is high in sky
    # At 15000: sun is at horizon (half visible)

    if distance > 15000:
        return

    # Calculate sun position
    # Start high, end at horizon
    start_y = 100  # High in sky
    end_y = GROUND_Y  # At horizon

    progress = min(distance / 15000, 1.0)
    sun_y = start_y + (end_y - start_y) * progress
    sun_x = WIDTH - 150  # Fixed x position on right side
    sun_radius = 50

    # Draw sun glow
    for i in range(5):
        glow_radius = sun_radius + (5 - i) * 10
        alpha = 50 - i * 10
        glow_color = (255, 220, 100)
        pygame.draw.circle(screen, glow_color, (int(sun_x), int(sun_y)), glow_radius)

    # Draw main sun
    pygame.draw.circle(screen, (255, 230, 100), (int(sun_x), int(sun_y)), sun_radius)
    pygame.draw.circle(screen, (255, 200, 50), (int(sun_x), int(sun_y)), sun_radius - 5)

    # If sun is at/below horizon, clip it
    if sun_y >= GROUND_Y - sun_radius:
        # Create a surface to clip the sun
        clip_rect = pygame.Rect(0, 0, WIDTH, GROUND_Y)
        screen.set_clip(clip_rect)
        # Sun already drawn above, just need to re-establish clipping
        screen.set_clip(None)


def draw_boston_skyline(screen, scroll_offset, distance):
    """Draw a simplified Boston skyline in the background"""
    # Buildings start appearing from the right at distance 15000
    # Slide in over 2000 distance units (15000-17000)
    skyline_start = 15000
    skyline_fully_visible = 17000

    # Don't draw anything before buildings start appearing
    if distance < skyline_start:
        return

    # Calculate slide-in progress
    if distance < skyline_fully_visible:
        slide_progress = (distance - skyline_start) / (skyline_fully_visible - skyline_start)
        # Buildings slide in from completely off the right side of the screen
        # We need to account for the full width of the skyline (about 800px)
        base_slide_offset = WIDTH + 800 - (WIDTH + 800) * slide_progress
    else:
        # Fully visible, now they scroll with parallax
        slide_progress = 1.0
        base_slide_offset = 0

    skyline_y = GROUND_Y

    # Buildings move slower than foreground (parallax effect)
    # Only apply parallax after buildings are fully visible
    if distance >= skyline_fully_visible:
        parallax_offset = (scroll_offset * 0.3) % WIDTH
    else:
        parallax_offset = 0

    # Define Boston-inspired buildings
    buildings = [
        # Hancock Tower (tallest)
        {'x': 100, 'w': 60, 'h': 200, 'color': (70, 90, 120), 'windows': True},
        # Prudential Tower
        {'x': 180, 'w': 50, 'h': 180, 'color': (80, 100, 130), 'windows': True},
        # Small building
        {'x': 240, 'w': 35, 'h': 100, 'color': (90, 110, 140), 'windows': True},
        # Custom House Tower (with spire)
        {'x': 290, 'w': 40, 'h': 140, 'color': (75, 95, 125), 'windows': True, 'spire': True},
        # Medium building
        {'x': 340, 'w': 45, 'h': 120, 'color': (85, 105, 135), 'windows': True},
        # State Street building
        {'x': 395, 'w': 55, 'h': 160, 'color': (65, 85, 115), 'windows': True},
        # Small building
        {'x': 460, 'w': 30, 'h': 90, 'color': (95, 115, 145), 'windows': True},
        # Federal Reserve
        {'x': 500, 'w': 50, 'h': 130, 'color': (70, 90, 120), 'windows': True},
        # Wide building
        {'x': 560, 'w': 65, 'h': 110, 'color': (80, 100, 130), 'windows': True},
        # Tall narrow
        {'x': 635, 'w': 35, 'h': 170, 'color': (75, 95, 125), 'windows': True},
        # Medium
        {'x': 680, 'w': 40, 'h': 125, 'color': (85, 105, 135), 'windows': True},
        # Short wide
        {'x': 730, 'w': 50, 'h': 95, 'color': (90, 110, 140), 'windows': True},
    ]

    # Draw buildings with slide-in effect from the right
    for offset in [-WIDTH, 0, WIDTH]:
        for building in buildings:
            # Apply parallax scrolling and slide-in offset
            x = building['x'] - parallax_offset + offset + base_slide_offset

            # Only draw if visible on screen
            if x < -building['w'] or x > WIDTH + building['w']:
                continue

            y = skyline_y - building['h']

            # Draw building body
            pygame.draw.rect(screen, building['color'],
                             (x, y, building['w'], building['h']))

            # Draw darker outline
            pygame.draw.rect(screen, (50, 60, 80),
                             (x, y, building['w'], building['h']), 2)

            # Draw windows if specified
            if building.get('windows'):
                window_color = (200, 220, 255, 100)
                window_w = 4
                window_h = 6
                spacing_x = 8
                spacing_y = 10

                for wy in range(int(y + 10), int(y + building['h'] - 5), spacing_y):
                    for wx in range(int(x + 6), int(x + building['w'] - 6), spacing_x):
                        # Random lit windows
                        if random.random() > 0.3:
                            pygame.draw.rect(screen, window_color,
                                             (wx, wy, window_w, window_h))

            # Draw spire for Custom House Tower
            if building.get('spire'):
                spire_w = 12
                spire_h = 30
                spire_x = x + building['w'] // 2 - spire_w // 2
                spire_y = y - spire_h
                pygame.draw.polygon(screen, (100, 120, 150), [
                    (spire_x + spire_w // 2, spire_y),
                    (spire_x, spire_y + spire_h),
                    (spire_x + spire_w, spire_y + spire_h)
                ])

def main():
    player = Player()
    golf_cart = GolfCart()
    enemies = []
    coins = []
    powerups = []
    dash_powerups = []
    particles = []

    spawn_timer = 0
    coin_timer = 0
    powerup_timer = 0
    dash_powerup_timer = 0
    distance = 0
    camera_offset = 0  # Track camera position for dash

    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)

    running = True
    game_over = False

    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    player.jump()
                if event.key == pygame.K_d and not game_over:
                    player.start_dash()
                if event.key == pygame.K_r and game_over:
                    player = Player()
                    golf_cart = GolfCart()
                    enemies = []
                    coins = []
                    powerups = []
                    dash_powerups = []
                    particles = []
                    spawn_timer = 0
                    coin_timer = 0
                    powerup_timer = 0
                    dash_powerup_timer = 0
                    distance = 0
                    camera_offset = 0
                    game_over = False

        if not game_over:
            # Store previous player x position
            prev_player_x = player.x

            player.update()
            distance += SCROLL_SPEED

            # If player moved forward from dash, adjust camera and world
            if player.is_dashing:
                dash_movement = player.x - prev_player_x - player.dash_speed_boost
                camera_offset += dash_movement

                # Move player back to normal position but shift everything else
                player.x = prev_player_x

                # Shift all world objects backward to create illusion of forward movement
                for enemy in enemies:
                    enemy.x -= player.dash_speed_boost
                for coin in coins:
                    coin.x -= player.dash_speed_boost
                for powerup in powerups:
                    powerup.x -= player.dash_speed_boost
                for dash_powerup in dash_powerups:
                    dash_powerup.x -= player.dash_speed_boost

            golf_cart.update(player.x)

            spawn_timer += 1
            if spawn_timer > random.randint(60, 120):
                enemies.append(Enemy(WIDTH + 50))
                spawn_timer = 0

            coin_timer += 1
            if coin_timer > random.randint(40, 80):
                coin_y = random.choice([GROUND_Y - 80, GROUND_Y - 150, GROUND_Y - 220])
                coins.append(Coin(WIDTH + 50, coin_y))
                coin_timer = 0

            powerup_timer += 1
            if powerup_timer > random.randint(300, 500):
                powerup_y = random.choice([GROUND_Y - 100, GROUND_Y - 180])
                powerups.append(PowerUp(WIDTH + 50, powerup_y))
                powerup_timer = 0

            dash_powerup_timer += 1
            if dash_powerup_timer > random.randint(350, 550):
                dash_powerup_y = random.choice([GROUND_Y - 100, GROUND_Y - 180])
                dash_powerups.append(DashPowerUp(WIDTH + 50, dash_powerup_y))
                dash_powerup_timer = 0

            for enemy in enemies[:]:
                enemy.update()
                if enemy.x < -100:
                    enemies.remove(enemy)

                if enemy.alive and player.get_rect().colliderect(enemy.get_rect()):
                    # If dashing, phase through enemy
                    if player.is_dashing:
                        continue
                    # If jumping on enemy
                    if player.vel_y > 0 and player.y < enemy.y - 10:
                        enemy.alive = False
                        player.vel_y = JUMP_FORCE * 0.7
                        player.score += 100
                        particles.append(ParticleEffect(enemy.x + 20, enemy.y + 20, ENEMY_COLOR))
                        player.target_squash = 1.4
                        player.target_stretch = 0.6
                    else:
                        game_over = True

            for coin in coins[:]:
                coin.update()
                if coin.x < -50:
                    coins.remove(coin)

                if not coin.collected and player.get_rect().colliderect(coin.get_rect()):
                    coin.collected = True
                    player.score += 10
                    particles.append(ParticleEffect(coin.x, coin.y, COIN_COLOR))
                    coins.remove(coin)

            for powerup in powerups[:]:
                powerup.update()
                if powerup.x < -50:
                    powerups.remove(powerup)

                if not powerup.collected and player.get_rect().colliderect(powerup.get_rect()):
                    powerup.collected = True
                    player.activate_powerup()
                    player.score += 50
                    particles.append(ParticleEffect(powerup.x, powerup.y, POWERUP_COLOR))
                    powerups.remove(powerup)

            for dash_powerup in dash_powerups[:]:
                dash_powerup.update()
                if dash_powerup.x < -50:
                    dash_powerups.remove(dash_powerup)

                if not dash_powerup.collected and player.get_rect().colliderect(dash_powerup.get_rect()):
                    dash_powerup.collected = True
                    player.activate_dash()
                    player.score += 50
                    particles.append(ParticleEffect(dash_powerup.x, dash_powerup.y, DASH_COLOR))
                    dash_powerups.remove(dash_powerup)

            for particle in particles[:]:
                particle.update()
                if particle.is_done():
                    particles.remove(particle)

        # Draw
        # Draw gradient sky based on distance
        draw_gradient_sky(screen, distance)

        # Draw sun (before buildings)
        draw_sun(screen, distance)

        # Draw Boston skyline with slide-in effect
        draw_boston_skyline(screen, distance, distance)

        pygame.draw.rect(screen, GROUND_COLOR, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
        pygame.draw.line(screen, (80, 160, 80), (0, GROUND_Y), (WIDTH, GROUND_Y), 3)

        golf_cart.draw(screen)

        for coin in coins:
            coin.draw(screen)

        for powerup in powerups:
            powerup.draw(screen)

        for dash_powerup in dash_powerups:
            dash_powerup.draw(screen)

        for enemy in enemies:
            enemy.draw(screen)

        for particle in particles:
            particle.draw(screen)

        player.draw(screen)

        # UI
        score_text = font.render(f'Score: {player.score}', True, BLACK)
        screen.blit(score_text, (10, 10))

        distance_text = font.render(f'Distance: {distance // 10}m', True, BLACK)
        screen.blit(distance_text, (10, 50))

        jumps_text = small_font.render(f'Jumps: {"O " * player.jumps_left}', True, PLAYER_COLOR)
        screen.blit(jumps_text, (10, 90))

        # Powerup timers display
        timer_y = 40
        timer_spacing = 80

        # Triple jump pie timer
        if player.triple_jump_active:
            pie_x = WIDTH - 80
            pie_y = timer_y
            pie_radius = 30

            pygame.draw.circle(screen, (50, 50, 50), (pie_x, pie_y), pie_radius + 3)
            pygame.draw.circle(screen, (20, 20, 20), (pie_x, pie_y), pie_radius)

            completion = player.triple_jump_duration / player.triple_jump_max_duration
            end_angle = -90 + (360 * (1 - completion))

            if completion > 0:
                points = [(pie_x, pie_y)]
                for angle in range(-90, int(end_angle) + 1, 5):
                    rad = math.radians(angle)
                    x = pie_x + math.cos(rad) * pie_radius
                    y = pie_y + math.sin(rad) * pie_radius
                    points.append((x, y))
                points.append((pie_x, pie_y))

                if len(points) > 2:
                    pygame.draw.polygon(screen, POWERUP_COLOR, points)

            pulse = 1.0 + math.sin(pygame.time.get_ticks() * 0.02) * 0.1
            ring_radius = int(pie_radius * pulse)
            pygame.draw.circle(screen, POWERUP_COLOR, (pie_x, pie_y), ring_radius, 3)

            # Triple jump icon in center
            for i in range(3):
                angle_offset = (i - 1) * 15
                arrow_x = pie_x + math.sin(math.radians(angle_offset)) * 5
                arrow_base_y = pie_y + 6
                arrow_tip_y = pie_y - 8

                pygame.draw.line(screen, WHITE, (arrow_x, arrow_base_y), (arrow_x, arrow_tip_y), 2)
                pygame.draw.polygon(screen, WHITE, [
                    (arrow_x, arrow_tip_y),
                    (arrow_x - 3, arrow_tip_y + 4),
                    (arrow_x + 3, arrow_tip_y + 4)
                ])

            time_left = player.triple_jump_duration // 60 + 1
            time_text = small_font.render(f'{time_left}s', True, WHITE)
            text_rect = time_text.get_rect(center=(pie_x, pie_y + pie_radius + 15))
            screen.blit(time_text, text_rect)

            timer_y += timer_spacing

        # Dash pie timer
        if player.dash_active:
            pie_x = WIDTH - 80
            pie_y = timer_y
            pie_radius = 30

            pygame.draw.circle(screen, (50, 50, 50), (pie_x, pie_y), pie_radius + 3)
            pygame.draw.circle(screen, (20, 20, 20), (pie_x, pie_y), pie_radius)

            completion = player.dash_duration / player.dash_max_duration
            end_angle = -90 + (360 * (1 - completion))

            if completion > 0:
                points = [(pie_x, pie_y)]
                for angle in range(-90, int(end_angle) + 1, 5):
                    rad = math.radians(angle)
                    x = pie_x + math.cos(rad) * pie_radius
                    y = pie_y + math.sin(rad) * pie_radius
                    points.append((x, y))
                points.append((pie_x, pie_y))

                if len(points) > 2:
                    pygame.draw.polygon(screen, DASH_COLOR, points)

            pulse = 1.0 + math.sin(pygame.time.get_ticks() * 0.02) * 0.1
            ring_radius = int(pie_radius * pulse)
            pygame.draw.circle(screen, DASH_COLOR, (pie_x, pie_y), ring_radius, 3)

            # Lightning bolt icon in center
            center_x = pie_x
            center_y = pie_y
            bolt_points = [
                (center_x - 2, center_y - 8),
                (center_x + 2, center_y - 2),
                (center_x - 1, center_y + 1),
                (center_x + 4, center_y + 8),
                (center_x + 1, center_y + 1),
                (center_x + 2, center_y - 2),
            ]
            pygame.draw.polygon(screen, WHITE, bolt_points)

            time_left = player.dash_duration // 60 + 1
            time_text = small_font.render(f'{time_left}s', True, WHITE)
            text_rect = time_text.get_rect(center=(pie_x, pie_y + pie_radius + 15))
            screen.blit(time_text, text_rect)

            # Dash cooldown indicator
            if player.dash_cooldown > 0:
                cooldown_text = small_font.render(f'CD: {player.dash_cooldown // 6 + 1}', True, (200, 200, 200))
                cd_rect = cooldown_text.get_rect(center=(pie_x, pie_y - pie_radius - 15))
                screen.blit(cooldown_text, cd_rect)

        if game_over:
            game_over_text = font.render('GAME OVER! Press R to Restart', True, (255, 0, 0))
            text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            pygame.draw.rect(screen, WHITE, text_rect.inflate(20, 20))
            screen.blit(game_over_text, text_rect)

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()