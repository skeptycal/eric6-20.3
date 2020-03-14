# -*- coding: utf-8 -*-

# Copyright (c) 2019 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the pip packages management widget.
"""


import textwrap
import os

from PyQt5.QtCore import pyqtSlot, Qt, QEventLoop, QRegExp
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (
    QWidget, QToolButton, QApplication, QHeaderView, QTreeWidgetItem,
    QInputDialog, QMenu, QDialog
)

from E5Gui.E5Application import e5App
from E5Gui import E5MessageBox

from E5Network.E5XmlRpcClient import E5XmlRpcClient

from .Ui_PipPackagesWidget import Ui_PipPackagesWidget

import UI.PixmapCache


class PipPackagesWidget(QWidget, Ui_PipPackagesWidget):
    """
    Class implementing the pip packages management widget.
    """
    ShowProcessGeneralMode = 0
    ShowProcessClassifiersMode = 1
    ShowProcessEntryPointsMode = 2
    ShowProcessFilesListMode = 3
    
    SearchStopwords = {
        "a", "and", "are", "as", "at", "be", "but", "by",
        "for", "if", "in", "into", "is", "it",
        "no", "not", "of", "on", "or", "such",
        "that", "the", "their", "then", "there", "these",
        "they", "this", "to", "was", "will",
    }
    SearchVersionRole = Qt.UserRole + 1
    
    def __init__(self, pip, parent=None):
        """
        Constructor
        
        @param pip reference to the global pip interface
        @type Pip
        @param parent reference to the parent widget
        @type QWidget
        """
        super(PipPackagesWidget, self).__init__(parent)
        self.setupUi(self)
        
        self.pipMenuButton.setObjectName(
            "pip_supermenu_button")
        self.pipMenuButton.setIcon(UI.PixmapCache.getIcon("superMenu"))
        self.pipMenuButton.setToolTip(self.tr("pip Menu"))
        self.pipMenuButton.setPopupMode(QToolButton.InstantPopup)
        self.pipMenuButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.pipMenuButton.setFocusPolicy(Qt.NoFocus)
        self.pipMenuButton.setAutoRaise(True)
        self.pipMenuButton.setShowMenuInside(True)
        
        self.refreshButton.setIcon(UI.PixmapCache.getIcon("reload"))
        self.upgradeButton.setIcon(UI.PixmapCache.getIcon("1uparrow"))
        self.upgradeAllButton.setIcon(UI.PixmapCache.getIcon("2uparrow"))
        self.uninstallButton.setIcon(UI.PixmapCache.getIcon("minus"))
        self.showPackageDetailsButton.setIcon(UI.PixmapCache.getIcon("info"))
        self.searchToggleButton.setIcon(UI.PixmapCache.getIcon("find"))
        self.searchButton.setIcon(UI.PixmapCache.getIcon("findNext"))
        self.installButton.setIcon(UI.PixmapCache.getIcon("plus"))
        self.installUserSiteButton.setIcon(UI.PixmapCache.getIcon("addUser"))
        self.showDetailsButton.setIcon(UI.PixmapCache.getIcon("info"))
        
        self.__pip = pip
        self.__client = E5XmlRpcClient(self.__pip.getIndexUrlXml(), self)
        
        self.packagesList.header().setSortIndicator(0, Qt.AscendingOrder)
        
        self.__infoLabels = {
            "name": self.tr("Name:"),
            "version": self.tr("Version:"),
            "location": self.tr("Location:"),
            "requires": self.tr("Requires:"),
            "summary": self.tr("Summary:"),
            "home-page": self.tr("Homepage:"),
            "author": self.tr("Author:"),
            "author-email": self.tr("Author Email:"),
            "license": self.tr("License:"),
            "metadata-version": self.tr("Metadata Version:"),
            "installer": self.tr("Installer:"),
            "classifiers": self.tr("Classifiers:"),
            "entry-points": self.tr("Entry Points:"),
            "files": self.tr("Files:"),
        }
        self.infoWidget.setHeaderLabels(["Key", "Value"])
        
        venvManager = e5App().getObject("VirtualEnvManager")
        venvManager.virtualEnvironmentAdded.connect(
            self.on_refreshButton_clicked)
        venvManager.virtualEnvironmentRemoved.connect(
            self.on_refreshButton_clicked)
        
        project = e5App().getObject("Project")
        project.projectOpened.connect(
            self.on_refreshButton_clicked)
        project.projectClosed.connect(
            self.on_refreshButton_clicked)
        
        self.__initPipMenu()
        self.__populateEnvironments()
        self.__updateActionButtons()
        
        self.statusLabel.hide()
        self.searchWidget.hide()
        
        self.__queryName = []
        self.__querySummary = []
        
        self.__packageDetailsDialog = None
    
    def __populateEnvironments(self):
        """
        Private method to get a list of environments and populate the selector.
        """
        self.environmentsComboBox.addItem("")
        projectVenv = self.__pip.getProjectEnvironmentString()
        if projectVenv:
            self.environmentsComboBox.addItem(projectVenv)
        self.environmentsComboBox.addItems(
            self.__pip.getVirtualenvNames(noRemote=True))
    
    def __isPipAvailable(self):
        """
        Private method to check, if the pip package is available for the
        selected environment.
        
        @return flag indicating availability
        @rtype bool
        """
        available = False
        
        venvName = self.environmentsComboBox.currentText()
        if venvName:
            available = len(self.packagesList.findItems(
                "pip", Qt.MatchExactly | Qt.MatchCaseSensitive)) == 1
        
        return available
    
    #######################################################################
    ## Slots handling widget signals below
    #######################################################################
    
    def __selectedUpdateableItems(self):
        """
        Private method to get a list of selected items that can be updated.
        
        @return list of selected items that can be updated
        @rtype list of QTreeWidgetItem
        """
        return [
            itm for itm in self.packagesList.selectedItems()
            if bool(itm.text(2))
        ]
    
    def __allUpdateableItems(self):
        """
        Private method to get a list of all items that can be updated.
        
        @return list of all items that can be updated
        @rtype list of QTreeWidgetItem
        """
        updateableItems = []
        for index in range(self.packagesList.topLevelItemCount()):
            itm = self.packagesList.topLevelItem(index)
            if itm.text(2):
                updateableItems.append(itm)
        
        return updateableItems
    
    def __updateActionButtons(self):
        """
        Private method to set the state of the action buttons.
        """
        if self.__isPipAvailable():
            self.upgradeButton.setEnabled(
                bool(self.__selectedUpdateableItems()))
            self.uninstallButton.setEnabled(
                bool(self.packagesList.selectedItems()))
            self.upgradeAllButton.setEnabled(
                bool(self.__allUpdateableItems()))
            self.showPackageDetailsButton.setEnabled(
                len(self.packagesList.selectedItems()) == 1)
        else:
            self.upgradeButton.setEnabled(False)
            self.uninstallButton.setEnabled(False)
            self.upgradeAllButton.setEnabled(False)
            self.showPackageDetailsButton.setEnabled(False)
    
    def __refreshPackagesList(self):
        """
        Private method to referesh the packages list.
        """
        self.packagesList.clear()
        venvName = self.environmentsComboBox.currentText()
        if venvName:
            interpreter = self.__pip.getVirtualenvInterpreter(venvName)
            if interpreter:
                QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
                self.statusLabel.show()
                self.statusLabel.setText(
                    self.tr("Getting installed packages..."))
                QApplication.processEvents()
                
                # 1. populate with installed packages
                self.packagesList.setUpdatesEnabled(False)
                installedPackages = self.__pip.getInstalledPackages(
                    venvName,
                    localPackages=self.localCheckBox.isChecked(),
                    notRequired=self.notRequiredCheckBox.isChecked(),
                    usersite=self.userCheckBox.isChecked(),
                )
                for package, version in installedPackages:
                    QTreeWidgetItem(self.packagesList, [package, version])
                self.packagesList.setUpdatesEnabled(True)
                self.statusLabel.setText(
                    self.tr("Getting outdated packages..."))
                QApplication.processEvents()
                
                # 2. update with update information
                self.packagesList.setUpdatesEnabled(False)
                outdatedPackages = self.__pip.getOutdatedPackages(
                    venvName,
                    localPackages=self.localCheckBox.isChecked(),
                    notRequired=self.notRequiredCheckBox.isChecked(),
                    usersite=self.userCheckBox.isChecked(),
                )
                for package, _version, latest in outdatedPackages:
                    items = self.packagesList.findItems(
                        package, Qt.MatchExactly | Qt.MatchCaseSensitive)
                    if items:
                        itm = items[0]
                        itm.setText(2, latest)
                
                self.packagesList.sortItems(0, Qt.AscendingOrder)
                for col in range(self.packagesList.columnCount()):
                    self.packagesList.resizeColumnToContents(col)
                self.packagesList.setUpdatesEnabled(True)
                QApplication.restoreOverrideCursor()
                self.statusLabel.hide()
        
        self.__updateActionButtons()
        self.__updateSearchActionButtons()
        self.__updateSearchButton()
    
    @pyqtSlot(int)
    def on_environmentsComboBox_currentIndexChanged(self, index):
        """
        Private slot handling the selection of a Python environment.
        
        @param index index of the selected Python environment
        @type int
        """
        self.__refreshPackagesList()
    
    @pyqtSlot(bool)
    def on_localCheckBox_clicked(self, checked):
        """
        Private slot handling the switching of the local mode.
        
        @param checked state of the local check box
        @type bool
        """
        self.__refreshPackagesList()
    
    @pyqtSlot(bool)
    def on_notRequiredCheckBox_clicked(self, checked):
        """
        Private slot handling the switching of the 'not required' mode.
        
        @param checked state of the 'not required' check box
        @type bool
        """
        self.__refreshPackagesList()
    
    @pyqtSlot(bool)
    def on_userCheckBox_clicked(self, checked):
        """
        Private slot handling the switching of the 'user-site' mode.
        
        @param checked state of the 'user-site' check box
        @type bool
        """
        self.__refreshPackagesList()
    
    @pyqtSlot()
    def on_packagesList_itemSelectionChanged(self):
        """
        Private slot handling the selection of a package.
        """
        self.infoWidget.clear()
        
        if len(self.packagesList.selectedItems()) == 1:
            itm = self.packagesList.selectedItems()[0]
            
            environment = self.environmentsComboBox.currentText()
            interpreter = self.__pip.getVirtualenvInterpreter(environment)
            if not interpreter:
                return
            
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            args = ["-m", "pip", "show"]
            if self.verboseCheckBox.isChecked():
                args.append("--verbose")
            if self.installedFilesCheckBox.isChecked():
                args.append("--files")
            args.append(itm.text(0))
            success, output = self.__pip.runProcess(args, interpreter)
            
            if success and output:
                mode = self.ShowProcessGeneralMode
                for line in output.splitlines():
                    line = line.rstrip()
                    if line != "---":
                        if mode != self.ShowProcessGeneralMode:
                            if line[0] == " ":
                                QTreeWidgetItem(
                                    self.infoWidget,
                                    [" ", line.strip()])
                            else:
                                mode = self.ShowProcessGeneralMode
                        if mode == self.ShowProcessGeneralMode:
                            try:
                                label, info = line.split(": ", 1)
                            except ValueError:
                                label = line[:-1]
                                info = ""
                            label = label.lower()
                            if label in self.__infoLabels:
                                QTreeWidgetItem(
                                    self.infoWidget,
                                    [self.__infoLabels[label], info])
                            if label == "files":
                                mode = self.ShowProcessFilesListMode
                            elif label == "classifiers":
                                mode = self.ShowProcessClassifiersMode
                            elif label == "entry-points":
                                mode = self.ShowProcessEntryPointsMode
                self.infoWidget.scrollToTop()
            
            header = self.infoWidget.header()
            header.setStretchLastSection(False)
            header.resizeSections(QHeaderView.ResizeToContents)
            if header.sectionSize(0) + header.sectionSize(1) < header.width():
                header.setStretchLastSection(True)
            
            QApplication.restoreOverrideCursor()
        
        self.__updateActionButtons()
    
    @pyqtSlot(QTreeWidgetItem, int)
    def on_packagesList_itemActivated(self, item, column):
        """
        Private slot reacting on a package item activation.
        
        @param item reference to the activated item
        @type QTreeWidgetItem
        @param column activated column
        @type int
        """
        packageName = item.text(0)
        if column == 1:
            # show details for installed version
            packageVersion = item.text(1)
        else:
            # show details for available version or installed one
            if item.text(2):
                packageVersion = item.text(2)
            else:
                packageVersion = item.text(1)
        
        self.__showPackageDetails(packageName, packageVersion)
    
    @pyqtSlot(bool)
    def on_verboseCheckBox_clicked(self, checked):
        """
        Private slot to handle a change of the verbose package information
        checkbox.
        
        @param checked state of the checkbox
        @type bool
        """
        self.on_packagesList_itemSelectionChanged()
    
    @pyqtSlot(bool)
    def on_installedFilesCheckBox_clicked(self, checked):
        """
        Private slot to handle a change of the installed files information
        checkbox.
        
        @param checked state of the checkbox
        @type bool
        """
        self.on_packagesList_itemSelectionChanged()
    
    @pyqtSlot()
    def on_refreshButton_clicked(self):
        """
        Private slot to refresh the display.
        """
        currentEnvironment = self.environmentsComboBox.currentText()
        self.environmentsComboBox.clear()
        self.packagesList.clear()
        
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        QApplication.processEvents()
        
        self.__populateEnvironments()
        
        index = self.environmentsComboBox.findText(
            currentEnvironment, Qt.MatchExactly | Qt.MatchCaseSensitive)
        if index != -1:
            self.environmentsComboBox.setCurrentIndex(index)
        
        QApplication.restoreOverrideCursor()
        self.__updateActionButtons()
    
    @pyqtSlot()
    def on_upgradeButton_clicked(self):
        """
        Private slot to upgrade selected packages of the selected environment.
        """
        packages = [itm.text(0) for itm in self.__selectedUpdateableItems()]
        if packages:
            ok = self.__executeUpgradePackages(packages)
            if ok:
                self.on_refreshButton_clicked()
    
    @pyqtSlot()
    def on_upgradeAllButton_clicked(self):
        """
        Private slot to upgrade all packages of the selected environment.
        """
        packages = [itm.text(0) for itm in self.__allUpdateableItems()]
        if packages:
            ok = self.__executeUpgradePackages(packages)
            if ok:
                self.on_refreshButton_clicked()
    
    @pyqtSlot()
    def on_uninstallButton_clicked(self):
        """
        Private slot to remove selected packages of the selected environment.
        """
        packages = [itm.text(0) for itm in self.packagesList.selectedItems()]
        if packages:
            ok = self.__pip.uninstallPackages(
                packages,
                venvName=self.environmentsComboBox.currentText())
            if ok:
                self.on_refreshButton_clicked()
    
    def __executeUpgradePackages(self, packages):
        """
        Private method to execute the pip upgrade command.
        
        @param packages list of package names to be upgraded
        @type list of str
        @return flag indicating success
        @rtype bool
        """
        ok = self.__pip.upgradePackages(
            packages, venvName=self.environmentsComboBox.currentText(),
            userSite=self.userCheckBox.isChecked())
        return ok
    
    @pyqtSlot()
    def on_showPackageDetailsButton_clicked(self):
        """
        Private slot to show information for the selected package.
        """
        item = self.packagesList.selectedItems()[0]
        if item:
            packageName = item.text(0)
            # show details for available version or installed one
            if item.text(2):
                packageVersion = item.text(2)
            else:
                packageVersion = item.text(1)
            
            self.__showPackageDetails(packageName, packageVersion)
    
    #######################################################################
    ## Search widget related methods below
    #######################################################################
    
    def __updateSearchActionButtons(self):
        """
        Private method to update the action button states of the search widget.
        """
        installEnable = (
            len(self.searchResultList.selectedItems()) > 0 and
            self.environmentsComboBox.currentIndex() > 0 and
            self.__isPipAvailable()
        )
        self.installButton.setEnabled(installEnable)
        self.installUserSiteButton.setEnabled(installEnable)
        
        self.showDetailsButton.setEnabled(
            len(self.searchResultList.selectedItems()) == 1 and
            self.__isPipAvailable()
        )
    
    def __updateSearchButton(self):
        """
        Private method to update the state of the search button.
        """
        self.searchButton.setEnabled(
            (bool(self.searchEditName.text()) or
             bool(self.searchEditSummary.text())) and
            self.__isPipAvailable()
        )
    
    @pyqtSlot(bool)
    def on_searchToggleButton_toggled(self, checked):
        """
        Private slot to togle the search widget.
        
        @param checked state of the search widget button
        @type bool
        """
        self.searchWidget.setVisible(checked)
        
        if checked:
            self.searchEditName.setFocus(Qt.OtherFocusReason)
            self.searchEditName.selectAll()
            
            self.__updateSearchActionButtons()
            self.__updateSearchButton()
    
    @pyqtSlot(str)
    def on_searchEditName_textChanged(self, txt):
        """
        Private slot handling a change of the search term.
        
        @param txt search term
        @type str
        """
        self.__updateSearchButton()
    
    @pyqtSlot()
    def on_searchEditName_returnPressed(self):
        """
        Private slot initiating a search via a press of the Return key.
        """
        self.__search()
    
    @pyqtSlot(str)
    def on_searchEditSummary_textChanged(self, txt):
        """
        Private slot handling a change of the search term.
        
        @param txt search term
        @type str
        """
        self.__updateSearchButton()
    
    @pyqtSlot()
    def on_searchEditSummary_returnPressed(self):
        """
        Private slot initiating a search via a press of the Return key.
        """
        self.__search()
    
    @pyqtSlot()
    def on_searchButton_clicked(self):
        """
        Private slot handling a press of the search button.
        """
        self.__search()
    
    @pyqtSlot()
    def on_searchResultList_itemSelectionChanged(self):
        """
        Private slot handling changes of the search result selection.
        """
        self.__updateSearchActionButtons()
    
    def __search(self):
        """
        Private method to perform the search.
        """
        self.searchResultList.clear()
        self.searchInfoLabel.clear()
        
        self.searchButton.setEnabled(False)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        QApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
        
        self.__queryName = [
            term for term in self.searchEditName.text().strip().split()
            if term not in self.SearchStopwords
        ]
        self.__querySummary = [
            term for term in self.searchEditSummary.text().strip().split()
            if term not in self.SearchStopwords
        ]
        self.__client.call(
            "search",
            ({"name": self.__queryName,
              "summary": self.__querySummary},
             self.searchTermCombineComboBox.currentText()),
            self.__processSearchResult,
            self.__searchError
        )
    
    def __processSearchResult(self, data):
        """
        Private method to process the search result data from PyPI.
        
        @param data result data with hits in the first element
        @type tuple
        """
        if data:
            packages = self.__transformHits(data[0])
            if packages:
                self.searchInfoLabel.setText(
                    self.tr("%n package(s) found.", "", len(packages)))
                wrapper = textwrap.TextWrapper(width=80)
                count = 0
                total = 0
                for package in packages:
                    itm = QTreeWidgetItem(
                        self.searchResultList, [
                            package['name'].strip(),
                            "{0:4d}".format(package['score']),
                            "\n".join([
                                wrapper.fill(line) for line in
                                package['summary'].strip().splitlines()
                            ])
                        ])
                    itm.setData(0, self.SearchVersionRole, package['version'])
                    count += 1
                    total += 1
                    if count == 100:
                        count = 0
                        QApplication.processEvents()
            else:
                QApplication.restoreOverrideCursor()
                E5MessageBox.warning(
                    self,
                    self.tr("Search PyPI"),
                    self.tr("""<p>The package search did not return"""
                            """ anything.</p>"""))
                self.searchInfoLabel.setText(
                    self.tr("""<p>The package search did not return"""
                            """ anything.</p>"""))
        else:
            QApplication.restoreOverrideCursor()
            E5MessageBox.warning(
                self,
                self.tr("Search PyPI"),
                self.tr("""<p>The package search did not return anything."""
                        """</p>"""))
            self.searchInfoLabel.setText(
                self.tr("""<p>The package search did not return anything."""
                        """</p>"""))
        
        header = self.searchResultList.header()
        self.searchResultList.sortItems(1, Qt.DescendingOrder)
        header.setStretchLastSection(False)
        header.resizeSections(QHeaderView.ResizeToContents)
        headerSize = 0
        for col in range(header.count()):
            headerSize += header.sectionSize(col)
        if headerSize < header.width():
            header.setStretchLastSection(True)
        
        self.__finishSearch()
    
    def __finishSearch(self):
        """
        Private slot performing the search finishing actions.
        """
        QApplication.restoreOverrideCursor()
        
        self.__updateSearchActionButtons()
        self.__updateSearchButton()
        
        self.searchEditName.setFocus(Qt.OtherFocusReason)
    
    def __searchError(self, errorCode, errorString):
        """
        Private method handling a search error.
        
        @param errorCode code of the error
        @type int
        @param errorString error message
        @type str
        """
        self.__finish()
        E5MessageBox.warning(
            self,
            self.tr("Search PyPI"),
            self.tr("""<p>The package search failed.</p><p>Reason: {0}</p>""")
            .format(errorString))
        self.searchInfoLabel.setText(self.tr("Error: {0}").format(errorString))
    
    def __transformHits(self, hits):
        """
        Private method to convert the list returned from pypi into a
        packages list.
        
        @param hits list returned from pypi
        @type list of dict
        @return list of packages
        @rtype list of dict
        """
        # we only include the record with the highest score
        packages = {}
        for hit in hits:
            name = hit['name'].strip()
            summary = (hit['summary'] or "").strip()
            version = hit['version'].strip()
            score = self.__score(name, summary)
            # cleanup the summary
            if summary in ["UNKNOWN", "."]:
                summary = ""

            if name not in packages:
                packages[name] = {
                    'name': name,
                    'summary': summary,
                    'version': [version.strip()],
                    'score': score}
            else:
                if score > packages[name]['score']:
                    packages[name]['score'] = score
                    packages[name]['summary'] = summary
                packages[name]['version'].append(version.strip())

        return list(packages.values())
    
    def __score(self, name, summary):
        """
        Private method to calculate some score for a search result.
        
        @param name name of the returned package
        @type str
        @param summary summary text for the package
        @type str
        @return score value
        @rtype int
        """
        score = 0
        for queryTerm in self.__queryName:
            if queryTerm.lower() in name.lower():
                score += 4
                if queryTerm.lower() == name.lower():
                    score += 4
            
        for queryTerm in self.__querySummary:
            if queryTerm.lower() in summary.lower():
                if QRegExp(r'\b{0}\b'.format(QRegExp.escape(queryTerm)),
                           Qt.CaseInsensitive).indexIn(summary) != -1:
                    # word match gets even higher score
                    score += 2
                else:
                    score += 1
        
        return score
    
    @pyqtSlot()
    def on_installButton_clicked(self):
        """
        Private slot to handle pressing the Install button..
        """
        self.__install()
    
    @pyqtSlot()
    def on_installUserSiteButton_clicked(self):
        """
        Private slot to handle pressing the Install to User-Site button..
        """
        self.__install(userSite=True)
    
    def __install(self, userSite=False):
        """
        Private slot to install the selected packages.
        
        @param userSite flag indicating to install to the user directory
        @type bool
        """
        venvName = self.environmentsComboBox.currentText()
        if venvName:
            packages = []
            for itm in self.searchResultList.selectedItems():
                packages.append(itm.text(0).strip())
            if packages:
                self.__pip.installPackages(packages, venvName=venvName,
                                           userSite=userSite)
    
    @pyqtSlot()
    def on_showDetailsButton_clicked(self):
        """
        Private slot to handle pressing the Show Details button.
        """
        self.__showSearchedDetails()
    
    @pyqtSlot(QTreeWidgetItem, int)
    def on_searchResultList_itemActivated(self, item, column):
        """
        Private slot reacting on an search result item activation.
        
        @param item reference to the activated item
        @type QTreeWidgetItem
        @param column activated column
        @type int
        """
        self.__showSearchedDetails(item)
    
    def __showSearchedDetails(self, item=None):
        """
        Private slot to show details about the selected search result package.
        
        @param item reference to the search result item to show details for
        @type QTreeWidgetItem
        """
        self.showDetailsButton.setEnabled(False)
        
        if not item:
            item = self.searchResultList.selectedItems()[0]
        
        packageVersions = item.data(0, self.SearchVersionRole)
        if len(packageVersions) == 1:
            packageVersion = packageVersions[0]
        elif len(packageVersions) == 0:
            packageVersion = ""
        else:
            packageVersion, ok = QInputDialog.getItem(
                self,
                self.tr("Show Package Details"),
                self.tr("Select the package version:"),
                packageVersions,
                0, False)
            if not ok:
                return
        packageName = item.text(0)
        
        self.__showPackageDetails(packageName, packageVersion)
    
    def __showPackageDetails(self, packageName, packageVersion):
        """
        Private method to populate the package details dialog.
        
        @param packageName name of the package to show details for
        @type str
        @param packageVersion version of the package
        @type str
        """
        QApplication.setOverrideCursor(Qt.WaitCursor)
        QApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
        
        packageData = self.__pip.getPackageDetails(packageName, packageVersion)
        
        QApplication.restoreOverrideCursor()
        if packageData:
            from .PipPackageDetailsDialog import PipPackageDetailsDialog
            
            self.showDetailsButton.setEnabled(True)
            
            if self.__packageDetailsDialog is not None:
                self.__packageDetailsDialog.close()
            
            self.__packageDetailsDialog = (
                PipPackageDetailsDialog(packageData, self)
            )
            self.__packageDetailsDialog.show()
        else:
            E5MessageBox.warning(
                self,
                self.tr("Search PyPI"),
                self.tr("""<p>No package details info for <b>{0}</b>"""
                        """ available.</p>""").format(packageName))
    
    #######################################################################
    ## Menu related methods below
    #######################################################################
        
    def __initPipMenu(self):
        """
        Private method to create the super menu and attach it to the super
        menu button.
        """
        self.__pipMenu = QMenu()
        self.__installPipAct = self.__pipMenu.addAction(
            self.tr("Install Pip"),
            self.__installPip)
        self.__installPipUserAct = self.__pipMenu.addAction(
            self.tr("Install Pip to User-Site"),
            self.__installPipUser)
        self.__repairPipAct = self.__pipMenu.addAction(
            self.tr("Repair Pip"),
            self.__repairPip)
        self.__pipMenu.addSeparator()
        self.__installPackagesAct = self.__pipMenu.addAction(
            self.tr("Install Packages"),
            self.__installPackages)
        self.__installLocalPackageAct = self.__pipMenu.addAction(
            self.tr("Install Local Package"),
            self.__installLocalPackage)
        self.__pipMenu.addSeparator()
        self.__installRequirementsAct = self.__pipMenu.addAction(
            self.tr("Install Requirements"),
            self.__installRequirements)
        self.__uninstallRequirementsAct = self.__pipMenu.addAction(
            self.tr("Uninstall Requirements"),
            self.__uninstallRequirements)
        self.__generateRequirementsAct = self.__pipMenu.addAction(
            self.tr("Generate Requirements..."),
            self.__generateRequirements)
        self.__pipMenu.addSeparator()
        # editUserConfigAct
        self.__pipMenu.addAction(
            self.tr("Edit User Configuration..."),
            self.__editUserConfiguration)
        self.__editVirtualenvConfigAct = self.__pipMenu.addAction(
            self.tr("Edit Environment Configuration..."),
            self.__editVirtualenvConfiguration)
        self.__pipMenu.addSeparator()
        # pipConfigAct
        self.__pipMenu.addAction(
            self.tr("Configure..."),
            self.__pipConfigure)

        self.__pipMenu.aboutToShow.connect(self.__aboutToShowPipMenu)
        
        self.pipMenuButton.setMenu(self.__pipMenu)
    
    def __aboutToShowPipMenu(self):
        """
        Private slot to set the action enabled status.
        """
        enable = bool(self.environmentsComboBox.currentText())
        enablePip = self.__isPipAvailable()
        
        self.__installPipAct.setEnabled(not enablePip)
        self.__installPipUserAct.setEnabled(not enablePip)
        self.__repairPipAct.setEnabled(enablePip)
        
        self.__installPackagesAct.setEnabled(enablePip)
        self.__installLocalPackageAct.setEnabled(enablePip)
        
        self.__installRequirementsAct.setEnabled(enablePip)
        self.__uninstallRequirementsAct.setEnabled(enablePip)
        self.__generateRequirementsAct.setEnabled(enablePip)
        
        self.__editVirtualenvConfigAct.setEnabled(enable)
    
    @pyqtSlot()
    def __installPip(self):
        """
        Private slot to install pip into the selected environment.
        """
        venvName = self.environmentsComboBox.currentText()
        if venvName:
            self.__pip.installPip(venvName)
    
    @pyqtSlot()
    def __installPipUser(self):
        """
        Private slot to install pip into the user site for the selected
        environment.
        """
        venvName = self.environmentsComboBox.currentText()
        if venvName:
            self.__pip.installPip(venvName, userSite=True)
    
    @pyqtSlot()
    def __repairPip(self):
        """
        Private slot to repair the pip installation of the selected
        environment.
        """
        venvName = self.environmentsComboBox.currentText()
        if venvName:
            self.__pip.repairPip(venvName)
    
    @pyqtSlot()
    def __installPackages(self):
        """
        Private slot to install packages to be given by the user.
        """
        venvName = self.environmentsComboBox.currentText()
        if venvName:
            from .PipPackagesInputDialog import PipPackagesInputDialog
            dlg = PipPackagesInputDialog(self, self.tr("Install Packages"))
            if dlg.exec_() == QDialog.Accepted:
                packages, user = dlg.getData()
                if packages:
                    self.__pip.installPackages(packages, venvName=venvName,
                                               userSite=user)
    
    @pyqtSlot()
    def __installLocalPackage(self):
        """
        Private slot to install a package available on local storage.
        """
        venvName = self.environmentsComboBox.currentText()
        if venvName:
            from .PipFileSelectionDialog import PipFileSelectionDialog
            dlg = PipFileSelectionDialog(self, "package")
            if dlg.exec_() == QDialog.Accepted:
                package, user = dlg.getData()
                if package and os.path.exists(package):
                    self.__pip.installPackages([package], venvName=venvName,
                                               userSite=user)
    
    @pyqtSlot()
    def __installRequirements(self):
        """
        Private slot to install packages as given in a requirements file.
        """
        venvName = self.environmentsComboBox.currentText()
        if venvName:
            self.__pip.installRequirements(venvName)
    
    @pyqtSlot()
    def __uninstallRequirements(self):
        """
        Private slot to uninstall packages as given in a requirements file.
        """
        venvName = self.environmentsComboBox.currentText()
        if venvName:
            self.__pip.uninstallRequirements(venvName)
    
    @pyqtSlot()
    def __generateRequirements(self):
        """
        Private slot to generate the contents for a requirements file.
        """
        venvName = self.environmentsComboBox.currentText()
        if venvName:
            from .PipFreezeDialog import PipFreezeDialog
            self.__freezeDialog = PipFreezeDialog(self.__pip, self)
            self.__freezeDialog.show()
            self.__freezeDialog.start(venvName)
    
    @pyqtSlot()
    def __editUserConfiguration(self):
        """
        Private slot to edit the user configuration.
        """
        self.__editConfiguration()
    
    @pyqtSlot()
    def __editVirtualenvConfiguration(self):
        """
        Private slot to edit the configuration of the selected environment.
        """
        venvName = self.environmentsComboBox.currentText()
        if venvName:
            self.__editConfiguration(venvName=venvName)
    
    def __editConfiguration(self, venvName=""):
        """
        Private method to edit a configuration.
        
        @param venvName name of the environment to act upon
        @type str
        """
        from QScintilla.MiniEditor import MiniEditor
        if venvName:
            cfgFile = self.__pip.getVirtualenvConfig(venvName)
            if not cfgFile:
                return
        else:
            cfgFile = self.__pip.getUserConfig()
        cfgDir = os.path.dirname(cfgFile)
        if not cfgDir:
            E5MessageBox.critical(
                None,
                self.tr("Edit Configuration"),
                self.tr("""No valid configuration path determined."""
                        """ Aborting"""))
            return
        
        try:
            if not os.path.isdir(cfgDir):
                os.makedirs(cfgDir)
        except OSError:
            E5MessageBox.critical(
                None,
                self.tr("Edit Configuration"),
                self.tr("""No valid configuration path determined."""
                        """ Aborting"""))
            return
        
        if not os.path.exists(cfgFile):
            try:
                f = open(cfgFile, "w")
                f.write("[global]\n")
                f.close()
            except (IOError, OSError):
                # ignore these
                pass
        
        # check, if the destination is writeable
        if not os.access(cfgFile, os.W_OK):
            E5MessageBox.critical(
                None,
                self.tr("Edit Configuration"),
                self.tr("""No valid configuration path determined."""
                        """ Aborting"""))
            return
        
        self.__editor = MiniEditor(cfgFile, "Properties")
        self.__editor.show()
 
    def __pipConfigure(self):
        """
        Private slot to open the configuration page.
        """
        e5App().getObject("UserInterface").showPreferences("pipPage")
