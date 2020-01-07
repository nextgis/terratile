# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function, unicode_literals

import _terratile


def build(dataset, tile):
    z, x, y = tile
    return _terratile.build(
        int(dataset.this),
        int(z), int(x), int(y))