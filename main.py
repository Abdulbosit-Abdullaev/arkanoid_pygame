import math
import random

import pygame
import settings as cfg
from screens.game_screen import apply_bonus
from game.entities import Paddle, Brick, Ball, PowerUp, POWER_UPS
from game.level import load_level

def _bounce_off_rect(ball: Ball, rect: pygame.Rect):
    """ Checks if the Ball collides with the given rect. """

    # Calculate ball's overlaps and find the smallest one
    overlap_left = ball.rect.right - rect.left
    overlap_right = rect.right - ball.rect.left
    overlap_top = ball.rect.bottom - rect.top
    overlap_bottom = rect.bottom - ball.rect.top

    min_overlap = min(
        overlap_bottom,
        overlap_left,
        overlap_right,
        overlap_top)

    # Calculate the Ball's final velocities
    if min_overlap == overlap_top and ball.vy > 0:
        ball.rect.bottom = rect.top
        ball.vy *= -1
    elif min_overlap == overlap_bottom and ball.vy < 0:
        ball.rect.top = rect.bottom
        ball.vy *= -1
    elif min_overlap == overlap_left and ball.vx > 0:
        ball.rect.right = rect.left
        ball.vx *= -1
    elif min_overlap == overlap_right and ball.vx < 0:
        ball.rect.left = rect.right
        ball.vx *= -1

    # The rect was nudged out of the obstacle, keep the float position in step
    ball.sync_from_rect()

def _handle_ball_vs_bricks(
    ball: Ball,
    bricks: list[Brick],
    powerups: list[PowerUp],
) -> int:

    scored = 0
    for brick in bricks[:]:
        if not ball.rect.colliderect(brick.rect):
            continue
        _bounce_off_rect(ball, brick.rect)
        # hp -1 is a boundary wall and hp 0 is an indestructible brick:
        # both only bounce the ball, they are never destroyed or scored.
        if brick.hp <= 0:
            continue
        brick.hit()

        if brick.hp <= 0:
            bricks.remove(brick)
            scored += cfg.BRICK_SCORE
            # Chance to drop a random power-up where the brick was
            if random.random() < cfg.BONUS_PROBABILITY:
                kind = random.choice(list(POWER_UPS))
                powerups.append(PowerUp(brick.rect.centerx, brick.rect.centery, kind))
    return scored

def _handle_ball_vs_paddle(ball: Ball, paddle: Paddle) -> None:
    """ Handles Ball bounce over the Paddle.

    Where the Ball lands on the Paddle decides the bounce *angle*, while the
    Ball's total *speed* is kept untouched - otherwise every paddle hit would
    silently undo the Ball Speed Up / Ball Speed Down power-ups.
    """
    speed = ball.speed
    _bounce_off_rect(ball, paddle.rect)

    # -1.0 at the paddle's left edge, 0.0 in the middle, +1.0 at the right edge
    offset = (ball.rect.centerx - paddle.rect.centerx) / (paddle.rect.width / 2)
    offset = max(-1.0, min(1.0, offset))

    angle = math.radians(cfg.MAX_BOUNCE_ANGLE) * offset

    # A dead-centre hit would send the ball perfectly vertical, and it could then
    # bounce up and down forever in an empty column. Always keep a little angle.
    min_angle = math.radians(cfg.MIN_BOUNCE_ANGLE)
    if abs(angle) < min_angle:
        if ball.vx != 0:
            direction = math.copysign(1, ball.vx)      # carry on the same way
        elif offset != 0:
            direction = math.copysign(1, offset)
        else:
            direction = 1 if paddle.rect.centerx < cfg.WIDTH // 2 else -1
        angle = min_angle * direction

    vx = speed * math.sin(angle)

    # Keep the horizontal speed sane, then rebuild vy so the total speed holds
    vx = max(-cfg.MAX_BALL_SPEED_X, min(cfg.MAX_BALL_SPEED_X, vx))
    ball.vx = vx
    ball.vy = -math.sqrt(max(0.0, speed * speed - vx * vx))

def _new_ball(paddle: Paddle) -> Ball:
    """ Creates a Ball resting on top of the Paddle, waiting to be served. """
    return Ball(paddle.rect.centerx, paddle.rect.top - cfg.BALL_RADIUS - 1)

def _stick_to_paddle(ball: Ball, paddle: Paddle) -> None:
    """ Keeps the not-yet-served Ball glued on top of the Paddle. """
    ball.rect.midbottom = (paddle.rect.centerx, paddle.rect.top - 1)
    ball.sync_from_rect()

def _level_cleared(bricks: list[Brick]) -> bool:
    """ True when no destructible bricks are left. """
    return not any(brick.hp > 0 for brick in bricks)

