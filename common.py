import os
import pygame as pg
import asyncio as aio

def load_image(name, *, alpha=None, colorkey=None):
    """Load an image file into memory."""
    try:
        image = pg.image.load(os.path.join('assets', 'textures', name))
    except pg.error:
        print('Image loading failed: ')
        raise
    if alpha is None:
        image = image.convert()
        if colorkey is not None:
            image.set_colorkey(colorkey)
        return image
    return image.convert_alpha()

def load_sound(name):
    return pg.mixer.Sound(os.path.join('assets', 'sounds', name))


class Singleton(object):
    """Objects that can have at most exactly one instance."""
    __slots__ = ()
    instances = {}

    def __new__(cls, *args):
        try:
            return Singleton.instances[cls]
        except KeyError:
            instance = super().__new__(cls)
            Singleton.instances[cls] = instance
            return instance


class ClipDrawSprite(pg.sprite.Sprite):
    """Sprites that use a clip rectangle to designate its tile in an atlas."""
    __slots__ = ('image', 'rect', 'clip')

    def __init__(self, image=None, rect=None, clip=None):
        super().__init__()
        self.image = image
        if image is not None and rect is None:
            self.rect = self.image.get_rect()
        else:
            self.rect = pg.Rect(rect)
        if self.rect is not None and clip is None:
            self.clip = self.rect.copy()
            self.clip.topleft = (0, 0)
        else:
            self.clip = pg.Rect(clip)

    def draw(self, surf, offx=0, offy=0):
        surf.blit(self.image, self.rect.move(-offx, -offy), self.clip)


class TileSprite(ClipDrawSprite):
    __slots__ = ()
    sheet = None


class ClipDrawGroup(pg.sprite.OrderedUpdates):
    """Group that accomodates atlas based sprites."""

    def draw(self, surf):
        """Draw all the sprites while taking into account their clip rects."""
        blitfunc = surf.blit
        for sprite in self.sprites():
            blitfunc(sprite.image, sprite.rect, sprite.clip)


class GameState(Singleton):

    def __init__(self, handler):
        self.handler = handler
        self.window = pg.display.get_surface()
        self.bounds = self.window.get_rect()

    async def eval_logic(self):
        raise NotImplementedError('override logic handler')

    async def draw_frame(self):
        raise NotImplementedError('override display handler')
