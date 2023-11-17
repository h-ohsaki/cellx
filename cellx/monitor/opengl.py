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
import struct

import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.GLUT as glut
import cellx
import pygame
from cellx.monitor.sdl import SDL

class OpenGL(SDL):
    def __init__(self, *kargs, **kwargs):
        super().__init__(*kargs, **kwargs)

    def init(self):
        super().init()
        width, height = self.width, self.height
        self.hwscreen = pygame.display.set_mode(
            (width, height), pygame.OPENGL | pygame.DOUBLEBUF)
        glut.glutInit()

    def normalize_position(self, x, y):
        return (x - self.width / 2) / self.width, (
            y - self.height / 2) / self.height

    def normalize_size(self, l):
        return l / self.width

    def _render_box(self, obj):
        x, y = self.normalize_position(obj.x, obj.y)
        w, h = self.normalize_size(obj.width), self.normalize_size(obj.height)
        color = self.palette.rgba(obj.color, obj.alpha)
        gl.glColor4ub(*color)
        gl.glPushMatrix()
        gl.glTranslatef(x, y, obj.priority)
        gl.glScalef(w, h, (w + h) / 2)
        gl.glMaterialfv(gl.GL_FRONT, gl.GL_EMISSION,
                        struct.pack('4f', .2, .2, 0, 1))
        glut.glutSolidCube(1)
        gl.glMaterialfv(gl.GL_FRONT, gl.GL_EMISSION,
                        struct.pack('4f', 0, 0, 0, 1))
        gl.glPopMatrix()

    def _render_ellipse(self, obj):
        x, y = self.normalize_position(obj.x, obj.y)
        r = self.normalize_size(obj.width / 2)
        color = self.palette.rgba(obj.color, obj.alpha)
        gl.glColor4ub(*color)
        gl.glPushMatrix()
        gl.glTranslatef(x, y, obj.priority)
        glut.glutSolidSphere(r, 20, 20)
        gl.glPopMatrix()

        pygame.display.flip()

        pygame.display.flip()
        import time
        time.sleep(10)

    def _display(self):
        pygame.display.flip()
