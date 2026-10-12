"""
renderer: all pygame drawing lives here, kept separate from game logic.
"""

import math
import pygame

WIDTH, HEIGHT = 640, 520
WINDOW_SIZE = (WIDTH, HEIGHT)

COLOR_BG = (20, 20, 30)
COLOR_PADDLE = (80, 180, 255)
COLOR_BALL = (240, 240, 240)
COLOR_TEXT = (255, 255, 255)
COMBO_STYLES = {
    "none": {
        "ball": COLOR_BALL,
        "paddle": COLOR_PADDLE,
        "glow": None,
    },
    "1x": {
        "ball": (255, 225, 55),
        "paddle": (255, 215, 70),
        "glow": (255, 225, 65),
    },
    "2x": {
        "ball": (150, 20, 20),
        "paddle": (220, 45, 35),
        "glow": (230, 45, 35),
    },
    "5x": {
        "ball": (255, 105, 35),
        "paddle": (160, 70, 230),
        "glow": (170, 75, 255),
    },
}


def draw_scene(surface, paddle, ball, bricks, particles=None, shake_offset=(0, 0), combo_mode="none"):
    target = surface
    if shake_offset != (0, 0):
        target = pygame.Surface(WINDOW_SIZE)

    surface.fill(COLOR_BG)
    target.fill(COLOR_BG)
    for brick in bricks:
        draw_brick(target, brick)
    if particles:
        for particle in particles:
            draw_particle(target, particle)
    draw_paddle(target, paddle, combo_mode)
    draw_ball(target, ball, combo_mode)

    if target is not surface:
        surface.blit(target, shake_offset)


def draw_paddle(surface, paddle, combo_mode):
    rect = paddle.get_rect()
    style = COMBO_STYLES[combo_mode]
    if style["glow"]:
        pulse = (math.sin(pygame.time.get_ticks() * 0.014) + 1) * 0.5
        glow_size = 8 + int(4 * pulse)
        glow_rect = rect.inflate(glow_size * 2, glow_size)
        pygame.draw.rect(surface, style["glow"], glow_rect, border_radius=7)
    pygame.draw.rect(surface, style["paddle"], rect, border_radius=4)
    pygame.draw.line(surface, (255, 255, 255), (rect.left + 8, rect.top + 3), (rect.right - 8, rect.top + 3), 2)


def draw_ball(surface, ball, combo_mode):
    style = COMBO_STYLES[combo_mode]
    pos = (int(ball.x), int(ball.y))
    if style["glow"]:
        pygame.draw.circle(surface, style["glow"], pos, ball.radius + 6)
    if combo_mode == "5x":
        pygame.draw.circle(surface, (110, 25, 20), pos, ball.radius + 3)
        pygame.draw.circle(surface, (255, 190, 45), pos, ball.radius)
        pygame.draw.circle(surface, (255, 70, 20), pos, max(2, ball.radius - 3))
    else:
        pygame.draw.circle(surface, style["ball"], pos, ball.radius)


def draw_brick(surface, brick):
    rect = brick.get_rect()
    if brick.brick_type == "moss":
        draw_moss_brick(surface, brick, rect)
    elif brick.brick_type == "concrete":
        draw_concrete_brick(surface, brick, rect)
    elif brick.brick_type == "metal":
        draw_metal_brick(surface, brick, rect)
    elif brick.brick_type == "obsidian":
        draw_obsidian_brick(surface, brick, rect)
    else:
        pygame.draw.rect(surface, brick.color, rect)
        pygame.draw.rect(surface, (120, 20, 20), rect, 1)


def draw_moss_brick(surface, brick, rect):
    pygame.draw.rect(surface, (55, 150, 55), rect, border_radius=3)
    pygame.draw.rect(surface, (80, 180, 65), rect.inflate(-8, -6), border_radius=3)
    dark_dots = [
        (7, 6, 2), (15, 15, 2), (24, 8, 3), (34, 17, 2),
        (44, 6, 2), (53, 14, 3), (61, 8, 2), (12, 10, 1),
        (30, 14, 1), (47, 18, 1),
    ]
    for x, y, radius in dark_dots:
        pygame.draw.circle(surface, (20, 80, 30), (rect.x + x, rect.y + y), radius)
    pygame.draw.rect(surface, (25, 95, 35), rect, 1, border_radius=3)


def draw_concrete_brick(surface, brick, rect):
    points = [
        (rect.left + 5, rect.top),
        (rect.right - 4, rect.top),
        (rect.right, rect.top + 5),
        (rect.right - 3, rect.bottom - 3),
        (rect.left + 4, rect.bottom),
        (rect.left, rect.bottom - 5),
        (rect.left + 2, rect.top + 4),
    ]
    pygame.draw.polygon(surface, brick.color, points)
    pygame.draw.line(surface, (180, 180, 175), points[0], points[1], 2)
    pygame.draw.line(surface, (85, 85, 80), points[3], points[4], 2)
    speckles = [
        (8, 6), (18, 15), (30, 8), (43, 17), (58, 7),
        (12, 18), (52, 14), (37, 5),
    ]
    for x, y in speckles:
        pygame.draw.circle(surface, (95, 95, 90), (rect.x + x, rect.y + y), 1)

    cracks = [
        [(rect.x + 10, rect.y + 5), (rect.x + 20, rect.y + 12), (rect.x + 28, rect.y + 9)],
        [(rect.x + 42, rect.y + 3), (rect.x + 38, rect.y + 13), (rect.x + 47, rect.y + 20)],
        [(rect.x + 25, rect.y + 18), (rect.x + 34, rect.y + 13), (rect.x + 41, rect.y + 16)],
        [(rect.x + 54, rect.y + 6), (rect.x + 61, rect.y + 12), (rect.x + 58, rect.y + 19)],
        [(rect.x + 5, rect.y + 17), (rect.x + 14, rect.y + 13), (rect.x + 18, rect.y + 20)],
    ]
    for crack in cracks[:brick.damage_taken()]:
        pygame.draw.lines(surface, (45, 45, 45), False, crack, 2)
    pygame.draw.polygon(surface, (70, 70, 70), points, 1)


