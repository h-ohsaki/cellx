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
import cellx
import pygame
import tbdump

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
        super().__init__(*kargs, **kwargs)

    def init(self):
        super().init()
        # Re-initialize display with OpenGL support.
        width, height = self.width, self.height
        self.hwscreen = pygame.display.set_mode(
            (width, height), pygame.OPENGL | pygame.DOUBLEBUF)
        glut.glutInit()

        gl.glShadeModel(gl.GL_SMOOTH)
        # FIXME: Not supported?
        # gl.glShadeModel(gl.GL_LINE_SMOOTH)

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
        gl.glMaterialf(gl.GL_FRONT, gl.GL_SHININESS, 100)

        gl.glLight(gl.GL_LIGHT0, gl.GL_POSITION, (-80, 80, -50, 1))
        gl.glLight(gl.GL_LIGHT0, gl.GL_AMBIENT, (1, 1, 1, 1))
        gl.glLight(gl.GL_LIGHT0, gl.GL_DIFFUSE, (.2, .7, .7, 1))
        gl.glLight(gl.GL_LIGHT0, gl.GL_SPECULAR, (1, 1, 1, 1))

    def normalize_position(self, x, y):
        return (x - self.width /
                2) / self.width, -(y - self.height / 2) / self.height

    def normalize_size(self, l):
        return l / self.width

    def relative_position(self, x, y):
        return x / self.width, y / self.height

    def draw_line(self, sx, sy, dx, dy, width, color, alpha, use_line=False):
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
        else:
            # Place a square rod connecting (SX, SY) and (DX, DY).
            # This code assumes SX is smaller than DX.
            gl.glPushMatrix()
            gl.glTranslatef(sx, sy, 0)
            angle = math.degrees(math.atan2(dy - sy, dx - sx))
            gl.glRotatef(angle, 0, 0, 1)
            l = math.sqrt((dx - sx)**2 + (dy - sy)**2)
            # Rotate 45 degrees for better visibility.
            gl.glRotatef(45, 1, 0, 0)
            gl.glScalef(l, w, w)
            gl.glTranslatef(.5, 0, 0)
            gl.glMaterial(gl.GL_FRONT, gl.GL_EMISSION, (.2, .2, 0, 1))
            glut.glutSolidCube(1)
            gl.glMaterial(gl.GL_FRONT, gl.GL_EMISSION, (0, 0, 0, 1))
            gl.glPopMatrix()

    def _render_box(self, obj):
        x, y = self.normalize_position(obj.x, obj.y)
        w, h = self.normalize_size(obj.width), self.normalize_size(obj.height)
        z = self.normalize_size(obj.priority)
        color = self.palette.rgba(obj.color, obj.alpha)
        gl.glColor4ub(*color)
        gl.glPushMatrix()
        gl.glTranslatef(x, y, z)
        gl.glScalef(w, h, (w + h) / 2)
        gl.glMaterial(gl.GL_FRONT, gl.GL_EMISSION, (.2, .2, 0, 1))
        glut.glutSolidCube(1)
        gl.glMaterial(gl.GL_FRONT, gl.GL_EMISSION, (0, 0, 0, 1))
        gl.glPopMatrix()

    def _render_ellipse(self, obj):
        x, y = self.normalize_position(obj.x, obj.y)
        z = self.normalize_size(obj.priority)
        r = self.normalize_size(obj.width / 2)
        color = self.palette.rgba(obj.color, obj.alpha)
        gl.glColor4ub(*color)
        gl.glPushMatrix()
        gl.glTranslatef(x, y, z)
        glut.glutSolidSphere(r, 20, 20)
        gl.glPopMatrix()

    def render_objects(self, objs):
        self._clear()
        # FIXME: support `fix' objects.
        super().render_objects(objs)

    def _clear(self):
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
        pygame.display.flip()
        # Slowly rotate the screen.
        self.rot_z += .02

    def _process_event(self, event):
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
