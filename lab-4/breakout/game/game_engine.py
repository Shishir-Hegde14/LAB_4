"""
GameEngine: owns the paddle, ball, and bricks.

Starter version: single brick type, no lives yet, no score/combo yet.
Ball-brick collision also has a known bug (see game/collision.py) that
Task 1 asks you to fix. If the ball falls below the paddle, it just
resets to the starting position with no consequence - that's what
Task 2 builds on.
"""

import pygame
import random

from game.paddle import Paddle
from game.ball import Ball
from game.brick import Brick
from game.collision import handle_ball_brick_collision
from game.renderer import WIDTH, HEIGHT

BRICK_ROWS = 4
BRICK_COLS = 8
BRICK_WIDTH = 68
BRICK_HEIGHT = 22
BRICK_GAP = 6
BRICK_TOP_MARGIN = 50
PARTICLE_COUNT = 8
BREAK_PARTICLE_COUNT = 14
PARTICLE_LIFETIME = 20
SHAKE_FRAMES = 8
COMBO_SHAKE_FRAMES = 14
FINAL_EXPLOSION_FRAMES = 40
OBSIDIAN_MAX_COUNT = 3
STARTING_LIVES = 3
STATE_PLAYING = "playing"
STATE_WIN_PENDING = "win_pending"
STATE_WON = "won"
STATE_GAME_OVER = "game_over"
BRICK_SCORES = {
    "red": 1,
    "moss": 3,
    "concrete": 5,
    "metal": 6,
}
COMBO_NONE = "none"
COMBO_1X = "1x"
COMBO_2X = "2x"
COMBO_5X = "5x"
COMBO_BOOSTS = {
    COMBO_NONE: 0,
    COMBO_1X: 3,
    COMBO_2X: 4,
    COMBO_5X: 5,
}
COMBO_LABELS = {
    COMBO_1X: "1X",
    COMBO_2X: "2X",
    COMBO_5X: "5X",
}
COMBO_LABEL_COLORS = {
    COMBO_1X: (255, 230, 60),
    COMBO_2X: (230, 45, 35),
    COMBO_5X: (170, 75, 255),
}
COMBO_TRAIL_COLORS = {
    COMBO_1X: [(255, 235, 80), (255, 200, 40)],
    COMBO_2X: [(190, 20, 20), (255, 70, 45)],
    COMBO_5X: [(255, 190, 45), (255, 80, 20), (160, 45, 255)],
}
COMBO_DECAY_HITS = 5


