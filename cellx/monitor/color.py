#!/usr/bin/env python3
#
#
# Copyright (c) 2018, Hiroyuki Ohsaki.
# All rights reserved.
#
# $Id: null.py,v 1.4 2019/03/10 11:49:59 ohsaki Exp ohsaki $
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

from perlcompat import die

COLOR_ALIASES = {
    'blue': 'SteelBlue', 'red': 'chocolate1', 'magenta': 'orange', 'cyan':
    'SkyBlue', 'green': 'PaleGreen', 'yellow': 'LightGoldenrod'
}

def hsv2rgb(h, s, v):
    """Convert color in HSV (Hue, Saturation, Value) space to RGB.  Return (R,
    G, B) as a list.  Transformation algorithm is taken from
    http://psychology.wikia.com/wiki/HSV_color_space."""
    hi = int(h / 60) % 6
    f = h / 60 - hi
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    if hi == 0:
        return v, t, p
    elif hi == 1:
        return q, v, p
    elif hi == 2:
        return p, v, t
    elif hi == 3:
        return p, q, v
    elif hi == 4:
        return t, p, v
    elif hi == 5:
        return v, p, q

def rgb_in_scheme(scheme, p=1):
    """Return the RGBA color (R, G, B, A) in color scheme SCHEME with
    brightness P."""
    if scheme == 0:  # HSV
        return hsv2rgb(240 * (1 - p), .9, 1.)
    elif scheme == 1:  # cyan-red
        return hsv2rgb(0 + 180 * (1 - p), abs(p - .5) * 2, 1.)
    elif scheme == 2:  # blue-orange
        return hsv2rgb(30 + 180 * (1 - p), abs(p - .5) * 2, 1.)
    elif scheme == 3:  # blue-yellow
        return hsv2rgb(60 + 180 * (1 - p), abs(p - .5) * 2, 1.)
    elif scheme == 4:  # purple-green
        return hsv2rgb(90 + 180 * (1 - p), abs(p - .5) * 2, 1.)
    elif scheme == 5:  # green-magenta
        return hsv2rgb(120 + 180 * p, abs(p - .5) * 2, 1.)
    elif scheme == 6:  # green-red
        return hsv2rgb(150 + 180 * p, abs(p - .5) * 2, 1.)
    else:
        die("rbg_in_scheme: invalid color scheme '{}'".format(scheme))

def load_x11_colors(file='/usr/share/X11/rgb.txt'):
    """Parse X Windows System's color definition and return all colors as a
    list.  Every color is represented as [NAME, R, G, B]."""
    try:
        f = open(file)
    except FileNotFoundError:
        return []
    colors = []
    for line in f:
        line = line.rstrip()
        if line.startswith('!'):
            continue
        color, name = line.split('\t\t')
        r, g, b = color.split()
        colors.append([name, int(r), int(g), int(b)])
    return colors

class Palette:
    def __init__(self, color_scheme=0):
        self.color_scheme = color_scheme
        self.palette = {}

    def define_color(self, name, r, g, b, a=1):
        """Define color NAME whose RGBA values are R, G, B, and A.  If R, G,
        B, and A are represented as ratios (e.g., R = .2 instead of R = 51),
        those values are converted to 8-bit integer."""
        if r <= 1:
            r *= 0xff
        if g <= 1:
            g *= 0xff
        if b <= 1:
            b *= 0xff
        if a <= 1:
            a *= 0xff
        self.palette[name] = [int(r), int(g), int(b), int(a)]

    def rgba(self, name, alpha=1.):
        """Return R, G, B, and A values of color NAME as a tuple.  If ALPHA is
        specified, alpha channel (A value) is multiplied by ALPHA."""
        try:
            r, g, b, a = self.palette[name]
        except KeyError:
            return None
        return r, g, b, a * alpha

    def rgb(self, name):
        """Return R, G and B values of color NAME as a tuple."""
        return self.rgba(name)[0:3]

    def reset(self):
        """Initialize color palette."""
        self.palette = {}

        # define builtin color names
        for level in range(100 + 1):
            p = level / 100
            q = 1 - p
            self.define_color('gray{}'.format(level), p, p, p)
            rgb = rgb_in_scheme(self.color_scheme, p)
            self.define_color('heat{}'.format(level), *rgb)
            self.define_color('cool{}'.format(level), 0, .8 * p,
                              .9 * p + .4 * q)

        # load color names from X Window System's rgb.txt
        for name, r, g, b in load_x11_colors():
            self.define_color(name, r, g, b)

        # define aliases (nickanems)
        for nickname, name in COLOR_ALIASES.items():
            self.define_color(nickname, *self.rgb(name))
