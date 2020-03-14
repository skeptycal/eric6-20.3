# -*- coding: utf-8 -*-

# Copyright (c) 2018 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to enter the data of a virtual environment.
"""


import os
import sys

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QDialogButtonBox

from E5Gui.E5PathPicker import E5PathPickerModes

from .Ui_VirtualenvAddEditDialog import Ui_VirtualenvAddEditDialog

import Utilities


class VirtualenvAddEditDialog(QDialog, Ui_VirtualenvAddEditDialog):
    """
    Class implementing a dialog to enter the data of a virtual environment.
    """
    def __init__(self, manager, venvName="", venvDirectory="",
                 venvInterpreter="", venvVariant=3, isGlobal=False,
                 isConda=False, isRemote=False, execPath="", parent=None):
        """
        Constructor
        
        @param manager reference to the virtual environment manager
        @type VirtualenvManager
        @param venvName logical name of a virtual environment for editing
        @type str
        @param venvDirectory directory of the virtual environment
        @type str
        @param venvInterpreter Python interpreter of the virtual environment
        @type str
        @param venvVariant Python variant of the virtual environment
        @type int
        @param isGlobal flag indicating a global environment
        @type bool
        @param isConda flag indicating an Anaconda virtual environment
        @type bool
        @param isRemote flag indicating a remotely accessed environment
        @type bool
        @param execPath search path string to be prepended to the PATH
            environment variable
        @type str
        @param parent reference to the parent widget
        @type QWidget
        """
        super(VirtualenvAddEditDialog, self).__init__(parent)
        self.setupUi(self)
        
        self.__venvName = venvName
        self.__manager = manager
        self.__editMode = bool(venvName)
        
        self.targetDirectoryPicker.setMode(E5PathPickerModes.DirectoryMode)
        self.targetDirectoryPicker.setWindowTitle(
            self.tr("Virtualenv Target Directory"))
        self.targetDirectoryPicker.setDefaultDirectory(Utilities.getHomeDir())
        
        self.pythonExecPicker.setMode(E5PathPickerModes.OpenFileMode)
        self.pythonExecPicker.setWindowTitle(
            self.tr("Python Interpreter"))
        self.pythonExecPicker.setDefaultDirectory(
            sys.executable.replace("w.exe", ".exe"))
        
        self.execPathEdit.setToolTip(self.tr(
            "Enter the executable search path to be prepended to the PATH"
            " environment variable. Use '{0}' as the separator.").format(
            os.pathsep)
        )
        
        self.nameEdit.setText(venvName)
        self.targetDirectoryPicker.setText(venvDirectory,
                                           toNative=not isRemote)
        self.pythonExecPicker.setText(venvInterpreter,
                                      toNative=not isRemote)
        self.variantComboBox.setCurrentIndex(3 - venvVariant)
        self.globalCheckBox.setChecked(isGlobal)
        self.anacondaCheckBox.setChecked(isConda)
        self.remoteCheckBox.setChecked(isRemote)
        self.execPathEdit.setText(execPath)
        
        self.__updateOk()
    
    def __updateOk(self):
        """
        Private slot to update the state of the OK button.
        """
        if self.__editMode:
            enable = (
                bool(self.nameEdit.text()) and
                (self.nameEdit.text() == self.__venvName or
                 self.__manager.isUnique(self.nameEdit.text()))
            )
        else:
            enable = (
                bool(self.nameEdit.text()) and
                self.__manager.isUnique(self.nameEdit.text())
            )
        
        if not self.globalCheckBox.isChecked():
            enable = (
                enable and (
                    self.remoteCheckBox.isChecked() or (
                        bool(self.targetDirectoryPicker.text()) and
                        os.path.exists(self.targetDirectoryPicker.text())
                    )
                )
            )
        
        enable = (
            enable and
            bool(self.pythonExecPicker.text()) and (
                self.remoteCheckBox.isChecked() or
                os.access(self.pythonExecPicker.text(), os.X_OK)
            )
        )
        
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(enable)
    
    @pyqtSlot(str)
    def on_nameEdit_textChanged(self, txt):
        """
        Private slot to handle changes of the logical name.
        
        @param txt current logical name
        @type str
        """
        self.__updateOk()
    
    @pyqtSlot(str)
    def on_targetDirectoryPicker_textChanged(self, txt):
        """
        Private slot to handle changes of the virtual environment directory.
        
        @param txt virtual environment directory
        @type str
        """
        self.__updateOk()
        
        if txt:
            self.pythonExecPicker.setDefaultDirectory(txt)
        else:
            self.pythonExecPicker.setDefaultDirectory(
                sys.executable.replace("w.exe", ".exe"))
    
    @pyqtSlot(str)
    def on_pythonExecPicker_textChanged(self, txt):
        """
        Private slot to handle changes of the virtual environment interpreter.
        
        @param txt virtual environment interpreter
        @type str
        """
        self.__updateOk()
    
    @pyqtSlot(bool)
    def on_globalCheckBox_toggled(self, checked):
        """
        Private slot handling a change of the global check box state.
        
        @param checked state of the check box
        @type bool
        """
        self.__updateOk()
    
    @pyqtSlot(bool)
    def on_remoteCheckBox_toggled(self, checked):
        """
        Private slot handling a change of the remote check box state.
        
        @param checked state of the check box
        @type bool
        """
        self.__updateOk()
    
    @pyqtSlot(bool)
    def on_anacondaCheckBox_clicked(self, checked):
        """
        Private slot handling a user click on this check box.
        
        @param checked state of the check box
        @type bool
        """
        if checked and not bool(self.execPathEdit.text()):
            # prepopulate the execPathEdit widget
            if Utilities.isWindowsPlatform():
                self.execPathEdit.setText(os.pathsep.join([
                    self.targetDirectoryPicker.text(),
                    os.path.join(self.targetDirectoryPicker.text(),
                                 "Scripts"),
                    os.path.join(self.targetDirectoryPicker.text(),
                                 "Library", "bin"),
                ]))
            else:
                self.execPathEdit.setText(
                    os.path.join(self.targetDirectoryPicker.text(),
                                 "bin"),
                )
    
    def getData(self):
        """
        Public method to retrieve the entered data.
        
        @return tuple containing the logical name, the directory, the
            interpreter of the virtual environment, the Python variant,
            a flag indicating a global environment, a flag indicating an
            Anaconda environment, aflag indicating a remotely accessed
            environment and a string to be prepended to the PATH environment
            variable
        @rtype tuple of (str, str, str, int, bool, bool, bool, str)
        """
        nativePaths = not self.remoteCheckBox.isChecked()
        return (
            self.nameEdit.text(),
            self.targetDirectoryPicker.text(toNative=nativePaths),
            self.pythonExecPicker.text(toNative=nativePaths),
            3 - self.variantComboBox.currentIndex(),
            self.globalCheckBox.isChecked(),
            self.anacondaCheckBox.isChecked(),
            self.remoteCheckBox.isChecked(),
            self.execPathEdit.text(),
        )
