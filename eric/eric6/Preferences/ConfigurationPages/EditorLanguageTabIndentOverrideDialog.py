# -*- coding: utf-8 -*-

# Copyright (c) 2019 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to set the tab and indentation width override for
a language.
"""

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QDialogButtonBox

from .Ui_EditorLanguageTabIndentOverrideDialog import (
    Ui_EditorLanguageTabIndentOverrideDialog
)


class EditorLanguageTabIndentOverrideDialog(
    QDialog, Ui_EditorLanguageTabIndentOverrideDialog
):
    """
    Class implementing a dialog to set the tab and indentation width override
    for a language.
    """
    def __init__(self, *, editMode=False, languages=None, tabWidth=0,
                 indentWidth=0, parent=None):
        """
        Constructor
        
        @keyparam editMode flag indicating the edit mode (Note: in edit mode
            the language is fixed)
        @type bool
        @keyparam languages list of available languages
        @type list of str
        @keyparam tabWidth tab width to be set
        @type int
        @keyparam indentWidth indentation width to be set
        @type int
        @keyparam parent reference to the parent widget
        @type QWidget
        """
        super(EditorLanguageTabIndentOverrideDialog, self).__init__(parent)
        self.setupUi(self)
        
        if editMode:
            self.languageComboBox.addItems(languages)
        else:
            self.languageComboBox.addItems([""] + sorted(languages))
        self.tabWidthSpinBox.setValue(tabWidth)
        self.indentWidthSpinBox.setValue(indentWidth)
    
    def getData(self):
        """
        Public method to get the entered data.
        
        @return tuple containing the language, the tab width and the
            indentation width
        @rtype tuple of (str, int, int)
        """
        return (
            self.languageComboBox.currentText(),
            self.tabWidthSpinBox.value(),
            self.indentWidthSpinBox.value(),
        )
    
    @pyqtSlot(str)
    def on_languageComboBox_currentIndexChanged(self, lang):
        """
        Private slot to handle the selection of a language.
        
        @param lang selected language
        @type str
        """
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(
            bool(lang))
