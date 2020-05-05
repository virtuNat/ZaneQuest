#!/usr/bin/env python
import os
from time import time
import pygame as pg
# import asyncio as aio
from common import (GameState, Singleton)
from objects import (ZaneBox)

__version__ = (0, 1, 0)

key_config = {
    'U': pg.K_UP,
    'D': pg.K_DOWN,
    'L': pg.K_LEFT,
    'R': pg.K_RIGHT,
    'A': pg.K_z,
    'B': pg.K_x,
    'Start': pg.K_ESCAPE,
    'Select': pg.K_RETURN,
    }

class Scene(GameState):

    def __init__(self, handler):
        super().__init__(handler)
        self.zanebox = ZaneBox(self.bounds)
        self.start = False

    def eval_logic(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.handler.running = False
            elif event.type == pg.KEYDOWN:
                try:
                    self.zanebox.send(key_config[event.key])
                except KeyError:
                    pass
            elif event.type == pg.KEYUP:
                pass
        self.zanebox.update()

    def draw_frame(self):
        self.window.fill(pg.Color(213, 210, 219))
        self.zanebox.draw(self.window)
        pg.display.flip()


class GameApplication(Singleton):
    """Handles the game, self-explanatory."""

    def __init__(self):
        self.window = pg.display.get_surface()
        self.rect = self.window.get_rect()
        self.state = Scene(self)
        self.running = True

        key_config.update({v: k for k, v in key_config.items()})

    def run(self, fps):
        clock = pg.time.Clock()
        self.fps = f'{fps:02d}'
        while self.running:
            self.state.eval_logic()
            self.state.draw_frame()
            clock.tick(fps)
            self.fps = str(clock.get_fps())

    # async def run(self, fps):
    #     self.fps = f'{fps:02d}'
    #     frame = aio.ensure_future(self.state.draw_frame())
    #     frate = 1 / fps
    #     ptime = ftime = time()
    #     count = 0
    #     while self.running:
    #         await self.state.eval_logic()
    #         await aio.sleep(max(0, frate - (time() - ptime)))
    #         ptime = time()
    #         count = (count + 1) % fps
    #         if not count:
    #             self.fps = f'{fps / (time() - ftime):02.0f}'
    #             ftime = time()
    #         if frame.done():
    #             frame = aio.ensure_future(self.state.draw_frame())


def main():
    pg.init()
    pg.display.set_caption('ZaneQuest 2020')
    pg.display.set_icon(pg.image.load(os.path.join('assets', 'textures', 'icon.png')))
    pg.display.set_mode((1024, 768), pg.ASYNCBLIT | pg.HWSURFACE | pg.DOUBLEBUF)
    GameApplication().run(60)
    # aio.run(GameApplication().run(40))
    pg.quit()

if __name__ == '__main__':
    main()
