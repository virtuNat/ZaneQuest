import os
import re
import pygame as pg
from common import (ClipDrawSprite)

class BoxedText(pg.sprite.Sprite):

    def __init__(self, rect, font, size, scroll=0):
        super().__init__()
        self.image = pg.Surface(rect.size, pg.SRCALPHA, 32)
        self.rect = rect
        self.font = pg.font.Font(font, size)
        self.scroll = scroll # If non-zero, the frame delay between letters.
        self.frame = 0
        self.color = pg.Color(0, 0, 0)

    def set_text(self, text, color):
        self.frame = 0
        self.color = color
        if not self.scroll:
            self.render(text)
            self.textgen = iter(())
        else:
            self.textgen = (text[:i+1] for i in range(len(text)) if text[i] != ' ')

    def render(self, text):
        words = re.findall(r'\S+\s*', text)
        lines = [words[0]]
        for word in words[1:]:
            if self.font.size(lines[-1]+word)[0] > self.rect.w:
                lines.append(word)
            else:
                lines[-1] += word
        self.image.fill(pg.Color(0, 0, 0, 0))
        size = self.font.get_linesize()
        for idx, line in enumerate(lines):
            self.image.blit(self.font.render(line, True, self.color), (0, idx * size))

    def update(self):
        if self.scroll > 0 and self.frame == 0:
            try:
                self.render(next(self.textgen))
            except StopIteration:
                pass
            else:
                self.frame = (self.frame + 1) % self.scroll


class TextBox(ClipDrawSprite):

    def __init__(self, bounds, atlas, rect=None, clip=None):
        super().__init__(atlas, rect, clip)
        self.boxed_text = None
        self.frame = 0

    def update(self):
        pass


class SampleTextBox(TextBox):

    def __init__(self, bounds):
        super().__init__(
            bounds,
            pg.Surface((900, 210), pg.SRCALPHA, 32),
            )
        self.rect.midbottom = bounds.midbottom
        self.boxed_text = BoxedText(
            pg.Rect(10, 10, 880, 200),
            os.path.join('assets', 'fonts', 'DejaVuSansCondensed.ttf'), 20, 1,
            )
        self.boxed_text.set_text(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor "
            "incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis "
            "nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. "
            "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu "
            "fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in "
            "culpa qui officia deserunt mollit anim id est laborum.",
            pg.Color(16, 16, 16)
            )

    def update(self):
        self.boxed_text.update()

    def draw(self, surf):
        self.image.fill(pg.Color(241, 38, 192))
        self.image.blit(self.boxed_text.image, self.boxed_text.rect)
        surf.blit(self.image, self.rect, self.clip)
