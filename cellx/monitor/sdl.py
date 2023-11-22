#!/usr/bin/env python3
#
#
# Copyright (c) 2018-2023, Hiroyuki Ohsaki.
# All rights reserved.
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

import contextlib
import math

# Discard messages when loading pygame modules.
with contextlib.redirect_stdout(None):
    import pygame
    import pygame.gfxdraw
    import pygame.transform

import cellx
from cellx.monitor.null import Null
from perlcompat import warn

class SDL(Null):
    def __init__(self, alpha=255, *kargs, **kwargs):
        """Initialize the graphics context with default settings.  This
        constructor initializes an instance of the graphics context with default
        settings. It sets various attributes and flags, such as 'pause', 'font_cache',
        'rendered', and 'enable_sound', and then calls the 'init' method to
        perform additional initialization."""
        super().__init__(*kargs, **kwargs)
        self.alpha = alpha
        self.pause = False
        self.font_cache = {}
        self.rendered = {}
        self.enable_sound = False
        self.init()

    def init(self):
        """Initialize the graphics context and associated resources.  This
        method performs the initialization of the graphics context, including
        initializing the display, font system, and optionally sound. It sets
        up the screen, fixed surface, and sound system (if available). If
        sound initialization fails, it continues without enabling sound."""
        pygame.display.init()
        pygame.font.init()
        width, height = self.width, self.height
        self.hwscreen = pygame.display.set_mode((width, height))
        self.fixed_surface = pygame.Surface((width, height), 0, self.hwscreen)
        self.current_frame = pygame.Surface((width, height), 0, self.hwscreen)
        self.current_frame.set_alpha(self.alpha)
        try:
            pygame.mixer.init()
            self.enable_sound = True
        except pygame.error:
            warn(
                'failed to initialize sound mixer.  continue without sound...')

    def draw_line(self, sx, sy, dx, dy, width, color, alpha):
        """Draw a filled line segment between two points with specified
        attributes.  This method draws a filled line segment between the
        starting point (SX, SY) and the destination point (DX, DY) with the
        specified line WIDTH, COLOR, and ALPHA transparency. The line is drawn
        with triangles to fill the area between the line segments, creating a
        solid appearance."""
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
        """Render a bitmap (image) object with specified attributes.  This
        method renders a bitmap (image) object with the specified file, width,
        height, x-coordinate, and y-coordinate.  It first checks if the bitmap
        has been cached, and if not, it loads the image from the file and
        caches it for future use. If the bitmap dimensions do not match the
        specified width and height, it resizes the image while maintaining its
        aspect ratio. Finally, it blits (draws) the image onto the screen."""
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
        # Resize the image if required.
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
        """Render a filled box (rectangle) object with specified attributes.
        This method renders a filled box (rectangle) object with the specified
        center coordinates, width, height, color, alpha transparency, and
        optional frame color. The box is drawn using Pygame's 'Rect' and
        'gfxdraw' functions."""
        x, y = obj.x, obj.y
        rect = pygame.Rect(x - obj.width / 2, y - obj.height / 2, obj.width,
                           obj.height)
        color = self.palette.rgba(obj.color, obj.alpha)
        pygame.gfxdraw.box(self.screen, rect, color)
        if obj.frame_color:
            color = self.palette.rgba(obj.frame_color, obj.alpha)
            pygame.gfxdraw.rectangle(self.screen, rect, color)

    def _render_ellipse(self, obj):
        """Render a filled ellipse object with specified attributes.  This
        method renders a filled ellipse object with the specified center
        coordinates, width, height, color, and alpha transparency. The ellipse
        is drawn using Pygame's 'gfxdraw.filled_ellipse' function."""
        color = self.palette.rgba(obj.color, obj.alpha)
        rx, ry = int(obj.width / 2), int(obj.height / 2)
        pygame.gfxdraw.filled_ellipse(self.screen, int(obj.x), int(obj.y), rx,
                                      ry, color)

    def _render_spline(self, obj):
        """Render a cubic Bezier spline curve with specified attributes.  This
        method renders a cubic Bezier spline curve with the specified control
        points and attributes, including color and alpha transparency. The
        curve is drawn using Pygame's 'gfxdraw.bezier' function."""
        p1 = obj.x, obj.y
        p2 = obj.x2, obj.y2
        p3 = obj.x3, obj.y3
        # FIXME: Implement line width.
        pygame.gfxdraw.bezier(self.screen, [p1, p2, p3], 20,
                              self.palette.rgba(obj.color, obj.alpha))

    def _render_polygon(self, obj):
        """Render a filled polygon with specified attributes.  This method
        renders a filled polygon with the specified vertices, color, and alpha
        transparency. The polygon is drawn using Pygame's
        'gfxdraw.filled_polygon' function."""
        vertices = obj.vertices()
        color = self.palette.rgba(obj.color, obj.alpha)
        pygame.gfxdraw.filled_polygon(self.screen, vertices, color)

    def _render_text(self, obj):
        """Render text with specified attributes.  This method renders text
        with the specified content, size, color, alignment, and alpha
        transparency. It caches rendered text lines for efficiency and
        calculates the dimensions of the text block. The rendered text is then
        positioned and aligned according to the specified attributes."""
        if not obj._text_cache:
            if not self.font_cache.get(obj.size, None):
                font = pygame.font.SysFont('Helvetica', obj.size)
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
            # Center by default.
            xpos = obj.x - obj.width / 2 + (obj.width - text.get_width()) / 2
            if obj.align == 'left':
                xpos = obj.x
            elif obj.align == 'right':
                xpos = obj.x - text.get_width()
            self.screen.blit(text, (xpos, ypos))
            ypos += text.get_height()

    def render_objects(self, objs):
        """Render a list of objects, both fixed and non-fixed.  This method
        renders a list of objects, iterating through the provided 'objs'
        list. It first renders fixed but not-yet-rendered objects, then resets
        the surface to the pre-rendered state. After that, it renders
        non-fixed objects. Rendering is based on the object's type-specific
        rendering method."""
        # Render fixed but not-rendered objects.
        self.screen = self.fixed_surface
        for obj in objs:
            if obj.fixed and not self.rendered.get(obj, None):
                self.render(obj)
                self.rendered[obj] = True

        # Reset to pre-rendered suface.
        self.current_frame.blit(self.fixed_surface, (0, 0))

        # Render non-fixed objects.
        self.screen = self.current_frame
        for obj in objs:
            if not obj.fixed:
                self.render(obj)

        self.hwscreen.blit(self.current_frame, (0, 0))

    def process_events(self):
        """Process pygame events in an infinite loop until explicitly
        exited. This method continuously polls for pygame events and handles
        them accordingly."""
        while True:
            event = pygame.event.poll()
            if event.type == pygame.NOEVENT:
                if not self.pause:
                    return
                else:
                    continue
            if event.type == pygame.KEYDOWN:
                key = event.key
                if key == pygame.K_q or key == pygame.K_ESCAPE:
                    exit()
                if key == pygame.K_SPACE:
                    self.pause = not self.pause
            if event.type == pygame.VIDEOEXPOSE:
                pygame.display.update()

    def display(self):
        pygame.display.update()
        self.process_events()

    def wait(self):
        self.pause = True
        self.process_events()

    def play(self, file):
        """Play a sound file if sound mixer is enabled.  This method plays a
        sound file using Pygame's sound mixer if sound is enabled. If the
        sound mixer is disabled, it issues a warning and does not play the
        sound."""
        if not self.enable_sound:
            warn(
                "cannot play '{}' since sound mixer is disabled.".format(file))
            return
        sound = pygame.mixer.Sound(file)
        sound.play()
