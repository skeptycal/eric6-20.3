# -*- coding: utf-8 -*-

# Copyright (c) 2019 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the snapshot mode enumeration.
"""


try:
    from enum import Enum
except ImportError:
    from ThirdParty.enum import Enum


class SnapshotModes(Enum):
    """
    Class implementing the snapshot modes.
    """
    Fullscreen = 0
    SelectedScreen = 1
    Rectangle = 2
    Freehand = 3
    Ellipse = 4
    SelectedWindow = 5
