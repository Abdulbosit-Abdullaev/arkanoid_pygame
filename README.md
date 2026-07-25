# PyGame Arkanoid

## Requirements

You'll need

1. Git
1. Python3 for your system
1. Python VENV (installs with Python)

To check, you can use commands listed below. If you'll get a "Command not found" error instead of the version, that means you don't have a certain tool installed correctly, so you'll need to reinstall it.

1. `git -v` - to check your git.
1. `python3 --version` - to check your Python. Version 3.11+ is recommended. Older versions are ok, but it's not guaranteed that the game will run on older versions.

## Installation and local run

1. Clone this repo: `git clone https://github.com/uptothetop/arkanoid_pygame.git`
1. Go to the app's folder: `cd arkanoid_pygame`
1. Set up your virtual env (venv): `python3 -m venv env`
1. Activate your venv: 
    1. OSX, Linux, Unix systems: `source env/bin/activate`
    1. For Windows use Powershell: `.\env\Scripts\Activate.ps1`
1. After activation there will be venv name in brackets in your terminal, for example `(env)`
1. Install dependencies: `pip install -r requirements.txt`
1. Run the app: `python3 main.py`

After that you should see a window titled as "Arkanoid" with the level loaded and the
ball resting on the paddle - that means that you've installed everything correctly.

## How to play

| Key | Action |
| --- | --- |
| `<-` / `->` | Move the paddle |
| `SPACE` | Launch the ball |
| `R` | Restart after Game Over / You Win |

Break every colored brick to win. Gray bricks are indestructible - they only bounce the
ball. You start with 3 lives and lose one whenever the ball falls below the paddle.

## Power-ups

Destroyed bricks have a 30% chance to drop a power-up. Catch it with the paddle to
apply its effect.

| Icon | Power-up | Effect |
| --- | --- | --- |
| `W` (green) | Extend | Makes the paddle wider |
| `S` (red) | Paddle Shrink | Makes the paddle narrower |
| `+` (orange) | Ball Speed Up | Makes the ball faster |
| `-` (cyan) | Ball Speed Down | Makes the ball slower |

Power-ups are listed in `game/entities.py` (`POWER_UPS`) and their behaviour is
implemented in `screens/game_screen.py` (`apply_bonus`). Sizes, speeds, limits and the
drop chance can all be tweaked in `settings.py`.
