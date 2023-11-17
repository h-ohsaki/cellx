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

import OpenGL.GL as gl
import OpenGL.GLUT as glut
import cellx
import pygame
from cellx.monitor.sdl import SDL

import tbdump

class OpenGL(SDL):
    def __init__(self, *kargs, **kwargs):
        self.xoffset = 0.
        self.yoffset = 0.
        self.zoom = 1.
        self.rot_x = 0.
        self.rot_y = 0.
        self.rot_z = 0.
        self.last_button = None
        self.texture_id = None
        super().__init__(*kargs, **kwargs)

    def init(self):
        super().init()
        width, height = self.width, self.height
        self.hwscreen = pygame.display.set_mode(
            (width, height), pygame.OPENGL | pygame.DOUBLEBUF)
        glut.glutInit()
        self._clear()

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
        mat_specular = (1, 1, 0, 1)
        gl.glMaterial(gl.GL_FRONT, gl.GL_SPECULAR, *mat_specular)
        mat_diffuse = (0, 1, 1, 1)
        gl.glMaterial(gl.GL_FRONT, gl.GL_DIFFUSE, *mat_diffuse)
        gl.glMaterialf(gl.GL_FRONT, gl.GL_SHININESS, 50)
        light_position = (-.25, .25, .5, 0)
        gl.glLight(gl.GL_LIGHT0, gl.GL_POSITION, *light_position)
        gl.glLight(gl.GL_LIGHT0, gl.GL_AMBIENT, (.3, .3, .3, 1))
        # FIXME: Not supported?
        # gl.glLightModel(gl.GL_LIGHT_MODEL_AMBIENT, (.3, .3, .3, 1))

        self.texture_id = gl.glGenTextures(1)

    def normalize_position(self, x, y):
        return (x - self.width / 2) / self.width, (
            y - self.height / 2) / self.height

    def normalize_size(self, l):
        return l / self.width

    def relative_position(self, x, y):
        return x / self.width, y / self.height

    def draw_surface(self):
        rgb_surface = pygame.image.tostring(self.screen, 'RGB')
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_id)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER,
                           gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER,
                           gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP)
        rect = self.screen.get_rect()
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, rect.width,
                        rect.height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE,
                        rgb_surface)
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

    def draw_line(self, sx, sy, dx, dy, width, color, alpha):
        sx, sy = self.normalize_position(sx, sy)
        dx, dy = self.normalize_position(dx, dy)
        color = self.palette.rgba(color, alpha)
        gl.glLineWidth(width)
        gl.glColor4ub(*color)
        gl.glBegin(gl.GL_LINES)
        gl.glVertex2d(sx, sy)
        gl.glVertex2d(dx, dy)
        gl.glEnd()

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
        self.draw_surface()
        pygame.display.flip()
        # Slowly rotate the screen.
        self.rot_z += .02

    def _process_event(self, event):
        super()._process_event(event)
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
            if self.last_button == 1:
                self.rot_x = (rx - .5) * 180
                self.rot_y = (ry - .5) * 180
            if self.last_button == 3:
                self.xoffset = -(rx - .5)
                self.yoffset = ry - .5
