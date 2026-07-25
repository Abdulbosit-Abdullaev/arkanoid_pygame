import pygame

import settings as cfg
from game.entities import Paddle, Ball


def run(screen: pygame.Surface, clock: pygame.time.Clock, level: int) -> None:
    paddle = Paddle()

    keys = pygame.key.get_pressed()
    paddle.move(keys)

    paddle.draw(screen)


def apply_bonus(kind: str, paddle: Paddle, ball: Ball) -> None:
    """ Applies a caught power-up's effect (the homework's ``ApplyBonus``).

    Each branch corresponds to one power-up kind defined in
    ``game.entities.POWER_UPS``.
    """
    if kind == "extend":
        paddle.resize(cfg.PADDLE_RESIZE_STEP)          
    elif kind == "paddle_shrink":
        paddle.resize(-cfg.PADDLE_RESIZE_STEP)         
    elif kind == "ball_speed_up":
        ball.change_speed(cfg.BALL_SPEED_FACTOR)       
    elif kind == "ball_speed_down":
        ball.change_speed(1 / cfg.BALL_SPEED_FACTOR) 
