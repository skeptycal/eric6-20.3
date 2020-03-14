# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Debugger Python2 configuration page.
"""


from PyQt5.QtCore import pyqtSlot

from E5Gui.E5Application import e5App
from E5Gui.E5PathPicker import E5PathPickerModes

from .ConfigurationPageBase import ConfigurationPageBase
from .Ui_DebuggerPython2Page import Ui_DebuggerPython2Page

import Preferences
import UI.PixmapCache


class DebuggerPython2Page(ConfigurationPageBase, Ui_DebuggerPython2Page):
    """
    Class implementing the Debugger Python2 configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        super(DebuggerPython2Page, self).__init__()
        self.setupUi(self)
        self.setObjectName("DebuggerPython2Page")
        
        try:
            self.__virtualenvManager = e5App().getObject("VirtualEnvManager")
        except KeyError:
            from VirtualEnv.VirtualenvManager import VirtualenvManager
            self.__virtualenvManager = VirtualenvManager()
        
        self.venvDlgButton.setIcon(UI.PixmapCache.getIcon("virtualenv.png"))
        
        self.debugClientPicker.setMode(E5PathPickerModes.OpenFileMode)
        self.debugClientPicker.setToolTip(self.tr(
            "Press to select the Debug Client via a file selection dialog"))
        self.debugClientPicker.setFilters(self.tr("Python Files (*.py *.py2)"))
        
        self.__populateAndSetVenvComboBox()
        
        # set initial values
        dct = Preferences.getDebugger("DebugClientType")
        if dct == "standard":
            self.standardButton.setChecked(True)
        else:
            self.customButton.setChecked(True)
        self.debugClientPicker.setText(
            Preferences.getDebugger("DebugClient"), toNative=False)
        self.pyRedirectCheckBox.setChecked(
            Preferences.getDebugger("PythonRedirect"))
        self.pyNoEncodingCheckBox.setChecked(
            Preferences.getDebugger("PythonNoEncoding"))
        self.sourceExtensionsEdit.setText(
            Preferences.getDebugger("PythonExtensions"))
    
    def save(self):
        """
        Public slot to save the Debugger Python configuration.
        """
        Preferences.setDebugger(
            "Python2VirtualEnv",
            self.venvComboBox.currentText())
        if self.standardButton.isChecked():
            dct = "standard"
        else:
            dct = "custom"
        Preferences.setDebugger("DebugClientType", dct)
        Preferences.setDebugger(
            "DebugClient",
            self.debugClientPicker.text(toNative=False))
        Preferences.setDebugger(
            "PythonRedirect",
            self.pyRedirectCheckBox.isChecked())
        Preferences.setDebugger(
            "PythonNoEncoding",
            self.pyNoEncodingCheckBox.isChecked())
    
    def __populateAndSetVenvComboBox(self):
        """
        Private method to populate and set the virtual environment combo box.
        """
        self.venvComboBox.clear()
        self.venvComboBox.addItems(
            [""] +
            sorted(self.__virtualenvManager.getVirtualenvNamesForVariant(2))
        )
        
        # set initial value
        venvName = Preferences.getDebugger("Python2VirtualEnv")
        if venvName:
            index = self.venvComboBox.findText(venvName)
            if index < 0:
                index = 0
            self.venvComboBox.setCurrentIndex(index)
    
    @pyqtSlot()
    def on_refreshButton_clicked(self):
        """
        Private slot handling a click of the refresh button.
        """
        self.sourceExtensionsEdit.setText(
            Preferences.getDebugger("PythonExtensions"))
    
    @pyqtSlot()
    def on_venvDlgButton_clicked(self):
        """
        Private slot to show the virtual environment manager dialog.
        """
        self.__virtualenvManager.showVirtualenvManagerDialog(modal=True)
        self.__populateAndSetVenvComboBox()
        self.activateWindow()
        self.raise_()
    

def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    @return reference to the instantiated page (ConfigurationPageBase)
    """
    page = DebuggerPython2Page()
    return page
