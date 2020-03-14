# -*- coding: utf-8 -*-

# Copyright (c) 2018 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to enter some non-common uic compiler options.
"""


from PyQt5.QtWidgets import QDialog

from .Ui_UicCompilerOptionsDialog import Ui_UicCompilerOptionsDialog


class UicCompilerOptionsDialog(QDialog, Ui_UicCompilerOptionsDialog):
    """
    Class implementing a dialog to enter some non-common uic compiler options.
    """
    def __init__(self, compilerOptions, compiler, parent=None):
        """
        Constructor
        
        @param compilerOptions dictionary containing the uic compiler options
        @type dict
        @param compiler name of the uic compiler executable
        @type str
        @param parent reference to the parent widget
        @type QWidget
        """
        super(UicCompilerOptionsDialog, self).__init__(parent)
        self.setupUi(self)
        
        self.packageEdit.setText(compilerOptions["Package"])
        self.packageRootEdit.setText(compilerOptions["PackagesRoot"])
        self.suffixEdit.setText(compilerOptions["RcSuffix"])
        
        if 'uic5' not in compiler:
            self.packageGroup.setEnabled(False)
        
        msh = self.minimumSizeHint()
        self.resize(max(self.width(), msh.width()), msh.height())
    
    def getData(self):
        """
        Public method to get the entered data.
        
        @return tuple containing the package, the rc-file suffix and the
            project relative root of the packages directory
        @rtype tuple of (str, str, str)
        """
        return (
            self.packageEdit.text().strip(),
            self.suffixEdit.text().strip(),
            self.packageRootEdit.text().strip(),
        )
