# -*- coding: utf-8 -*-

# Copyright (c) 2019 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the MicroPython configuration page.
"""


from E5Gui.E5PathPicker import E5PathPickerModes

from .ConfigurationPageBase import ConfigurationPageBase
from .Ui_MicroPythonPage import Ui_MicroPythonPage

import Preferences

from MicroPython.MicroPythonWidget import AnsiColorSchemes


class MicroPythonPage(ConfigurationPageBase, Ui_MicroPythonPage):
    """
    Class implementing the MicroPython configuration page.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(MicroPythonPage, self).__init__()
        self.setupUi(self)
        self.setObjectName("MicroPythonPage")
        
        self.colorSchemeComboBox.addItems(sorted(AnsiColorSchemes.keys()))
        
        self.mpyCrossPicker.setMode(E5PathPickerModes.OpenFileMode)
        self.mpyCrossPicker.setFilters(self.tr("All Files (*)"))
        
        self.dfuUtilPathPicker.setMode(E5PathPickerModes.OpenFileMode)
        self.dfuUtilPathPicker.setFilters(self.tr("All Files (*)"))
        
        # set initial values
        self.timeoutSpinBox.setValue(
            Preferences.getMicroPython("SerialTimeout") / 1000)
        # converted to seconds
        self.syncTimeCheckBox.setChecked(
            Preferences.getMicroPython("SyncTimeAfterConnect"))
        self.colorSchemeComboBox.setCurrentIndex(
            self.colorSchemeComboBox.findText(
                Preferences.getMicroPython("ColorScheme")))
        self.replWrapCheckBox.setChecked(
            Preferences.getMicroPython("ReplLineWrap"))
        self.mpyCrossPicker.setText(
            Preferences.getMicroPython("MpyCrossCompiler"))
        self.dfuUtilPathPicker.setText(
            Preferences.getMicroPython("DfuUtilPath"))
        self.micropythonFirmwareUrlLineEdit.setText(
            Preferences.getMicroPython("MicroPythonFirmwareUrl"))
        self.circuitpythonFirmwareUrlLineEdit.setText(
            Preferences.getMicroPython("CircuitPythonFirmwareUrl"))
        self.microbitFirmwareUrlLineEdit.setText(
            Preferences.getMicroPython("MicrobitFirmwareUrl"))
        self.micropythonDocuUrlLineEdit.setText(
            Preferences.getMicroPython("MicroPythonDocuUrl"))
        self.circuitpythonDocuUrlLineEdit.setText(
            Preferences.getMicroPython("CircuitPythonDocuUrl"))
        self.microbitDocuUrlLineEdit.setText(
            Preferences.getMicroPython("MicrobitDocuUrl"))
    
    def save(self):
        """
        Public slot to save the MicroPython configuration.
        """
        Preferences.setMicroPython(
            "SerialTimeout",
            self.timeoutSpinBox.value() * 1000)
        # converted to milliseconds
        Preferences.setMicroPython(
            "SyncTimeAfterConnect",
            self.syncTimeCheckBox.isChecked())
        Preferences.setMicroPython(
            "ColorScheme",
            self.colorSchemeComboBox.currentText())
        Preferences.setMicroPython(
            "ReplLineWrap",
            self.replWrapCheckBox.isChecked())
        Preferences.setMicroPython(
            "MpyCrossCompiler",
            self.mpyCrossPicker.text())
        Preferences.setMicroPython(
            "DfuUtilPath",
            self.dfuUtilPathPicker.text())
        Preferences.setMicroPython(
            "MicroPythonFirmwareUrl",
            self.micropythonFirmwareUrlLineEdit.text())
        Preferences.setMicroPython(
            "CircuitPythonFirmwareUrl",
            self.circuitpythonFirmwareUrlLineEdit.text())
        Preferences.setMicroPython(
            "MicrobitFirmwareUrl",
            self.microbitFirmwareUrlLineEdit.text())
        Preferences.setMicroPython(
            "MicroPythonDocuUrl",
            self.micropythonDocuUrlLineEdit.text())
        Preferences.setMicroPython(
            "CircuitPythonDocuUrl",
            self.circuitpythonDocuUrlLineEdit.text())
        Preferences.setMicroPython(
            "MicrobitDocuUrl",
            self.microbitDocuUrlLineEdit.text())


def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    @return reference to the instantiated page (ConfigurationPageBase)
    """
    return MicroPythonPage()
