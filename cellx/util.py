#!/usr/bin/env python3
#
#
# Copyright (c) 2018, Hiroyuki Ohsaki.
# All rights reserved.
#
# $Id: util.py,v 1.2 2019/03/10 11:49:53 ohsaki Exp ohsaki $
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

def deg2rad(degree):
    """Conver degree DEGREE to radian."""
    return (2 * math.pi) * (degree / 360)

def rad2deg(rad):
    """Convert radian RAD to degree."""
    return 360 * (rad / (2 * math.pi))

def cmp(a, b):
    """Compare two numbers A and B, and return 1, 0, and -1 when A > B, A = B,
    and A < B, respectively."""
    if a > b:
        return 1
    elif a < b:
        return -1
    else:
        return 0
