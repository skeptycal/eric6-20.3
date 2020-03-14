# -*- coding: utf-8 -*-

# Copyright (c) 2019 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the device interface class for CircuitPython boards.
"""


import shutil
import os

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog

from E5Gui import E5MessageBox, E5FileDialog

from .MicroPythonDevices import MicroPythonDevice
from .MicroPythonWidget import HAS_QTCHART

import Utilities
import Preferences


class CircuitPythonDevice(MicroPythonDevice):
    """
    Class implementing the device for CircuitPython boards.
    """
    DeviceVolumeName = "CIRCUITPY"
    
    def __init__(self, microPythonWidget, parent=None):
        """
        Constructor
        
        @param microPythonWidget reference to the main MicroPython widget
        @type MicroPythonWidget
        @param parent reference to the parent object
        @type QObject
        """
        super(CircuitPythonDevice, self).__init__(microPythonWidget, parent)
    
    def setButtons(self):
        """
        Public method to enable the supported action buttons.
        """
        super(CircuitPythonDevice, self).setButtons()
        self.microPython.setActionButtons(
            run=True, repl=True, files=True, chart=HAS_QTCHART)
        
        if self.__deviceVolumeMounted():
            self.microPython.setActionButtons(open=True, save=True)
    
    def forceInterrupt(self):
        """
        Public method to determine the need for an interrupt when opening the
        serial connection.
        
        @return flag indicating an interrupt is needed
        @rtype bool
        """
        return False
    
    def deviceName(self):
        """
        Public method to get the name of the device.
        
        @return name of the device
        @rtype str
        """
        return self.tr("CircuitPython")
    
    def canStartRepl(self):
        """
        Public method to determine, if a REPL can be started.
        
        @return tuple containing a flag indicating it is safe to start a REPL
            and a reason why it cannot.
        @rtype tuple of (bool, str)
        """
        return True, ""
    
    def canStartPlotter(self):
        """
        Public method to determine, if a Plotter can be started.
        
        @return tuple containing a flag indicating it is safe to start a
            Plotter and a reason why it cannot.
        @rtype tuple of (bool, str)
        """
        return True, ""
    
    def canRunScript(self):
        """
        Public method to determine, if a script can be executed.
        
        @return tuple containing a flag indicating it is safe to start a
            Plotter and a reason why it cannot.
        @rtype tuple of (bool, str)
        """
        return True, ""
    
    def runScript(self, script):
        """
        Public method to run the given Python script.
        
        @param script script to be executed
        @type str
        """
        pythonScript = script.split("\n")
        self.sendCommands(pythonScript)
    
    def canStartFileManager(self):
        """
        Public method to determine, if a File Manager can be started.
        
        @return tuple containing a flag indicating it is safe to start a
            File Manager and a reason why it cannot.
        @rtype tuple of (bool, str)
        """
        return True, ""
    
    def supportsLocalFileAccess(self):
        """
        Public method to indicate file access via a local directory.
        
        @return flag indicating file access via local directory
        @rtype bool
        """
        return self.__deviceVolumeMounted()
    
    def __deviceVolumeMounted(self):
        """
        Private method to check, if the device volume is mounted.
        
        @return flag indicated a mounted device
        @rtype bool
        """
        return self.getWorkspace(silent=True).endswith(self.DeviceVolumeName)
    
    def getWorkspace(self, silent=False):
        """
        Public method to get the workspace directory.
        
        @param silent flag indicating silent operations
        @type bool
        @return workspace directory used for saving files
        @rtype str
        """
        # Attempts to find the path on the filesystem that represents the
        # plugged in CIRCUITPY board.
        deviceDirectory = Utilities.findVolume(self.DeviceVolumeName)
        
        if deviceDirectory:
            return deviceDirectory
        else:
            # return the default workspace and give the user a warning (unless
            # silent mode is selected)
            if not silent:
                E5MessageBox.warning(
                    self.microPython,
                    self.tr("Workspace Directory"),
                    self.tr("Python files for CircuitPython devices are stored"
                            " on the device. Therefore, to edit these files"
                            " you need to have the device plugged in. Until"
                            " you plug in a device, the standard directory"
                            " will be used."))
            
            return super(CircuitPythonDevice, self).getWorkspace()
    
    def addDeviceMenuEntries(self, menu):
        """
        Public method to add device specific entries to the given menu.
        
        @param menu reference to the context menu
        @type QMenu
        """
        connected = self.microPython.isConnected()
        
        act = menu.addAction(self.tr("Flash CircuitPython Firmware"),
                             self.__flashCircuitPython)
        act.setEnabled(not connected)
        menu.addSeparator()
        act = menu.addAction(self.tr("Install Library Files"),
                             self.__installLibraryFiles)
        act.setEnabled(self.__deviceVolumeMounted())
    
    @pyqtSlot()
    def __flashCircuitPython(self):
        """
        Private slot to flash a CircuitPython firmware to the device.
        """
        ok = E5MessageBox.information(
            self.microPython,
            self.tr("Flash CircuitPython Firmware"),
            self.tr("Please reset the device to bootloader mode and confirm"
                    " when ready."),
            E5MessageBox.StandardButtons(
                E5MessageBox.Abort |
                E5MessageBox.Ok))
        if ok:
            from .CircuitPythonFirmwareSelectionDialog import (
                CircuitPythonFirmwareSelectionDialog)
            dlg = CircuitPythonFirmwareSelectionDialog()
            if dlg.exec_() == QDialog.Accepted:
                cpyPath, devicePath = dlg.getData()
                shutil.copy2(cpyPath, devicePath)
    
    @pyqtSlot()
    def __installLibraryFiles(self):
        """
        Private slot to install Python files into the onboard library.
        """
        if not self.__deviceVolumeMounted():
            E5MessageBox.critical(
                self.microPython,
                self.tr("Install Library Files"),
                self.tr("""The device volume "<b>{0}</b>" is not available."""
                        """ Ensure it is mounted properly and try again."""))
            return
        
        target = os.path.join(self.getWorkspace(), "lib")
        # ensure that the library directory exists on the device
        if not os.path.isdir(target):
            os.makedirs(target)
        
        libraryFiles = E5FileDialog.getOpenFileNames(
            self.microPython,
            self.tr("Install Library Files"),
            os.path.expanduser("~"),
            self.tr("Compiled Python Files (*.mpy);;"
                    "Python Files (*.py);;"
                    "All Files (*)"))
        
        for libraryFile in libraryFiles:
            if os.path.exists(libraryFile):
                shutil.copy2(libraryFile, target)
    
    def getDocumentationUrl(self):
        """
        Public method to get the device documentation URL.
        
        @return documentation URL of the device
        @rtype str
        """
        return Preferences.getMicroPython("CircuitPythonDocuUrl")
    
    def getFirmwareUrl(self):
        """
        Public method to get the device firmware download URL.
        
        @return firmware download URL of the device
        @rtype str
        """
        return Preferences.getMicroPython("CircuitPythonFirmwareUrl")