def draw_metal_brick(surface, brick, rect):
    pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 0.5
    glow = 20 + int(25 * pulse)
    pygame.draw.rect(surface, (120 + glow, 130 + glow, 140 + glow), rect.inflate(6, 6), border_radius=4)
    pygame.draw.rect(surface, brick.color, rect, border_radius=2)
    pygame.draw.line(surface, (245, 250, 255), (rect.left + 7, rect.top + 5), (rect.right - 8, rect.top + 2), 2)
    pygame.draw.line(surface, (105, 115, 125), (rect.left + 5, rect.bottom - 4), (rect.right - 6, rect.bottom - 8), 2)
    pygame.draw.rect(surface, (80, 90, 100), rect, 1, border_radius=2)


def draw_obsidian_brick(surface, brick, rect):
    pygame.draw.rect(surface, (95, 40, 145), rect.inflate(10, 10), border_radius=5)
    pygame.draw.rect(surface, brick.color, rect, border_radius=3)
    pygame.draw.line(surface, (160, 80, 230), (rect.left + 8, rect.top + 4), (rect.right - 10, rect.bottom - 6), 2)
    pygame.draw.line(surface, (80, 35, 130), (rect.left + 12, rect.bottom - 4), (rect.right - 5, rect.top + 8), 1)
    pygame.draw.rect(surface, (190, 95, 255), rect, 1, border_radius=3)


def draw_particle(surface, particle):
    pos = (int(particle["x"]), int(particle["y"]))
    if particle.get("shape") == "text":
        particle_font = pygame.font.SysFont("consolas", particle.get("size", 18), bold=True)
        text_surf = particle_font.render(particle["text"], True, particle["color"])
        surface.blit(text_surf, text_surf.get_rect(center=pos))
    elif particle.get("shape") == "spike":
        size = particle.get("size", 4)
        points = [
            (pos[0], pos[1] - size * 2),
            (pos[0] - size, pos[1] + size),
            (pos[0] + size, pos[1] + size),
        ]
        pygame.draw.polygon(surface, particle["color"], points)
    else:
        pygame.draw.circle(surface, particle["color"], pos, particle.get("size", 3))


def draw_text(surface, font, text, pos, color=COLOR_TEXT):
    surface.blit(font.render(text, True, color), pos)


def draw_hud(surface, font, score, lives, combo_mode):
    hud_font = pygame.font.SysFont("consolas", 22, bold=True)
    small_font = pygame.font.SysFont("consolas", 16, bold=True)
    score_rect = pygame.Rect(10, 10, 150, 34)
    lives_rect = pygame.Rect(WIDTH - 128, 10, 118, 34)

    for rect in (score_rect, lives_rect):
        pygame.draw.rect(surface, (32, 34, 44), rect, border_radius=6)
        pygame.draw.rect(surface, (95, 105, 120), rect, 1, border_radius=6)

    score_surf = hud_font.render(f"Score {score}", True, (255, 245, 210))
    surface.blit(score_surf, (score_rect.x + 10, score_rect.y + 5))

    lives_surf = hud_font.render(f"Lives {lives}", True, (190, 230, 255))
    surface.blit(lives_surf, (lives_rect.x + 10, lives_rect.y + 5))

    if combo_mode != "none":
        combo_colors = {
            "1x": (255, 230, 60),
            "2x": (235, 50, 40),
            "5x": (180, 85, 255),
        }
        combo_rect = pygame.Rect(WIDTH // 2 - 54, 10, 108, 34)
        pygame.draw.rect(surface, (28, 24, 34), combo_rect, border_radius=6)
        pygame.draw.rect(surface, combo_colors[combo_mode], combo_rect, 2, border_radius=6)
        combo_surf = small_font.render(f"{combo_mode.upper()} COMBO", True, combo_colors[combo_mode])
        surface.blit(combo_surf, combo_surf.get_rect(center=combo_rect.center))


def draw_end_screen(surface, font, title, buttons, score):
    overlay = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    surface.blit(overlay, (0, 0))

    title_font = pygame.font.SysFont("consolas", 56, bold=True)
    title_surf = title_font.render(title, True, (255, 220, 80))
    title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
    surface.blit(title_surf, title_rect)

    score_font = pygame.font.SysFont("consolas", 26, bold=True)
    score_surf = score_font.render(f"Final Score: {score}", True, (255, 255, 255))
    score_rect = score_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 5))
    surface.blit(score_surf, score_rect)

    button_labels = {
        "restart": "Restart Game",
        "quit": "Quit",
    }
    for name, rect in buttons.items():
        pygame.draw.rect(surface, (255, 255, 255), rect, border_radius=6)
        pygame.draw.rect(surface, (40, 40, 50), rect, 2, border_radius=6)
        label_surf = font.render(button_labels[name], True, (15, 15, 20))
        label_rect = label_surf.get_rect(center=rect.center)
        surface.blit(label_surf, label_rect)


def draw_banner(surface, font, text):
    surf = font.render(text, True, (255, 220, 80))
    rect = surf.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
    surface.blit(surf, rect)
