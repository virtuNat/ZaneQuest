import os
import re
import pygame as pg
from common import (ClipDrawSprite)

class ScrollableText(pg.sprite.Sprite):
    """A text surface that can animate scrolling."""
    __slots__ = ('image', 'rect', 'font', 'color', '_textgen', 'done')

    def __init__(self, surf, pos, font, text, color, scroll):
        super().__init__()
        self.image = surf
        self.rect = pg.Rect(pos, font.size(text))
        self.font = font
        self.color = color
        if scroll == 0:
            self.image.blit(self.font.render(text, True, color), pos)
            self._textgen = None
            self.done = True
        else:
            self._textgen = (text[:i+1] for i in range(len(text)) if text[i] != ' ')
            self.done = False

    def update(self):
        if not self.done:
            try:
                text = next(self._textgen)
            except StopIteration:
                self.done = True
            else:
                self.image.fill(pg.Color(0, 0, 0, 0), self.rect)
                self.image.blit(
                    self.font.render(text, True, self.color),
                    self.rect,
                    )


class TextBox(pg.sprite.Sprite):
    """Generic Textbox"""

    def __init__(self, bounds, bgsprite, textrect, font, scroll=0):
        super().__init__()
        self.bounds = bounds
        self.bgsprite = bgsprite
        self.textimage = pg.Surface(textrect.size, pg.SRCALPHA, 32)
        self.textrect = textrect
        self.font = font
        self.scroll = scroll
        self._lines = []
        self._frame = 0

    def set_text(self, text, color):
        words = re.findall(r'\S+\s*', text)
        lines = [words[0]]
        for word in words[1:]:
            if self.font.size(lines[-1]+word)[0] > self.textrect.w:
                lines.append(word)
            else:
                lines[-1] += word
        self._lines = [
            ScrollableText(
                self.textimage, (0, idx * self.font.get_linesize()),
                self.font, line, color, self.scroll,
                )
            for idx, line in enumerate(lines)
            ]

    def update(self):
        self.bgsprite.update()
        if self.scroll > 0 and self._frame == 0:
            for line in self._lines:
                if not line.done:
                    line.update()
                    break
        self._frame = (self._frame + 1) % self.scroll

    def draw(self, surf):
        self.bgsprite.image.blit(self.textimage, self.textrect)
        self.bgsprite.draw(surf)


class SampleTextBox(TextBox):
    """Sample test textbox"""

    def __init__(self, bounds):
        super().__init__(
            bounds,
            ClipDrawSprite(pg.Surface((900, 200), pg.SRCALPHA, 32)),
            pg.Rect(25, 30, 850, 170),
            pg.font.Font(os.path.join('assets', 'fonts', 'DejaVuSans.ttf'), 20),
            2,
            )
        self.bgsprite.rect.midbottom = bounds.midbottom
        self.set_text(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor "
            "incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis "
            "nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. "
            "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu "
            "fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in "
            "culpa qui officia deserunt mollit anim id est laborum.",
            pg.Color(252, 61, 57),
            )

    def draw(self, surf):
        self.bgsprite.image.fill(pg.Color(49, 39, 63))
        super().draw(surf)


class ZaneBox(TextBox):
    """Main textbox at the bottom of scenes and the overworld."""

    def __init__(self):
        pass
