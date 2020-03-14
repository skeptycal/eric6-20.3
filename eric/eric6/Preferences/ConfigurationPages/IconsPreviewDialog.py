# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to preview the contents of an icon directory.
"""


import os.path

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QListWidgetItem, QDialog
from PyQt5.QtCore import QDir

from .Ui_IconsPreviewDialog import Ui_IconsPreviewDialog


class IconsPreviewDialog(QDialog, Ui_IconsPreviewDialog):
    """
    Class implementing a dialog to preview the contents of an icon directory.
    """
    def __init__(self, parent, dirName):
        """
        Constructor
        
        @param parent parent widget (QWidget)
        @param dirName name of directory to show (string)
        """
        super(IconsPreviewDialog, self).__init__(parent)
        self.setupUi(self)
        
        directory = QDir(dirName)
        for icon in directory.entryList(["*.svg", "*.svgz", "*.png"]):
            QListWidgetItem(
                QIcon(os.path.join(dirName, icon)),
                icon, self.iconView)
