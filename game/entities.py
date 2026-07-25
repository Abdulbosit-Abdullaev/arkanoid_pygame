import math

import pygame

import settings as cfg

# --- List of power-ups -------------------------------------------------------
# Each power-up has a unique letter (icon) and a color. The behaviour for every
# kind is implemented in screens/game_screen.py -> apply_bonus().
POWER_UPS = {
    "extend":          {"letter": "W", "color": cfg.GREEN},   # widen the paddle
    "paddle_shrink":   {"letter": "S", "color": cfg.RED},     # narrow the paddle
    "ball_speed_up":   {"letter": "+", "color": cfg.ORANGE},  # speed the ball up
    "ball_speed_down": {"letter": "-", "color": cfg.CYAN},    # slow the ball down
}


class Paddle:
    """ Our main player, Paddle, moves only horizontally. """

    def __init__(self) -> None:
        self.rect = pygame.Rect(0, 0, cfg.PADDLE_WIDTH, cfg.PADDLE_HEIGHT)
        self.rect.midbottom = (cfg.WIDTH // 2, cfg.HEIGHT - 20)
        self.speed = cfg.PADDLE_SPEED
        self.vx = 0
        self.extended = False
        self.laser = False

    def move(self, keys: pygame.key.ScancodeWrapper):
        """ Moves the Paddle if the key is pressed. """
        self.vx = 0
        if keys[pygame.K_LEFT]:
            self.vx = -self.speed
        elif keys[pygame.K_RIGHT]:
            self.vx = self.speed
        
        self.rect.x += self.vx

        self._clamp()

    def _clamp(self) -> None:
        """ Restrict the Paddle's movement to the playing field. """
        if self.rect.left < cfg.FIELD_LEFT:
            self.rect.left = cfg.FIELD_LEFT
        if self.rect.right > cfg.FIELD_RIGHT:
            self.rect.right = cfg.FIELD_RIGHT

    def resize(self, delta: int) -> None:
        """ Grows (delta > 0) or shrinks (delta < 0) the paddle, keeping it centered. """
        center = self.rect.centerx
        new_width = max(
            cfg.PADDLE_MIN_WIDTH,
            min(cfg.PADDLE_MAX_WIDTH, self.rect.width + delta),
        )
        self.rect.width = new_width
        self.rect.centerx = center
        self.extended = new_width > cfg.PADDLE_WIDTH
        self._clamp()

    def draw(self, screen: pygame.Surface) -> None:
        """ Renders the Paddle on the screen. """
        pygame.draw.rect(screen, cfg.PADDLE_COLOR, self.rect, border_radius=5)


class Brick:
    """
        Class for Game's brick.

        HP = -1: Level Boundary
        HP = 0: Indestructable
        HP = 1, 2: One / Two hit
    """
    
    def __init__(self, col: int, row: int, hp: int) -> None:
        self.hp = hp
        self.color = cfg.BRICK_COLORS[hp]
        self.rect = pygame.Rect(
            cfg.FIELD_LEFT + col * cfg.BRICK_WIDTH,
            cfg.TOP_OFFSET + row * cfg.BRICK_HEIGHT,
            cfg.BRICK_WIDTH,
            cfg.BRICK_HEIGHT,
        )

    def draw(self, screen: pygame.Surface) -> None:
        """ Renders a Brick in a certain row and col. """
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, cfg.DARK_GRAY, self.rect, 2)
    
    def hit(self) -> None:
        """ Handles the Brick Hit. """
        if self.hp > 0:
            self.hp -= 1
            if self.hp > 0:
                self.color = cfg.BRICK_COLORS[self.hp]
                return
        return

class Ball:
    """ Ball Actor class. """

    def __init__(self, x: int, y: int) -> None:
        self.radius = cfg.BALL_RADIUS
        self.rect = pygame.Rect(
            x - self.radius,
            y - self.radius,
            2 * self.radius,
            2 * self.radius,
        )
        # A pygame.Rect only stores whole pixels, so fractional speeds would be
        # thrown away every frame. The float position below is the real one and
        # the rect is just rounded from it for collisions / drawing.
        self.x = float(self.rect.centerx)
        self.y = float(self.rect.centery)
        self.vx = float(cfg.BALL_SPEED_X)
        self.vy = float(cfg.BALL_SPEED_Y)

    @property
    def speed(self) -> float:
        """ The Ball's total speed. """
        return math.hypot(self.vx, self.vy)

    def update(self) -> None:
        """ Updates the Ball's position for the each frame. """
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (round(self.x), round(self.y))

    def sync_from_rect(self) -> None:
        """ Re-syncs the float position after something moved the rect. """
        self.x = float(self.rect.centerx)
        self.y = float(self.rect.centery)

    def change_speed(self, factor: float) -> None:
        """ Scales the ball's total speed by ``factor`` (clamped), keeping its direction. """
        speed = self.speed
        if speed == 0:
            return
        new_speed = max(cfg.BALL_MIN_SPEED, min(cfg.BALL_MAX_SPEED, speed * factor))
        scale = new_speed / speed
        self.vx *= scale
        self.vy *= scale

    def draw(self, screen: pygame.Surface) -> None:
        """ Renders the Ball. """
        colour = cfg.BALL_COLOR
        pygame.draw.circle(screen, colour, self.rect.center, self.radius)


class PowerUp:
    """ A capsule that drops from a destroyed brick and falls towards the paddle. """

    def __init__(self, x: int, y: int, kind: str) -> None:
        self.kind = kind
        spec = POWER_UPS[kind]
        self.letter = spec["letter"]
        self.color = spec["color"]
        self.rect = pygame.Rect(0, 0, cfg.POWERUP_SIZE, cfg.POWERUP_SIZE)
        self.rect.center = (x, y)
        self.vy = cfg.POWERUP_FALL_SPEED

    def update(self) -> None:
        """ Moves the power-up down one frame. """
        self.rect.y += self.vy

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """ Renders the power-up capsule with its letter (icon). """
        pygame.draw.rect(screen, self.color, self.rect, border_radius=4)
        pygame.draw.rect(screen, cfg.WHITE, self.rect, 2, border_radius=4)
        label = font.render(self.letter, True, cfg.BLACK)
        screen.blit(label, label.get_rect(center=self.rect.center))