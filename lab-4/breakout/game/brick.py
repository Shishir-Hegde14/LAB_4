"""
Brick: a single destructible block.
"""

import pygame

BRICK_TYPES = {
    "red": {
        "hits": 1,
        "color": (210, 55, 55),
        "unbreakable": False,
    },
    "moss": {
        "hits": 3,
        "color": (165, 70, 65),
        "unbreakable": False,
    },
    "concrete": {
        "hits": 5,
        "color": (130, 130, 125),
        "unbreakable": False,
    },
    "metal": {
        "hits": 6,
        "color": (175, 185, 195),
        "unbreakable": False,
    },
    "obsidian": {
        "hits": None,
        "color": (55, 30, 80),
        "unbreakable": True,
    },
}


class Brick:
    def __init__(self, x, y, width, height, brick_type="red"):
        type_data = BRICK_TYPES[brick_type]
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.brick_type = brick_type
        self.max_hits = type_data["hits"]
        self.hits_remaining = type_data["hits"]
        self.color = type_data["color"]
        self.unbreakable = type_data["unbreakable"]

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def damage_taken(self):
        if self.unbreakable:
            return 0
        return self.max_hits - self.hits_remaining