class GameEngine:
    def __init__(self):
        self.paddle = None
        self.ball = None
        self.bricks = self._build_bricks()
        self.particles = []
        self.lives = STARTING_LIVES
        self.state = STATE_PLAYING
        self.buttons = self._build_buttons()
        self.shake_frames = 0
        self.score = 0
        self.break_streak = 0
        self.combo_mode = COMBO_NONE
        self.non_breaking_hits = 0
        self.win_delay_frames = 0
        self._reset_positions()

    def _build_bricks(self):
        bricks = []
        total_width = BRICK_COLS * (BRICK_WIDTH + BRICK_GAP) - BRICK_GAP
        start_x = (WIDTH - total_width) / 2
        brick_types = self._build_random_brick_types()
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                x = start_x + col * (BRICK_WIDTH + BRICK_GAP)
                y = BRICK_TOP_MARGIN + row * (BRICK_HEIGHT + BRICK_GAP)
                brick_type = brick_types.pop()
                bricks.append(Brick(x, y, BRICK_WIDTH, BRICK_HEIGHT, brick_type))
        return bricks

    def _build_random_brick_types(self):
        total_bricks = BRICK_ROWS * BRICK_COLS
        obsidian_count = random.randint(0, OBSIDIAN_MAX_COUNT)
        metal_count = 3
        concrete_count = 5
        moss_count = 8
        red_count = total_bricks - obsidian_count - metal_count - concrete_count - moss_count
        brick_types = (
            ["red"] * red_count
            + ["moss"] * moss_count
            + ["concrete"] * concrete_count
            + ["metal"] * metal_count
            + ["obsidian"] * obsidian_count
        )
        random.shuffle(brick_types)
        return brick_types

    def _build_buttons(self):
        button_width = 160
        button_height = 46
        gap = 18
        top = HEIGHT // 2 + 45
        start_x = (WIDTH - (button_width * 2 + gap)) // 2
        return {
            "restart": pygame.Rect(start_x, top, button_width, button_height),
            "quit": pygame.Rect(start_x + button_width + gap, top, button_width, button_height),
        }

    def _reset_positions(self):
        self.paddle = Paddle(x=WIDTH / 2, y=HEIGHT - 30)
        self.ball = Ball(x=WIDTH / 2, y=HEIGHT - 50)

    def restart_game(self):
        self.bricks = self._build_bricks()
        self.particles = []
        self.lives = STARTING_LIVES
        self.state = STATE_PLAYING
        self.shake_frames = 0
        self.score = 0
        self._reset_combo()
        self.win_delay_frames = 0
        self._reset_positions()

    def _spawn_particles(self, brick, colors, count=PARTICLE_COUNT, shape="circle"):
        rect = brick.get_rect()
        for _ in range(count):
            self.particles.append({
                "x": rect.centerx,
                "y": rect.centery,
                "vx": random.uniform(-3.0, 3.0),
                "vy": random.uniform(-3.0, 1.7),
                "life": PARTICLE_LIFETIME,
                "color": random.choice(colors),
                "shape": shape,
                "size": random.randint(3, 5),
            })

    def _spawn_text_particle(self, brick, text, color):
        rect = brick.get_rect()
        self.particles.append({
            "x": rect.centerx,
            "y": rect.top - 6,
            "vx": random.uniform(-0.4, 0.4),
            "vy": -1.2,
            "life": 36,
            "color": color,
            "shape": "text",
            "text": text,
            "size": 18,
        })

    def _spawn_ball_trail(self):
        if self.combo_mode == COMBO_NONE:
            return

        base_count = 3 if self.combo_mode == COMBO_5X else 1
        count = max(1, base_count - self.non_breaking_hits // 2)
        base_life = 18 if self.combo_mode == COMBO_5X else 14
        particle_life = max(6, base_life - self.non_breaking_hits * 2)
        colors = COMBO_TRAIL_COLORS[self.combo_mode]
        for _ in range(count):
            self.particles.append({
                "x": self.ball.x + random.uniform(-5, 5),
                "y": self.ball.y + random.uniform(-5, 5),
                "vx": random.uniform(-0.8, 0.8) - self.ball.vx * 0.12,
                "vy": random.uniform(-0.8, 0.8) - self.ball.vy * 0.12,
                "life": particle_life,
                "color": random.choice(colors),
                "shape": "circle",
                "size": random.randint(2, 4),
            })

    def _spawn_final_explosion(self):
        for brick in self.bricks[:]:
            rect = brick.get_rect()
            for _ in range(8):
                self.particles.append({
                    "x": rect.centerx,
                    "y": rect.centery,
                    "vx": random.uniform(-4.5, 4.5),
                    "vy": random.uniform(-4.5, 2.5),
                    "life": 34,
                    "color": random.choice([(255, 190, 45), (255, 80, 20), (170, 75, 255)]),
                    "shape": "spike" if random.random() < 0.45 else "circle",
                    "size": random.randint(3, 6),
                })
        self.bricks = []
        self.shake_frames = COMBO_SHAKE_FRAMES
        self.win_delay_frames = FINAL_EXPLOSION_FRAMES
        self.state = STATE_WIN_PENDING

    def _spawn_hit_particles(self, brick):
        colors = {
            "red": [(230, 65, 65), (255, 120, 95)],
            "moss": [(70, 210, 80), (130, 235, 105)],
            "concrete": [(165, 165, 160), (115, 115, 110)],
            "metal": [(220, 225, 230), (170, 180, 190)],
            "obsidian": [(170, 80, 255), (105, 40, 190)],
        }
        self._spawn_particles(brick, colors[brick.brick_type])

    def _spawn_break_particles(self, brick):
        colors = {
            "red": [(230, 55, 55), (255, 105, 85)],
            "moss": [(75, 210, 85), (205, 65, 60)],
            "concrete": [(155, 155, 150), (120, 95, 70)],
            "metal": [(235, 240, 245), (165, 175, 185)],
        }
        shape = "spike" if brick.brick_type == "metal" else "circle"
        self._spawn_particles(brick, colors[brick.brick_type], BREAK_PARTICLE_COUNT, shape)

    def _breakable_bricks_left(self):
        return sum(1 for brick in self.bricks if not brick.unbreakable)

    def _combo_mode_for_streak(self, streak):
        if streak >= 8:
            return COMBO_5X
        if streak >= 5:
            return COMBO_2X
        if streak >= 3:
            return COMBO_1X
        return COMBO_NONE

    def _score_combo_for_next_break(self):
        if self.break_streak >= 8:
            return COMBO_5X
        if self.break_streak >= 5:
            return COMBO_2X
        if self.break_streak >= 3:
            return COMBO_1X
        return COMBO_NONE

    def _reset_combo(self):
        self.break_streak = 0
        self.combo_mode = COMBO_NONE
        self.non_breaking_hits = 0

    def _record_non_breaking_hit(self):
        if self.combo_mode == COMBO_NONE:
            return

        self.non_breaking_hits += 1
        if self.non_breaking_hits >= COMBO_DECAY_HITS:
            self._reset_combo()

    def _score_break(self, brick):
        score_combo = self._score_combo_for_next_break()
        points = BRICK_SCORES.get(brick.brick_type, 0) + COMBO_BOOSTS[score_combo]
        self.score += points

        if score_combo != COMBO_NONE:
            self._spawn_text_particle(
                brick,
                COMBO_LABELS[score_combo],
                COMBO_LABEL_COLORS[score_combo],
            )

        previous_mode = self.combo_mode
        self.break_streak += 1
        self.non_breaking_hits = 0
        self.combo_mode = self._combo_mode_for_streak(self.break_streak)
        if previous_mode in (COMBO_1X, COMBO_2X) and self.combo_mode != previous_mode:
            self.shake_frames = COMBO_SHAKE_FRAMES

    def _handle_brick_hit(self, brick):
        if brick.brick_type == "metal":
            self.shake_frames = SHAKE_FRAMES

        if brick.unbreakable:
            self._spawn_hit_particles(brick)
            return False

        brick.hits_remaining -= 1
        if brick.hits_remaining <= 0:
            self._score_break(brick)
            self._spawn_break_particles(brick)
            return True

        self._spawn_hit_particles(brick)
        return False

    def _update_particles(self):
        alive_particles = []
        for particle in self.particles:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["vy"] += 0.12
            particle["life"] -= 1
            if particle["life"] > 0:
                alive_particles.append(particle)
        self.particles = alive_particles

    def _update_shake(self):
        if self.shake_frames > 0:
            self.shake_frames -= 1

    def handle_input(self, keys_pressed):
        if self.state != STATE_PLAYING:
            return

        dx = 0
        if keys_pressed[pygame.K_LEFT]:
            dx -= self.paddle.speed
        if keys_pressed[pygame.K_RIGHT]:
            dx += self.paddle.speed
        self.paddle.move(dx, WIDTH)

    def handle_keydown(self, key):
        pass

    def handle_mouse_down(self, pos):
        if self.state not in (STATE_WON, STATE_GAME_OVER):
            return None

        if self.buttons["restart"].collidepoint(pos):
            self.restart_game()
            return "restart"
        if self.buttons["quit"].collidepoint(pos):
            return "quit"
        return None

    def update(self):
        if self.state == STATE_WIN_PENDING:
            self._update_particles()
            self._update_shake()
            self.win_delay_frames -= 1
            if self.win_delay_frames <= 0:
                self.state = STATE_WON
            return

        if self.state != STATE_PLAYING:
            return

        self.ball.update()
        self._spawn_ball_trail()
        self.ball.bounce_off_walls(WIDTH)

        if self.ball.get_rect().colliderect(self.paddle.get_rect()) and self.ball.vy > 0:
            self.ball.bounce_off_paddle(self.paddle.get_rect())
            self._record_non_breaking_hit()

        for brick in self.bricks[:]:
            if handle_ball_brick_collision(self.ball, brick):
                was_5x_combo = self.combo_mode == COMBO_5X
                if self._handle_brick_hit(brick):
                    self.bricks.remove(brick)
                    if self._breakable_bricks_left() == 0 and was_5x_combo:
                        self._spawn_final_explosion()
                if self._breakable_bricks_left() == 0:
                    if self.state != STATE_WIN_PENDING:
                        self.state = STATE_WON
                break

        self._update_particles()
        self._update_shake()

        if self.ball.is_below(HEIGHT):
            self.lives -= 1
            self._reset_combo()
            if self.lives <= 0:
                self.state = STATE_GAME_OVER
            else:
                self._reset_positions()

    def draw(self, surface, font):
        from game import renderer
        shake_offset = (0, 0)
        if self.shake_frames > 0:
            shake_offset = (random.randint(-4, 4), random.randint(-4, 4))
        renderer.draw_scene(
            surface,
            self.paddle,
            self.ball,
            self.bricks,
            self.particles,
            shake_offset,
            self.combo_mode,
        )
        renderer.draw_hud(surface, font, self.score, self.lives, self.combo_mode)
        if self.state == STATE_WON:
            renderer.draw_end_screen(surface, font, "YOU WIN", self.buttons, self.score)
        elif self.state == STATE_GAME_OVER:
            renderer.draw_end_screen(surface, font, "GAME OVER", self.buttons, self.score)
