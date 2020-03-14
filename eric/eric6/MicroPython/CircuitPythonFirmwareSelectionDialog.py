# -*- coding: utf-8 -*-

# Copyright (c) 2019 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to enter the firmware flashing data.
"""


import os

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QDialogButtonBox

from E5Gui.E5PathPicker import E5PathPickerModes
from E5Gui import E5MessageBox

from .Ui_CircuitPythonFirmwareSelectionDialog import (
    Ui_CircuitPythonFirmwareSelectionDialog
)

import Utilities
import UI.PixmapCache


class CircuitPythonFirmwareSelectionDialog(
        QDialog, Ui_CircuitPythonFirmwareSelectionDialog):
    """
    Class implementing a dialog to enter the firmware flashing data.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(CircuitPythonFirmwareSelectionDialog, self).__init__(parent)
        self.setupUi(self)
        
        self.retestButton.setIcon(UI.PixmapCache.getIcon("rescan"))
        
        self.firmwarePicker.setMode(E5PathPickerModes.OpenFileMode)
        self.firmwarePicker.setFilters(
            self.tr("CircuitPython Firmware Files (*.uf2);;"
                    "All Files (*)"))
        
        self.bootPicker.setMode(E5PathPickerModes.DirectoryShowFilesMode)
        
        boards = (
            ("", ""),           # indicator for no selection
            
            ("Circuit Playground Express", "CPLAYBOOT"),
            ("Feather M0 Express", "FEATHERBOOT"),
            ("Feather M4 Express", "FEATHERBOOT"),
            ("Gemma M0", "GEMMABOOT"),
            ("Grand Central M4 Express", "GCM4BOOT"),
            ("ItsyBitsy M0 Express", "ITSYBOOT"),
            ("ItsyBitsy M4 Express", "ITSYM4BOOT"),
            ("Metro M0 Express", "METROBOOT"),
            ("Metro M4 Express", "METROM4BOOT"),
            ("NeoTrelis M4 Express", "TRELM4BOOT"),
            ("Trinket M0", "TRINKETBOOT"),
            
            ("Manual Select", "<manual>"),
        )
        for boardName, bootVolume in boards:
            self.boardComboBox.addItem(boardName, bootVolume)
        
        msh = self.minimumSizeHint()
        self.resize(max(self.width(), msh.width()), msh.height())
    
    def __updateOkButton(self):
        """
        Private method to update the state of the OK button and the retest
        button.
        """
        firmwareFile = self.firmwarePicker.text()
        self.retestButton.setEnabled(bool(firmwareFile) and
                                     os.path.exists(firmwareFile))
        
        if not bool(firmwareFile) or not os.path.exists(firmwareFile):
            enable = False
        else:
            volumeName = self.boardComboBox.currentData()
            if volumeName and volumeName != "<manual>":
                # check if the user selected a board and the board is in
                # bootloader mode
                deviceDirectory = Utilities.findVolume(volumeName)
                if deviceDirectory:
                    self.bootPicker.setText(deviceDirectory)
                    enable = True
                else:
                    enable = False
                    E5MessageBox.warning(
                        self,
                        self.tr("Select Path to Device"),
                        self.tr("""<p>The device volume <b>{0}</b> could not"""
                                """ be found. Is the device in 'bootloader'"""
                                """ mode and mounted?</p> <p>Alternatively"""
                                """ select the "Manual Select" entry and"""
                                """ enter the path to the device below.</p>""")
                        .format(volumeName)
                    )
            
            elif volumeName == "<manual>":
                # select the device path manually
                deviceDirectory = self.bootPicker.text()
                enable = (bool(deviceDirectory) and
                          os.path.exists(deviceDirectory))
            
            else:
                # illegal entry
                enable = False
        
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(enable)
    
    @pyqtSlot(str)
    def on_firmwarePicker_textChanged(self, firmware):
        """
        Private slot handling a change of the firmware path.
        
        @param firmware path to the firmware
        @type str
        """
        self.__updateOkButton()
    
    @pyqtSlot(int)
    def on_boardComboBox_currentIndexChanged(self, index):
        """
        Private slot to handle the selection of a board type.
        
        @param index index of the selected board type
        @type int
        """
        if self.boardComboBox.itemData(index) == "<manual>":
            self.bootPicker.clear()
            self.bootPicker.setEnabled(True)
        else:
            self.bootPicker.setEnabled(False)
        
        self.__updateOkButton()
    
    @pyqtSlot()
    def on_retestButton_clicked(self):
        """
        Private slot to research for the selected volume.
        """
        self.__updateOkButton()
    
    @pyqtSlot(str)
    def on_bootPicker_textChanged(self, devicePath):
        """
        Private slot handling a change of the device path.
        
        @param devicePath path to the device
        @type str
        """
        self.__updateOkButton()
    
    def getData(self):
        """
        Public method to obtain the entered data.
        
        @return tuple containing the path to the CircuitPython firmware file
            and the path to the device
        @rtype tuple of (str, str)
        """
        return self.firmwarePicker.text(), self.bootPicker.text()
