# -*- coding: utf-8 -*-

# Copyright (c) 2016 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the JavaScript settings dialog.
"""


from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog

from .Ui_JavaScriptSettingsDialog import Ui_JavaScriptSettingsDialog

import Preferences


class JavaScriptSettingsDialog(QDialog, Ui_JavaScriptSettingsDialog):
    """
    Class implementing the JavaScript settings dialog.
    
    Note: it contains the JavaScript part of the web browser configuration
    dialog.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(JavaScriptSettingsDialog, self).__init__(parent)
        self.setupUi(self)
        
        self.javaScriptGroup.setChecked(
            Preferences.getWebBrowser("JavaScriptEnabled"))
        self.jsOpenWindowsCheckBox.setChecked(
            Preferences.getWebBrowser("JavaScriptCanOpenWindows"))
        try:
            # Qt 5.10
            self.jsActivateWindowsCheckBox.setChecked(
                Preferences.getWebBrowser(
                    "AllowWindowActivationFromJavaScript"))
        except KeyError:
            self.jsActivateWindowsCheckBox.setEnabled(False)
        self.jsClipboardCheckBox.setChecked(
            Preferences.getWebBrowser("JavaScriptCanAccessClipboard"))
        try:
            # Qt 5.11
            self.jsPasteCheckBox.setChecked(
                Preferences.getWebBrowser("JavaScriptCanPaste"))
        except KeyError:
            self.jsPasteCheckBox.setEnabled(False)
        
        msh = self.minimumSizeHint()
        self.resize(max(self.width(), msh.width()), msh.height())
    
    @pyqtSlot()
    def accept(self):
        """
        Public slot to accept the dialog.
        """
        Preferences.setWebBrowser(
            "JavaScriptEnabled",
            self.javaScriptGroup.isChecked())
        Preferences.setWebBrowser(
            "JavaScriptCanOpenWindows",
            self.jsOpenWindowsCheckBox.isChecked())
        if self.jsActivateWindowsCheckBox.isEnabled():
            Preferences.setWebBrowser(
                "AllowWindowActivationFromJavaScript",
                self.jsActivateWindowsCheckBox.isChecked())
        Preferences.setWebBrowser(
            "JavaScriptCanAccessClipboard",
            self.jsClipboardCheckBox.isChecked())
        if self.jsPasteCheckBox.isEnabled():
            Preferences.setWebBrowser(
                "JavaScriptCanPaste",
                self.jsPasteCheckBox.isChecked())
        
        Preferences.syncPreferences()
        
        super(JavaScriptSettingsDialog, self).accept()