def _draw_hud(screen: pygame.Surface, font: pygame.font.Font, score: int, lives: int) -> None:
    """ Renders the top status bar: score and remaining lives. """
    score_text = font.render(f"Score: {score}", True, cfg.WHITE)
    screen.blit(score_text, (cfg.FIELD_LEFT, 12))

    lives_text = font.render(f"Lives: {lives}", True, cfg.WHITE)
    screen.blit(lives_text, lives_text.get_rect(topright=(cfg.FIELD_RIGHT, 12)))

def _draw_message(
    screen: pygame.Surface,
    big_font: pygame.font.Font,
    font: pygame.font.Font,
    title: str,
    subtitle: str,
) -> None:
    """ Dims the field and shows a centered message (serve prompt / game over / win). """
    overlay = pygame.Surface((cfg.WIDTH, cfg.HEIGHT))
    overlay.set_alpha(160)
    overlay.fill(cfg.BLACK)
    screen.blit(overlay, (0, 0))

    title_text = big_font.render(title, True, cfg.WHITE)
    screen.blit(title_text, title_text.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT // 2 - 20)))

    subtitle_text = font.render(subtitle, True, cfg.YELLOW)
    screen.blit(subtitle_text, subtitle_text.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT // 2 + 30)))

def main():
    pygame.init()
    screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
    pygame.display.set_caption("Arkanoid")
    clock = pygame.time.Clock()

    powerup_font = pygame.font.SysFont(None, 20)
    hud_font = pygame.font.SysFont(None, 28)
    big_font = pygame.font.SysFont(None, 72)

    def start_game():
        """ Builds a fresh game: level, paddle, ball on the paddle, no power-ups. """
        paddle = Paddle()
        bricks, _, _ = load_level(1)
        return paddle, bricks, _new_ball(paddle), [], cfg.START_LIVES, 0

    paddle, bricks, ball, powerups, lives, score = start_game()
    served = False    # False while the ball waits on the paddle
    game_over = False
    won = False

    running = True
    while running:
        # Main Loop
        screen.fill(cfg.BLACK)

        # Event Section
        for event in pygame.event.get():
            if event.type == pygame.QUIT:   # Press "close" button
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not served and not game_over:
                    served = True   # Launch the ball
                elif event.key == pygame.K_r and game_over:
                    paddle, bricks, ball, powerups, lives, score = start_game()
                    served = False
                    game_over = False
                    won = False

        # Update Section
        if not game_over:
            keys = pygame.key.get_pressed()

            paddle.move(keys)

            if not served:
                # Ball rides the paddle until the player serves it
                _stick_to_paddle(ball, paddle)
            else:
                score += _handle_ball_vs_bricks(ball, bricks, powerups)

                if ball.rect.colliderect(paddle.rect) and ball.vy > 0:
                    _handle_ball_vs_paddle(ball, paddle)

                ball.update()

                # Ball fell below the paddle -> lose a life
                if ball.rect.top > cfg.HEIGHT:
                    lives -= 1
                    powerups.clear()
                    if lives <= 0:
                        game_over = True
                    else:
                        paddle = Paddle()   # Reset the paddle's size and position
                        ball = _new_ball(paddle)
                        served = False

            # Update falling power-ups: catch on the paddle, drop off the bottom
            for powerup in powerups[:]:
                powerup.update()
                if powerup.rect.colliderect(paddle.rect):
                    apply_bonus(powerup.kind, paddle, ball)
                    powerups.remove(powerup)
                elif powerup.rect.top > cfg.HEIGHT:
                    powerups.remove(powerup)

            # All destructible bricks cleared -> the player wins
            if _level_cleared(bricks):
                game_over = True
                won = True

        # Draw Section
        for brick in bricks:
            brick.draw(screen)

        for powerup in powerups:
            powerup.draw(screen, powerup_font)

        paddle.draw(screen)
        if not (game_over and not won):
            ball.draw(screen)

        _draw_hud(screen, hud_font, score, lives)

        if game_over:
            if won:
                _draw_message(screen, big_font, hud_font,
                              "YOU WIN!", f"Score: {score}  -  Press R to play again")
            else:
                _draw_message(screen, big_font, hud_font,
                              "GAME OVER", f"Score: {score}  -  Press R to play again")
        elif not served:
            _draw_message(screen, big_font, hud_font,
                          "READY", "Press SPACE to launch the ball")

        pygame.display.flip()   # Screen Update
        clock.tick(cfg.FPS)         # FPS (Frames Per Second)

    pygame.quit()

if __name__ == "__main__":
    main()
