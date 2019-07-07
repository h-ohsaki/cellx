#!/usr/bin/env python3
#
#
# Copyright (c) 2018, Hiroyuki Ohsaki.
# All rights reserved.
#
# $Id: sdl.py,v 1.9 2019/07/06 16:11:41 ohsaki Exp ohsaki $
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
from cellx.monitor.null import Null

class SDL(Null):
    def __init__(self, *kargs, **kwargs):
        super().__init__(*kargs, **kwargs)
        self.font_cache = {}
        self.rendered = {}
        self.init()

    def init(self):
        pygame.display.init()
        pygame.font.init()
        width, height = self.width, self.height
        self.hwscreen = pygame.display.set_mode((width, height))
        self.fixed_surface = pygame.Surface((width, height), 0, self.hwscreen)
        pygame.mixer.init()

    def draw_line(self, sx, sy, dx, dy, width, color, alpha):
        theta = math.atan2(dy - sy, dx - sx)
        xx = width / 2 * math.cos(math.pi / 2 + theta)
        yy = width / 2 * math.sin(math.pi / 2 + theta)
        color = self.palette.rgba(color, alpha)
        pygame.gfxdraw.filled_trigon(self.screen, int(sx + xx), int(sy + yy),
                                     int(sx - xx), int(sy - yy), int(dx + xx),
                                     int(dy + yy), color)
        pygame.gfxdraw.filled_trigon(self.screen, int(dx + xx), int(dy + yy),
                                     int(dx - xx), int(dy - yy), int(sx - xx),
                                     int(sy - yy), color)

    def _render_bitmap(self, obj):
        if not obj._bitmap_cache:
            file = obj.file
            img = pygame.image.load_extended(file)
            if not img:
                cellx.die('pygame.image.load_extended(%s) failed.', file)
            obj._bitmap_cache = img
            if obj.width is None:
                obj.width = img.get_width()
            if obj.height is None:
                obj.height = img.get_height()

        img = obj._bitmap_cache
        # resize the image if required
        if obj.width != img.get_width() or obj.height != img.get_height():
            zoom_x = obj.width / img.get_width()
            zoom_y = obj.height / img.get_height()
            zoom = min(zoom_x, zoom_y)
            img = pygame.transform.rotozoom(img, 0, zoom)
            obj.width = img.get_width()
            obj.height = img.get_height()

        x = obj.x - obj.width / 2
        y = obj.y - obj.height / 2
        self.screen.blit(img, (x, y))

    def _render_box(self, obj):
        x, y = obj.x, obj.y
        rect = pygame.Rect(x - obj.width / 2, y - obj.height / 2, obj.width,
                           obj.height)
        color = self.palette.rgba(obj.color, obj.alpha)
        pygame.gfxdraw.box(self.screen, rect, color)

    def _render_ellipse(self, obj):
        color = self.palette.rgba(obj.color, obj.alpha)
        rx, ry = int(obj.width / 2), int(obj.height / 2)
        pygame.gfxdraw.filled_ellipse(self.screen, int(obj.x), int(obj.y), rx,
                                      ry, color)

    def _render_line(self, obj):
        self.draw_line(obj.x, obj.y, obj.x2, obj.y2, obj.width, obj.color,
                       obj.alpha)

    def _render_link(self, obj):
        src, dst = obj.src, obj.dst
        self.draw_line(src.x, src.y, dst.x, dst.y, obj.width, obj.color,
                       obj.alpha)

    def _render_spline(self, obj):
        p1 = obj.x, obj.y
        p2 = obj.x2, obj.y2
        p3 = obj.x3, obj.y3
        # FIXME: implement line width
        pygame.gfxdraw.bezier(self.screen, [p1, p2, p3], 20,
                              self.palette.rgba(obj.color, obj.alpha))

    def _render_polygon(self, obj):
        vertices = obj.vertices()
        color = self.palette.rgba(obj.color, obj.alpha)
        pygame.gfxdraw.filled_polygon(self.screen, vertices, color)

    def _render_text(self, obj):
        if not obj._text_cache:
            if not self.font_cache.get(obj.size, None):
                font = pygame.font.Font(
                    '/etc/alternatives/fonts-japanese-gothic.ttf', obj.size)
                if not font:
                    cellx.die('pygame.font.SysFont() failed.')
                self.font_cache[obj.size] = font

            font = self.font_cache[obj.size]
            width, height = 0, 0
            color = self.palette.rgba('white')
            for line in obj.text.split('\\\\'):
                text = font.render(line, 1, color)
                obj._text_cache.append(text)
                width = max(width, text.get_width())
                height += text.get_height()
            obj.width = width
            obj.height = height

        ypos = obj.y - obj.height / 2
        for text in obj._text_cache:
            # center by default
            xpos = obj.x - obj.width / 2 + (obj.width - text.get_width()) / 2
            if obj.align == 'left':
                xpos = obj.x
            elif obj.align == 'right':
                xpos = obj.x - text.get_width()
            self.screen.blit(text, (xpos, ypos))
            ypos += text.get_height()

    def _render_wire(self, obj):
        x, y = obj.x, obj.y
        x2, y2 = obj.x2, obj.y2
        # slightly extend the line length to draw smooth corners
        xsign = cellx.cmp(x2 - x, 0)
        ysign = cellx.cmp(y2 - y, 0)
        delta = obj.width / 2
        xmid = (x + x2) / 2
        segments = [[x, y, xmid + xsign * delta, y], \
            [xmid, y - ysign * delta, xmid, y2 + ysign * delta], \
            [xmid - xsign * delta, y2, x2, y2]]
        for segment in segments:
            self.draw_line(*segment, obj.width, obj.color, obj.alpha)

    def render(self, obj):
        type = obj.type_
        if type == 'bitmap':
            self._render_bitmap(obj)
        elif type == 'box':
            self._render_box(obj)
        elif type == 'ellipse':
            self._render_ellipse(obj)
        elif type == 'line':
            self._render_line(obj)
        elif type == 'link':
            self._render_link(obj)
        elif type == 'polygon':
            self._render_polygon(obj)
        elif type == 'spline':
            self._render_spline(obj)
        elif type == 'text':
            self._render_text(obj)
        elif type == 'wire':
            self._render_wire(obj)

    def render_objects(self, objs):
        # render fixed but not-rendered objects
        self.screen = self.fixed_surface
        for obj in objs:
            if obj.fixed and not self.rendered.get(obj, None):
                self.render(obj)
                self.rendered[obj] = True

        # reset to pre-rendered suface
        self.hwscreen.blit(self.fixed_surface, (0, 0))

        # render non-fixed objects
        self.screen = self.hwscreen
        for obj in objs:
            if not obj.fixed:
                self.render(obj)

    def display(self):
        pygame.display.update()

    def wait(self):
        while True:
            event = pygame.event.wait()
            if event.type == pygame.KEYDOWN:
                key = event.key
                if key == pygame.K_SPACE:
                    break
                if key == pygame.K_q:
                    exit()

    def play(self, file):
        sound = pygame.mixer.Sound(file)
        sound.play()
