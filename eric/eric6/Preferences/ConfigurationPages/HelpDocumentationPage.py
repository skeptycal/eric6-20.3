# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Help Documentation configuration page.
"""


from E5Gui.E5PathPicker import E5PathPickerModes

from .ConfigurationPageBase import ConfigurationPageBase
from .Ui_HelpDocumentationPage import Ui_HelpDocumentationPage

import Preferences
import Utilities


class HelpDocumentationPage(ConfigurationPageBase, Ui_HelpDocumentationPage):
    """
    Class implementing the Help Documentation configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        super(HelpDocumentationPage, self).__init__()
        self.setupUi(self)
        self.setObjectName("HelpDocumentationPage")
        
        self.ericDocDirPicker.setMode(E5PathPickerModes.OpenFileMode)
        self.ericDocDirPicker.setFilters(self.tr(
            "HTML Files (*.html *.htm);;All Files (*)"))
        self.python2DocDirPicker.setMode(E5PathPickerModes.OpenFileMode)
        self.python2DocDirPicker.setFilters(self.tr(
            "HTML Files (*.html *.htm);;"
            "Compressed Help Files (*.chm);;"
            "All Files (*)"))
        self.pythonDocDirPicker.setMode(E5PathPickerModes.OpenFileMode)
        self.pythonDocDirPicker.setFilters(self.tr(
            "HTML Files (*.html *.htm);;"
            "Compressed Help Files (*.chm);;"
            "All Files (*)"))
        self.qt4DocDirPicker.setMode(E5PathPickerModes.OpenFileMode)
        self.qt4DocDirPicker.setFilters(self.tr(
            "HTML Files (*.html *.htm);;All Files (*)"))
        self.qt5DocDirPicker.setMode(E5PathPickerModes.OpenFileMode)
        self.qt5DocDirPicker.setFilters(self.tr(
            "HTML Files (*.html *.htm);;All Files (*)"))
        self.pyqt4DocDirPicker.setMode(E5PathPickerModes.OpenFileMode)
        self.pyqt4DocDirPicker.setFilters(self.tr(
            "HTML Files (*.html *.htm);;All Files (*)"))
        self.pyqt5DocDirPicker.setMode(E5PathPickerModes.OpenFileMode)
        self.pyqt5DocDirPicker.setFilters(self.tr(
            "HTML Files (*.html *.htm);;All Files (*)"))
        self.pysideDocDirPicker.setMode(E5PathPickerModes.OpenFileMode)
        self.pysideDocDirPicker.setFilters(self.tr(
            "HTML Files (*.html *.htm);;All Files (*)"))
        self.pyside2DocDirPicker.setMode(E5PathPickerModes.OpenFileMode)
        self.pyside2DocDirPicker.setFilters(self.tr(
            "HTML Files (*.html *.htm);;All Files (*)"))
        
        pyside_py2, pyside_py3 = Utilities.checkPyside("1")
        if pyside_py2 or pyside_py3:
            self.pysideGroup.setEnabled(True)
        else:
            self.pysideGroup.setEnabled(False)
        
        pyside2_py2, pyside2_py3 = Utilities.checkPyside("2")
        if pyside2_py2 or pyside2_py3:
            self.pyside2Group.setEnabled(True)
        else:
            self.pyside2Group.setEnabled(False)
        
        # set initial values
        self.ericDocDirPicker.setText(
            Preferences.getHelp("EricDocDir"), toNative=False)
        self.python2DocDirPicker.setText(
            Preferences.getHelp("Python2DocDir"), toNative=False)
        self.pythonDocDirPicker.setText(
            Preferences.getHelp("PythonDocDir"), toNative=False)
        self.qt4DocDirPicker.setText(
            Preferences.getHelp("Qt4DocDir"), toNative=False)
        self.qt5DocDirPicker.setText(
            Preferences.getHelp("Qt5DocDir"), toNative=False)
        self.pyqt4DocDirPicker.setText(
            Preferences.getHelp("PyQt4DocDir"), toNative=False)
        self.pyqt5DocDirPicker.setText(
            Preferences.getHelp("PyQt5DocDir"), toNative=False)
        self.pysideDocDirPicker.setText(
            Preferences.getHelp("PySideDocDir"), toNative=False)
        self.pyside2DocDirPicker.setText(
            Preferences.getHelp("PySide2DocDir"), toNative=False)
        
    def save(self):
        """
        Public slot to save the Help Documentation configuration.
        """
        Preferences.setHelp(
            "EricDocDir",
            self.ericDocDirPicker.text(toNative=False))
        Preferences.setHelp(
            "Python2DocDir",
            self.python2DocDirPicker.text(toNative=False))
        Preferences.setHelp(
            "PythonDocDir",
            self.pythonDocDirPicker.text(toNative=False))
        Preferences.setHelp(
            "Qt4DocDir",
            self.qt4DocDirPicker.text(toNative=False))
        Preferences.setHelp(
            "Qt5DocDir",
            self.qt5DocDirPicker.text(toNative=False))
        Preferences.setHelp(
            "PyQt4DocDir",
            self.pyqt4DocDirPicker.text(toNative=False))
        Preferences.setHelp(
            "PyQt5DocDir",
            self.pyqt5DocDirPicker.text(toNative=False))
        Preferences.setHelp(
            "PySideDocDir",
            self.pysideDocDirPicker.text(toNative=False))
        Preferences.setHelp(
            "PySide2DocDir",
            self.pyside2DocDirPicker.text(toNative=False))
    

def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    @return reference to the instantiated page (ConfigurationPageBase)
    """
    page = HelpDocumentationPage()
    return page
