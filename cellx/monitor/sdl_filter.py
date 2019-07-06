#!/usr/bin/env python3
#
#
# Copyright (c) 2018, Hiroyuki Ohsaki.
# All rights reserved.
#
# $Id: sdl_filter.py,v 1.2 2019/03/10 11:50:05 ohsaki Exp ohsaki $
#

import math
import pygame
import pygame.gfxdraw
import pygame.transform

import cellx
from cellx.monitor.sdl import SDL

class SDL_Filter(SDL):
    def __init__(self):
        super().__init__()
        self.alpha = 40

        width, height = self.width, self.height
        self.current_frame = pygame.Surface((width, height), 0, self.hwscreen)
        self.current_frame.set_alpha(self.alpha)

    def render_objects(self, objs):
        # render fixed but not-rendered objects
        self.screen = self.fixed_surface
        for obj in objs:
            if obj.fixed and not self.rendered.get(obj, None):
                self.render(obj)
                self.rendered[obj] = True

        # reset to pre-rendered suface
        self.current_frame.blit(self.fixed_surface, (0, 0))

        # render non-fixed objects
        self.screen = self.current_frame
        for obj in objs:
            if not obj.fixed:
                self.render(obj)

        self.hwscreen.blit(self.current_frame, (0, 0))
