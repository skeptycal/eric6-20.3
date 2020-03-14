# -*- coding: utf-8 -*-

# Copyright (c) 2011 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to show the commit message of the current patch.
"""


import os

from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtWidgets import QDialog, QDialogButtonBox

from .Ui_HgQueuesHeaderDialog import Ui_HgQueuesHeaderDialog

import Utilities


class HgQueuesHeaderDialog(QDialog, Ui_HgQueuesHeaderDialog):
    """
    Class implementing a dialog to show the commit message of the current
    patch.
    """
    def __init__(self, vcs, parent=None):
        """
        Constructor
        
        @param vcs reference to the vcs object
        @param parent reference to the parent widget (QWidget)
        """
        super(HgQueuesHeaderDialog, self).__init__(parent)
        self.setupUi(self)
        
        self.buttonBox.button(QDialogButtonBox.Close).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Cancel).setDefault(True)
        
        self.vcs = vcs
        self.__hgClient = vcs.getClient()
        
        self.show()
        QCoreApplication.processEvents()
    
    def closeEvent(self, e):
        """
        Protected slot implementing a close event handler.
        
        @param e close event (QCloseEvent)
        """
        if self.__hgClient.isExecuting():
            self.__hgClient.cancel()
        
        e.accept()
    
    def start(self, path):
        """
        Public slot to start the list command.
        
        @param path name of directory to be listed (string)
        """
        self.activateWindow()
        
        dname, fname = self.vcs.splitPath(path)
        
        # find the root of the repo
        repodir = dname
        while not os.path.isdir(os.path.join(repodir, self.vcs.adminDir)):
            repodir = os.path.dirname(repodir)
            if os.path.splitdrive(repodir)[1] == os.sep:
                return
        
        args = self.vcs.initCommand("qheader")
        
        out, err = self.__hgClient.runcommand(
            args, output=self.__showOutput, error=self.__showError)
        if err:
            self.__showError(err)
        if out:
            self.__showOutPut(out)
        self.__finish()
    
    def __finish(self):
        """
        Private slot called when the process finished or the user pressed
        the button.
        """
        self.buttonBox.button(QDialogButtonBox.Close).setEnabled(True)
        self.buttonBox.button(QDialogButtonBox.Cancel).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Close).setDefault(True)
        self.buttonBox.button(QDialogButtonBox.Close).setFocus(
            Qt.OtherFocusReason)
    
    def on_buttonBox_clicked(self, button):
        """
        Private slot called by a button of the button box clicked.
        
        @param button button that was clicked (QAbstractButton)
        """
        if button == self.buttonBox.button(QDialogButtonBox.Close):
            self.close()
        elif button == self.buttonBox.button(QDialogButtonBox.Cancel):
            if self.__hgClient:
                self.__hgClient.cancel()
            else:
                self.__finish()
    
    def __showOutput(self, out):
        """
        Private slot to show some output.
        
        @param out output to be shown (string)
        """
        self.messageEdit.appendPlainText(Utilities.filterAnsiSequences(out))
    
    def __showError(self, out):
        """
        Private slot to show some error.
        
        @param out error to be shown (string)
        """
        self.messageEdit.appendPlainText(self.tr("Error: "))
        self.messageEdit.appendPlainText(Utilities.filterAnsiSequences(out))
