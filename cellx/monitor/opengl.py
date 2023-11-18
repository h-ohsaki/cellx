#!/usr/bin/env python3
#
#
# Copyright (c) 2023, Hiroyuki Ohsaki.
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

# FIXME: Support text rendering.
# FIXME: Support polygon rendering.
# FIXME: Support spline rendering.
# FIXME: Support fixed objects.

import math

from cellx.monitor.sdl import SDL
import OpenGL.GL as gl
import OpenGL.GLUT as glut
import pygame

class OpenGL(SDL):
    def __init__(self, *kargs, **kwargs):
        # View port settings.
        self.xoffset = 0.
        self.yoffset = 0.
        self.zoom = 1.
        self.rot_x = 0.
        self.rot_y = 0.
        self.rot_z = 0.

        self.last_button = None
        self.fixed_list = None
        super().__init__(*kargs, **kwargs)
        self.font_bitmap = self.load_font()

    def init(self):
        super().init()
        # Re-initialize display with OpenGL support.
        width, height = self.width, self.height
        self.hwscreen = pygame.display.set_mode(
            (width, height), pygame.OPENGL | pygame.DOUBLEBUF)
        glut.glutInit()
        gl.glShadeModel(gl.GL_SMOOTH)
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)

        # Enable alpha-blending.
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        # Enable lighting.
        gl.glEnable(gl.GL_LIGHTING)
        gl.glEnable(gl.GL_LIGHT0)
        gl.glDepthFunc(gl.GL_LESS)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_NORMALIZE)
        gl.glEnable(gl.GL_COLOR_MATERIAL)

        # Configure lights.
        gl.glMaterial(gl.GL_FRONT, gl.GL_AMBIENT, (.8, .0, .2, 1.))
        gl.glMaterial(gl.GL_FRONT, gl.GL_DIFFUSE, (1., 1., 1., 1.))
        gl.glMaterial(gl.GL_FRONT, gl.GL_SPECULAR, (.4, .4, .4, 1.))
        gl.glMaterialf(gl.GL_FRONT, gl.GL_SHININESS, 80)

        gl.glLight(gl.GL_LIGHT0, gl.GL_POSITION, (-100, 100, 100, 0))
        gl.glLight(gl.GL_LIGHT0, gl.GL_AMBIENT, (.1, .1, .1, 1))
        gl.glLight(gl.GL_LIGHT0, gl.GL_DIFFUSE, (.7, .7, .7, 1))
        gl.glLight(gl.GL_LIGHT0, gl.GL_SPECULAR, (1, 1, 1, 1))

    def normalize_position(self, x, y):
        """Normalize a 2D position (x, y) relative to the center of the
        screen."""
        return (x - self.width /
                2) / self.width, -(y - self.height / 2) / self.height

    def normalize_size(self, l):
        """Normalize a size (length) L relative to the screen width. """
        # Force the minimum size to be one pixel.
        return max(1/self.width, l / self.width)

    def relative_position(self, x, y):
        """Calculate the relative position of a point (x, y) on the screen."""
        return x / self.width, y / self.height

    def load_font(self):
        """Load a bitmap font from a file and return it as a list of 8x8 pixel
        character representations."""
        BITMAP_FONT = '/home/ohsaki/lib/fonts/8x8maru.fnt'
        with open(BITMAP_FONT, 'rb') as f:
            font_data = f.read()
        # Split font data per 8 bytes.
        # FIXME: should not hard-code font size
        # FIXME: support Kanji characters
        return [font_data[i:i + 8][::-1] for i in range(0, len(font_data), 8)]

    def draw_line(self, sx, sy, dx, dy, width, color, alpha, use_line=False):
        """Draw a line or a square rod between two points with specified
        attributes.  This function allows drawing either a line segment or a
        square rod connecting two points in a graphical context.  The
        appearance of the drawn object can be customized with options such as
        WIDTH, COLOR, and ALPHA transparency."""
        if sx > dx:
            sx, sy, dx, dy = dx, dy, sx, sy
        sx, sy = self.normalize_position(sx, sy)
        dx, dy = self.normalize_position(dx, dy)
        w = self.normalize_size(width)
        color = self.palette.rgba(color, alpha)
        gl.glColor4ub(*color)
        if use_line:
            # Draw a line segment between (SX, SY) and (DX, DY).
            gl.glLineWidth(w)
            gl.glBegin(gl.GL_LINES)
            gl.glVertex2d(sx, sy)
            gl.glVertex2d(dx, dy)
            gl.glEnd()
            return

        # Place a square rod connecting (SX, SY) and (DX, DY).
        # This code assumes SX is smaller than DX.
        gl.glPushMatrix()
        gl.glTranslatef(sx, sy, 0)
        angle = math.degrees(math.atan2(dy - sy, dx - sx))
        gl.glRotatef(angle, 0, 0, 1)
        l = math.sqrt((dx - sx)**2 + (dy - sy)**2)
        gl.glScalef(l, w, w)
        gl.glTranslatef(.5, 0, 0)
        glut.glutSolidCube(1)
        gl.glPopMatrix()

    def draw_ellipse(self, x, y, r, color, alpha):
        """Draw an ellipse at a specified position with given attributes.
        This function draws an ellipse at the specified (X, Y) position with a
        given radius R. The appearance of the ellipse can be customized with
        options such as COLOR and ALPHA transparency."""
        x, y = self.normalize_position(x, y)
        r = self.normalize_size(r)
        color = self.palette.rgba(color, alpha)
        gl.glColor4ub(*color)
        gl.glBegin(gl.GL_POLYGON)
        # Draw the ellipse with 20 segments.
        for degree in range(0, 360, 360 // 20):
            radians = math.radians(degree)
            x1, y1 = x + r * math.cos(radians), y + r * math.sin(radians)
            gl.glVertex2d(x1, y1)
        gl.glEnd()

    def _render_bitmap(self, obj):
        raise NotImplementedError

    def _render_box(self, obj):
        """Render a 3D box object OBJ with specified attributes.  This
        function renders a 3D box at the position (x, y) with dimensions
        (width, height) and a priority level. The appearance of the box can be
        customized with options such as COLOR and ALPHA transparency."""
        x, y = self.normalize_position(obj.x, obj.y)
        w, h = self.normalize_size(obj.width), self.normalize_size(obj.height)
        z = self.normalize_size(obj.priority)
        color = self.palette.rgba(obj.color, obj.alpha)
        gl.glColor4ub(*color)
        gl.glPushMatrix()
        gl.glTranslatef(x, y, z)
        gl.glScalef(w, h, (w + h) / 2)
        glut.glutSolidCube(1)
        gl.glPopMatrix()

    def _render_ellipse(self, obj, use_polygon=False):
        """Render an ellipse object with specified attributes.  This function
        renders an ellipse at the position (x, y) with a specified width and
        priority level. The appearance of the ellipse can be customized with
        options such as color and alpha transparency. The ellipse can be
        rendered as either a polygon or a solid sphere in 3D space."""
        if use_polygon:
            self.draw_ellipse(obj.x, obj.y, obj.width / 2, obj.color,
                              obj.alpha)
            return

        x, y = self.normalize_position(obj.x, obj.y)
        z = self.normalize_size(obj.priority)
        r = self.normalize_size(obj.width / 2)
        color = self.palette.rgba(obj.color, obj.alpha)
        gl.glColor4ub(*color)
        gl.glPushMatrix()
        gl.glTranslatef(x, y, z)
        glut.glutSolidSphere(r, 20, 20)
        gl.glPopMatrix()

    def _render_polygon(self, obj):
        """Render a filled polygon object OBJ with specified attributes.  This
        function renders a filled polygon using the specified vertices, color,
        and alpha transparency. The appearance of the polygon can be
        customized with options such as color and alpha transparency."""
        vertices = obj.vertices()
        color = self.palette.rgba(obj.color, obj.alpha)
        gl.glColor4ub(*color)
        gl.glBegin(gl.GL_POLYGON)
        for v in vertices:
            x, y = self.normalize_position(*v)
            gl.glVertex2d(x, y)
        gl.glEnd()

    def _render_spline(self, obj):
        """Render a spline (curve) object OBJ with specified attributes. This
        function is intended to render a spline, but it currently renders a
        sequence of connected line segments between control points. The
        appearance of the spline can be customized with options such as color,
        alpha transparency, width, and control points."""
        x, y = self.normalize_position(obj.x, obj.y)
        x2, y2 = self.normalize_position(obj.x2, obj.y2)
        x3, y3 = self.normalize_position(obj.x3, obj.y3)
        w = self.normalize_size(obj.width)
        color = self.palette.rgba(obj.color, obj.alpha)
        # FIXME: Spline is not implemented.
        gl.glLineWidth(w)
        gl.glColor4ub(*color)
        # FIXME: Rewrite with glMatrix1fv.
        gl.glBegin(gl.GL_LINE_STRIP)
        gl.glVertex2d(x, y)
        gl.glVertex2d(x2, y2)
        gl.glVertex2d(x3, y3)
        gl.glEnd()

    def _render_text(self, obj):
        """Render text with specified attributes.  This function renders text
        at the specified (x, y) position with the provided text string, color,
        and alpha transparency. The appearance of the text can be customized
        with options such as color and alpha transparency.  Currently, it uses
        a fixed-size font and aligns the text to the left."""
        # FIXME: Support scalable fonts.
        # FIXME: Align text (e.g., centerling).
        x, y = self.normalize_position(obj.x, obj.y)
        w = self.normalize_size(8 * len(obj.text))
        color = self.palette.rgba(obj.color, obj.alpha)
        gl.glColor4ub(*color)
        gl.glPushMatrix()
        gl.glRasterPos3f(x - w / 2, y, .001)
        for c in obj.text:
            gl.glBitmap(8, 8, 0, 0, 8, 0, self.font_bitmap[ord(c)])
        gl.glPopMatrix()

    def render_objects(self, objs):
        """Render a list of objects with specified rendering attributes.  This
        function takes a list of objects and renders them according to their
        rendering attributes. Objects can be categorized as fixed and
        non-fixed, and they are rendered separately."""
        # Render fixed but not-rendered objects.
        if not self.fixed_list:
            self.fixed_list = gl.glGenLists(1)
            gl.glNewList(self.fixed_list, gl.GL_COMPILE)
            for obj in objs:
                if not obj.fixed:
                    continue
                self.render(obj)
            gl.glEndList()

        # Reset to pre-rendered suface.
        self._clear()
        gl.glCallList(self.fixed_list)

        # Render non-fixed objects.
        for obj in objs:
            if obj.fixed:
                continue
            self.render(obj)

    def _clear(self):
        """Clear the graphics context and initialize view settings.  This
        function clears the graphics context by clearing the color and depth
        buffers. It then initializes the view settings including the view
        volume and rotation."""
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        # Initialize view port settings.
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(self.xoffset - .5 * self.zoom,
                   self.xoffset + .5 * self.zoom,
                   self.yoffset - .5 * self.zoom,
                   self.yoffset + .5 * self.zoom, -100, 100)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        gl.glRotatef(self.rot_x, 0, 1, 0)
        gl.glRotatef(self.rot_y, 1, 0, 0)
        gl.glRotatef(self.rot_z, 0, 0, 1)

    def _display(self):
        """Update the display and apply gradual screen rotation and zoom.
        This function updates the display, making any rendered graphics
        visible on the screen. Additionally, it applies a gradual screen
        rotation and zoom effect to provide visual interest."""
        pygame.display.flip()
        # Slowly rotate the screen.
        self.rot_z += .03
        self.zoom *= 0.9997
        # self.zoom *= 1.0001

    def _process_event(self, event):
        """Process user input events and update the graphics context.  This
        function handles various user input events, such as mouse button
        presses, mouse motion, and mouse button releases. It uses these events
        to interactively modify the graphics context, including zooming,
        tilting, and adjusting the visible area."""
        super()._process_event(event)
        # Mouse wheel zooms in and out the view.
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.zoom *= .99
            if event.button == 5:
                self.zoom *= 1.01
            self.last_button = event.button
        if event.type == pygame.MOUSEBUTTONUP:
            self.last_button = None
        if event.type == pygame.MOUSEMOTION:
            x, y = event.pos
            rx, ry = self.relative_position(x, y)
            # Dragging the left button tilts the view.
            if self.last_button == 1:
                self.rot_x = (rx - .5) * 180
                self.rot_y = (ry - .5) * 180
            # Dragging the right button change the visialbe area.
            if self.last_button == 3:
                self.xoffset = -(rx - .5)
                self.yoffset = ry - .5
