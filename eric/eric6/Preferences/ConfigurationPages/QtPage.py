# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Qt configuration page.
"""


from PyQt5.QtCore import pyqtSlot

from E5Gui.E5PathPicker import E5PathPickerModes

from .ConfigurationPageBase import ConfigurationPageBase
from .Ui_QtPage import Ui_QtPage

import Preferences


class QtPage(ConfigurationPageBase, Ui_QtPage):
    """
    Class implementing the Qt configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        super(QtPage, self).__init__()
        self.setupUi(self)
        self.setObjectName("QtPage")
        
        self.qtTransPicker.setMode(E5PathPickerModes.DirectoryMode)
        self.qtToolsDirPicker.setMode(E5PathPickerModes.DirectoryShowFilesMode)
        self.pyqtToolsDirPicker.setMode(
            E5PathPickerModes.DirectoryShowFilesMode)
        
        # set initial values
        self.qtTransPicker.setText(
            Preferences.getQt("Qt5TranslationsDir"))
        self.qtToolsDirPicker.setText(Preferences.getQt("QtToolsDir"))
        self.qtPrefixEdit.setText(Preferences.getQt("QtToolsPrefix"))
        self.qtPostfixEdit.setText(Preferences.getQt("QtToolsPostfix"))
        self.__updateQtSample()
        self.pyqtToolsDirPicker.setText(Preferences.getQt("PyQtToolsDir"))
        self.pyuicIndentSpinBox.setValue(Preferences.getQt("PyuicIndent"))
        self.pyuicImportsCheckBox.setChecked(
            Preferences.getQt("PyuicFromImports"))
        
    def save(self):
        """
        Public slot to save the Qt configuration.
        """
        Preferences.setQt("Qt5TranslationsDir", self.qtTransPicker.text())
        Preferences.setQt("QtToolsDir", self.qtToolsDirPicker.text())
        Preferences.setQt("QtToolsPrefix", self.qtPrefixEdit.text())
        Preferences.setQt("QtToolsPostfix", self.qtPostfixEdit.text())
        Preferences.setQt("PyQtToolsDir", self.pyqtToolsDirPicker.text())
        Preferences.setQt("PyuicIndent", self.pyuicIndentSpinBox.value())
        Preferences.setQt("PyuicFromImports",
                          self.pyuicImportsCheckBox.isChecked())
        
    def __updateQtSample(self):
        """
        Private slot to update the Qt tools sample label.
        """
        self.qtSampleLabel.setText(
            self.tr("Sample: {0}designer{1}").format(
                self.qtPrefixEdit.text(), self.qtPostfixEdit.text()))
    
    @pyqtSlot(str)
    def on_qtPrefixEdit_textChanged(self, txt):
        """
        Private slot to handle a change in the entered Qt directory.
        
        @param txt the entered string (string)
        """
        self.__updateQtSample()
    
    @pyqtSlot(str)
    def on_qtPostfixEdit_textChanged(self, txt):
        """
        Private slot to handle a change in the entered Qt directory.
        
        @param txt the entered string (string)
        """
        self.__updateQtSample()
    

def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    @return reference to the instantiated page (ConfigurationPageBase)
    """
    page = QtPage()
    return page
