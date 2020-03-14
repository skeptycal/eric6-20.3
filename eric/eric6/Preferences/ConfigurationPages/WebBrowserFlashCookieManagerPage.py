# -*- coding: utf-8 -*-

# Copyright (c) 2015 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Flash Cookies Manager configuration page.
"""


from E5Gui.E5PathPicker import E5PathPickerModes

from .ConfigurationPageBase import ConfigurationPageBase
from .Ui_WebBrowserFlashCookieManagerPage import (
    Ui_WebBrowserFlashCookieManagerPage
)

import Preferences


class WebBrowserFlashCookieManagerPage(ConfigurationPageBase,
                                       Ui_WebBrowserFlashCookieManagerPage):
    """
    Class implementing the Flash Cookies Manager configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        super(WebBrowserFlashCookieManagerPage, self).__init__()
        self.setupUi(self)
        self.setObjectName("WebBrowserFlashCookieManagerPage")
        
        self.flashDataPathPicker.setMode(E5PathPickerModes.DirectoryMode)
        
        # set initial values
        self.flashDataPathPicker.setText(
            Preferences.getWebBrowser("FlashCookiesDataPath"))
        self.autoModeGroup.setChecked(
            Preferences.getWebBrowser("FlashCookieAutoRefresh"))
        self.notificationGroup.setChecked(
            Preferences.getWebBrowser("FlashCookieNotify"))
        self.deleteGroup.setChecked(
            Preferences.getWebBrowser("FlashCookiesDeleteOnStartExit"))
    
    def save(self):
        """
        Public slot to save the Flash Cookies Manager configuration.
        """
        Preferences.setWebBrowser(
            "FlashCookiesDataPath", self.flashDataPathPicker.text())
        Preferences.setWebBrowser(
            "FlashCookieAutoRefresh", self.autoModeGroup.isChecked())
        Preferences.setWebBrowser(
            "FlashCookieNotify", self.notificationGroup.isChecked())
        Preferences.setWebBrowser(
            "FlashCookiesDeleteOnStartExit", self.deleteGroup.isChecked())
    

def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    @return reference to the instantiated page (ConfigurationPageBase)
    """
    page = WebBrowserFlashCookieManagerPage()
    return page
