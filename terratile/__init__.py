# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function, unicode_literals

import _terratile


def mesh_tile(dataset, tile, write_normals=False, quality=1.0):
    z, x, y = tile
    return _terratile.mesh_tile(
        int(dataset.this),
        int(z), int(x), int(y),
        bool(write_normals), float(quality))


def max_zoom(dataset):
    return _terratile.max_zoom(int(dataset.this))
