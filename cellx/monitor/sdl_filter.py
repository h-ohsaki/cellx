#!/usr/bin/env python3
#
#
# Copyright (c) 2018-2019, Hiroyuki Ohsaki.
# All rights reserved.
#
# $Id: sdl_filter.py,v 1.2 2019/03/10 11:50:05 ohsaki Exp ohsaki $
#

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import math
import pygame
import pygame.gfxdraw
import pygame.transform

import cellx
from cellx.monitor.sdl import SDL

class SDL_Filter(SDL):
    def __init__(self, alpha=40, *kargs, **kwargs):
        super().__init__()
        self.alpha = alpha

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
