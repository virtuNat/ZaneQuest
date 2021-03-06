import os
import re
from itertools import cycle, chain
import pygame as pg
from common import (load_image, Singleton, ClipDrawSprite)

class ScrollableText(pg.sprite.Sprite):
    """A text surface that can animate scrolling."""
    __slots__ = ('image', 'rect', 'font', 'color', 'text', '_textgen', 'done')

    def __init__(self, surf, pos, font, text, color, scroll):
        super().__init__()
        self.image = surf
        self.rect = pg.Rect(pos, font.size(text))
        self.font = font
        self.color = color
        self.text = text
        if scroll == 0:
            self.image.blit(self.font.render(text, True, color), pos)
            self._textgen = None
            self.done = True
        else:
            self._textgen = (text[:i+1] for i in range(len(text)) if text[i] != ' ')
            self.done = False

    def interrupt(self):
        if self._textgen is not None:
            self._textgen = iter((self.text,))

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
        self.done = scroll == 0
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

    def set_textframes(self, arglist):
        self._textframes = (self.set_text(*arg) for arg in arglist)

    def send(self, signal):
        pass

    def interrupt(self):
        for line in self._lines:
            line.interrupt()

    def update(self):
        if not self.done:
            if self._frame == 0:
                for line in self._lines:
                    if not line.done:
                        line.update()
                        break
                else:
                    self.done = True
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

    def update(self):
        self.bgsprite.update()
        super().update()

    def draw(self, surf):
        self.bgsprite.image.fill(pg.Color(49, 39, 63))
        super().draw(surf)


class ZaneBoxBG(Singleton, ClipDrawSprite):
    emotemap = {
        'IDLE': 0,
        }

    def __init__(self, bounds):
        super().__init__(rect=pg.Rect(0, 0, 220, 220))
        self.image = pg.Surface(self.rect.size, pg.SRCALPHA, 32)
        self.bounds = bounds
        self.atlas = load_image('zanemotes.png', alpha=True)
        self.mask = load_image('zaneboxmask.png')
        self.set_emote('IDLE')

    def set_emote(self, emote):
        self.clip.x = self.emotemap[emote] * self.clip.w
        self.image.fill(pg.Color(0, 0, 0, 0))
        self.image.blit(self.atlas, (0, 0), self.clip)
        pg.transform.threshold(self.image, self.mask, pg.Color(0, 255, 0, 255), inverse_set=True)


class NextArrow(ClipDrawSprite):
    """The arrow that indicates you can proceed to the next text frame."""
    adisp = (0,)*10 + (1, 2, 4, 8, 16, 8, 4, 2, 1) + (0,)*11

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visible = False
        self._anchor = self.rect.x
        self._frame = False
        self._adisp = None

    def set_visible(self, visible):
        if visible == self.visible:
            return
        if visible:
            self._frame = False
            self._adisp = cycle(self.adisp)
        self.visible = visible

    def update(self):
        if self.visible:
            if self._frame:
                self.rect.x = self._anchor + next(self._adisp)
            self._frame = not self._frame


class ZaneBox(Singleton, TextBox):
    """Main textbox at the bottom of scenes and the overworld."""
    avel = (1, 3, 6, 10, 15, 21, 54, 54, 21, 15, 10, 6, 3, 1)

    def __init__(self, bounds):
        self.atlas = load_image('zanebox.png', alpha=True)
        super().__init__(
            bounds,
            ZaneBoxBG(bounds),
            pg.Rect(235, 48, 605, 147),
            pg.font.Font(os.path.join('assets', 'fonts', 'DejaVuSans.ttf'), 23),
            1,
            )
        self.arrow = NextArrow(
            self.atlas,
            pg.Rect(840, 160, 26, 45),
            pg.Rect(874, 220, 26, 45),
            )
        self.set_textframes(((
            "Did you fucking know that Chuck E. Cheese isn't actually made of cheese? "
            "Funniest shit I've ever seen in my life. Better than that pickle shit.",
            pg.Color(10, 10, 10),
            ), (
            "What, did you honestly really fucking think that? Wow, you're such a goddamn "
            "loser. Clearly you walk around claiming to have a high enough IQ to understand "
            "\"intellectual\" shows, huh? Creep.",
            pg.Color(10, 10, 10),
            ),))
        self.image = pg.Surface((900, 220), pg.SRCALPHA, 32)
        self.rect = self.image.get_rect()
        self.rect.midtop = bounds.midbottom

        self.astate = 0 # 0: Idle, 1: Up, 2: Down, 3: Scroll
        self._adisp = iter(self.avel)

    def queue_next(self):
        try:
            next(self._textframes)
        except StopIteration:
            self.astate = 2
        else:
            self.textimage.fill(pg.Color(0, 0, 0, 0))
            self.arrow.set_visible(False)
            self.done = False

    def send(self, signal):
        if signal == 'A':
            if self.astate == 0:
                self.astate = 1
                next(self._textframes)
            elif self.astate == 3:
                if not self.done:
                    self.interrupt()
                else:
                    self.queue_next()
        elif signal == 'B':
            if self.astate == 3:
                self.queue_next()

    def update(self):
        if self.astate == 3:
            super().update()
            if self.done:
                self.arrow.set_visible(True)
            self.arrow.update()
        else:
            try:
                if self.astate == 1:
                    self.rect.y -= next(self._adisp)
                elif self.astate == 2:
                    self.rect.y += next(self._adisp)
            except StopIteration:
                self.astate = (3, 0)[self.astate-1]
                self._adisp = iter(self.avel)

    def draw(self, surf):
        self.bgsprite.draw(self.image)
        self.image.blit(self.atlas, (0, 0))
        self.image.blit(self.textimage, self.textrect)
        if self.arrow.visible:
            self.arrow.draw(self.image)
        surf.blit(self.image, self.rect)
