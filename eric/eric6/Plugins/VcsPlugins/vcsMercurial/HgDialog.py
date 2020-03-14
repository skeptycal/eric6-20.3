# -*- coding: utf-8 -*-

# Copyright (c) 2010 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog starting a process and showing its output.
"""

from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtWidgets import QDialog, QDialogButtonBox

from .Ui_HgDialog import Ui_HgDialog

import Preferences
import Utilities


class HgDialog(QDialog, Ui_HgDialog):
    """
    Class implementing a dialog starting a process and showing its output.
    
    It starts a QProcess and displays a dialog that
    shows the output of the process. The dialog is modal,
    which causes a synchronized execution of the process.
    """
    def __init__(self, text, hg=None, useClient=True, parent=None):
        """
        Constructor
        
        @param text text to be shown by the label (string)
        @param hg reference to the Mercurial interface object (Hg)
        @param useClient flag indicating to use the command server client
            if possible (boolean)
        @param parent parent widget (QWidget)
        """
        super(HgDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.Window)
        
        self.buttonBox.button(QDialogButtonBox.Close).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Cancel).setDefault(True)
        
        self.username = ''
        self.password = ''
        self.vcs = hg
        
        self.outputGroup.setTitle(text)
        
        self.show()
        QCoreApplication.processEvents()
    
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
        
        if (
            Preferences.getVCS("AutoClose") and
            self.normal and
            self.errors.toPlainText() == ""
        ):
            self.accept()
    
    def on_buttonBox_clicked(self, button):
        """
        Private slot called by a button of the button box clicked.
        
        @param button button that was clicked (QAbstractButton)
        """
        if button == self.buttonBox.button(QDialogButtonBox.Close):
            self.close()
        elif button == self.buttonBox.button(QDialogButtonBox.Cancel):
            self.vcs.getClient().cancel()
    
    def startProcess(self, args, workingDir=None, showArgs=True,
                     environment=None):
        """
        Public slot used to start the process.
        
        @param args list of arguments for the process (list of strings)
        @keyparam workingDir working directory for the process (string)
        @keyparam showArgs flag indicating to show the arguments (boolean)
        @keyparam environment dictionary of environment settings to add
            or change for the git process (dict of string and string)
        @return flag indicating a successful start of the process
        """
        self.errorGroup.hide()
        self.normal = False
        
        self.__hasAddOrDelete = False
        if (
            args[0] in ["fetch", "qpush", "qpop", "qgoto", "rebase",
                        "update", "import", "revert", "graft", "shelve",
                        "unshelve", "strip", "histedit"] or
            (args[0] in ["pull", "unbundle"] and
             ("--update" in args[1:] or "--rebase" in args[1:]))
        ):
            self.__updateCommand = True
        else:
            self.__updateCommand = False
        
        if showArgs:
            self.resultbox.append(' '.join(args))
            self.resultbox.append('')
        
        out, err = self.vcs.getClient().runcommand(
            args, output=self.__showOutput, error=self.__showError)
        
        if err:
            self.__showError(err)
        if out:
            self.__showOutput(out)
        
        self.normal = True
        
        self.__finish()
        
        return True
    
    def normalExit(self):
        """
        Public method to check for a normal process termination.
        
        @return flag indicating normal process termination (boolean)
        """
        return self.normal
    
    def normalExitWithoutErrors(self):
        """
        Public method to check for a normal process termination without
        error messages.
        
        @return flag indicating normal process termination (boolean)
        """
        return self.normal and self.errors.toPlainText() == ""
    
    def __showOutput(self, out):
        """
        Private slot to show some output.
        
        @param out output to be shown (string)
        """
        self.resultbox.insertPlainText(Utilities.filterAnsiSequences(out))
        self.resultbox.ensureCursorVisible()
        
        # check for a changed project file
        if self.__updateCommand:
            for line in out.splitlines():
                if '.e4p' in line:
                    self.__hasAddOrDelete = True
                    break
        
        QCoreApplication.processEvents()
    
    def __showError(self, out):
        """
        Private slot to show some error.
        
        @param out error to be shown (string)
        """
        self.errorGroup.show()
        self.errors.insertPlainText(Utilities.filterAnsiSequences(out))
        self.errors.ensureCursorVisible()
        
        QCoreApplication.processEvents()
    
    def hasAddOrDelete(self):
        """
        Public method to check, if the last action contained an add or delete.
        
        @return flag indicating the presence of an add or delete (boolean)
        """
        return self.__hasAddOrDelete
