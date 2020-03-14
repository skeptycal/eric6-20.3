# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Editor General configuration page.
"""

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QTreeWidgetItem, QHeaderView, QDialog
from PyQt5.Qsci import QsciScintillaBase

from E5Gui import E5MessageBox

from .ConfigurationPageBase import ConfigurationPageBase
from .Ui_EditorGeneralPage import Ui_EditorGeneralPage
from .EditorLanguageTabIndentOverrideDialog import (
    EditorLanguageTabIndentOverrideDialog
)

import Preferences
import UI.PixmapCache


class EditorGeneralPage(ConfigurationPageBase, Ui_EditorGeneralPage):
    """
    Class implementing the Editor General configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        super(EditorGeneralPage, self).__init__()
        self.setupUi(self)
        self.setObjectName("EditorGeneralPage")
        
        self.addButton.setIcon(UI.PixmapCache.getIcon("plus"))
        self.deleteButton.setIcon(UI.PixmapCache.getIcon("minus"))
        self.editButton.setIcon(UI.PixmapCache.getIcon("edit"))
        
        # set initial values
        self.tabwidthSlider.setValue(
            Preferences.getEditor("TabWidth"))
        self.indentwidthSlider.setValue(
            Preferences.getEditor("IndentWidth"))
        self.tabforindentationCheckBox.setChecked(
            Preferences.getEditor("TabForIndentation"))
        self.tabindentsCheckBox.setChecked(
            Preferences.getEditor("TabIndents"))
        self.converttabsCheckBox.setChecked(
            Preferences.getEditor("ConvertTabsOnLoad"))
        self.autoindentCheckBox.setChecked(
            Preferences.getEditor("AutoIndentation"))
        self.comment0CheckBox.setChecked(
            Preferences.getEditor("CommentColumn0"))
        
        virtualSpaceOptions = Preferences.getEditor("VirtualSpaceOptions")
        self.vsSelectionCheckBox.setChecked(
            virtualSpaceOptions & QsciScintillaBase.SCVS_RECTANGULARSELECTION)
        self.vsUserCheckBox.setChecked(
            virtualSpaceOptions & QsciScintillaBase.SCVS_USERACCESSIBLE)
        
        self.__populateLanguageOverrideWidget()
    
    def save(self):
        """
        Public slot to save the Editor General configuration.
        """
        Preferences.setEditor(
            "TabWidth",
            self.tabwidthSlider.value())
        Preferences.setEditor(
            "IndentWidth",
            self.indentwidthSlider.value())
        Preferences.setEditor(
            "TabForIndentation",
            self.tabforindentationCheckBox.isChecked())
        Preferences.setEditor(
            "TabIndents",
            self.tabindentsCheckBox.isChecked())
        Preferences.setEditor(
            "ConvertTabsOnLoad",
            self.converttabsCheckBox.isChecked())
        Preferences.setEditor(
            "AutoIndentation",
            self.autoindentCheckBox.isChecked())
        Preferences.setEditor(
            "CommentColumn0",
            self.comment0CheckBox.isChecked())
        
        virtualSpaceOptions = QsciScintillaBase.SCVS_NONE
        if self.vsSelectionCheckBox.isChecked():
            virtualSpaceOptions |= QsciScintillaBase.SCVS_RECTANGULARSELECTION
        if self.vsUserCheckBox.isChecked():
            virtualSpaceOptions |= QsciScintillaBase.SCVS_USERACCESSIBLE
        Preferences.setEditor("VirtualSpaceOptions", virtualSpaceOptions)
        
        self.__saveLanguageOverrides()
        
    def on_tabforindentationCheckBox_toggled(self, checked):
        """
        Private slot used to set the tab conversion check box.
        
        @param checked flag received from the signal (boolean)
        """
        if checked and self.converttabsCheckBox.isChecked():
            self.converttabsCheckBox.setChecked(not checked)
        self.converttabsCheckBox.setEnabled(not checked)
    
    def __populateLanguageOverrideWidget(self):
        """
        Private method to populate the language specific indentation and tab
        width override widget.
        """
        overrides = Preferences.getEditor("TabIndentOverride")
        for language, (tabWidth, indentWidth) in overrides.items():
            self.__createOverrideItem(language, tabWidth, indentWidth)
        self.languageOverrideWidget.sortItems(0, Qt.AscendingOrder)
        self.__resizeOverrideColumns()
        self.on_languageOverrideWidget_itemSelectionChanged()
    
    def __createOverrideItem(self, language, tabWidth, indentWidth):
        """
        Private method to create an entry for a language override.
        
        @param language name of the language
        @type str
        @param tabWidth tabulator width
        @type int
        @param indentWidth indentation width
        @type int
        """
        itm = QTreeWidgetItem(self.languageOverrideWidget, [
            language,
            "{0:2d}".format(tabWidth),
            "{0:2d}".format(indentWidth)])
        itm.setTextAlignment(1, Qt.AlignHCenter)
        itm.setTextAlignment(2, Qt.AlignHCenter)
        
    def __resizeOverrideColumns(self):
        """
        Private method to resize the list columns.
        """
        self.languageOverrideWidget.header().resizeSections(
            QHeaderView.ResizeToContents)
        self.languageOverrideWidget.header().setStretchLastSection(True)
    
    def __saveLanguageOverrides(self):
        """
        Private method to save the language specific indentation and tab width
        overrides.
        """
        overrides = {}
        for row in range(self.languageOverrideWidget.topLevelItemCount()):
            itm = self.languageOverrideWidget.topLevelItem(row)
            language = itm.text(0)
            overrides[language] = [
                int(itm.text(1)),
                int(itm.text(2)),
            ]
        
        Preferences.setEditor("TabIndentOverride", overrides)
    
    @pyqtSlot()
    def on_languageOverrideWidget_itemSelectionChanged(self):
        """
        Private slot handling a change of the override selection.
        """
        self.deleteButton.setEnabled(
            len(self.languageOverrideWidget.selectedItems()) > 0)
        self.editButton.setEnabled(
            len(self.languageOverrideWidget.selectedItems()) == 1)
    
    @pyqtSlot()
    def on_addButton_clicked(self):
        """
        Private slot to add a new override entry.
        """
        import QScintilla.Lexers
        languages = list(
            QScintilla.Lexers.getSupportedLanguages().keys())
        for row in range(self.languageOverrideWidget.topLevelItemCount()):
            itm = self.languageOverrideWidget.topLevelItem(row)
            language = itm.text(0)
            if language in languages:
                languages.remove(language)
        dlg = EditorLanguageTabIndentOverrideDialog(
            editMode=False,
            languages=languages,
            tabWidth=self.tabwidthSlider.value(),
            indentWidth=self.indentwidthSlider.value(),
        )
        if dlg.exec_() == QDialog.Accepted:
            language, tabWidth, indentWidth = dlg.getData()
            self.__createOverrideItem(language, tabWidth, indentWidth)
            self.languageOverrideWidget.sortItems(0, Qt.AscendingOrder)
            self.__resizeOverrideColumns()
    
    @pyqtSlot()
    def on_deleteButton_clicked(self):
        """
        Private slot to delete the selected override entries.
        """
        ok = E5MessageBox.yesNo(
            self,
            self.tr("Tab and Indent Override"),
            self.tr("""Shall the selected entries really be removed?"""))
        if ok:
            for itm in self.languageOverrideWidget.selectedItems():
                index = self.languageOverrideWidget.indexOfTopLevelItem(itm)
                self.languageOverrideWidget.takeTopLevelItem(index)
                del itm
    
    @pyqtSlot()
    def on_editButton_clicked(self):
        """
        Private slot to edit the selected override entry.
        """
        itm = self.languageOverrideWidget.selectedItems()[0]
        dlg = EditorLanguageTabIndentOverrideDialog(
            editMode=True,
            languages=[itm.text(0)],
            tabWidth=int(itm.text(1)),
            indentWidth=int(itm.text(2)),
        )
        if dlg.exec_() == QDialog.Accepted:
            language, tabWidth, indentWidth = dlg.getData()
            itm.setText(1, "{0:2d}".format(tabWidth))
            itm.setText(2, "{0:2d}".format(indentWidth))


def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    @return reference to the instantiated page (ConfigurationPageBase)
    """
    page = EditorGeneralPage()
    return page
