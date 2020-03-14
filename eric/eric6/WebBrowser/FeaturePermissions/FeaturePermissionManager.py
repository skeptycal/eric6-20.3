# -*- coding: utf-8 -*-

# Copyright (c) 2015 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the feature permission manager object.
"""


from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWebEngineWidgets import QWebEnginePage

import Globals
import Preferences


class FeaturePermissionManager(QObject):
    """
    Class implementing the feature permission manager object.
    """
    SettingsKeyFormat = "WebBrowser/FeaturePermissions/{0}"
    
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent object
        @type QObject
        """
        super(FeaturePermissionManager, self).__init__(parent)
        
        self.__featurePermissions = {
            QWebEnginePage.Geolocation: {
                QWebEnginePage.PermissionGrantedByUser: [],
                QWebEnginePage.PermissionDeniedByUser: [],
            },
            QWebEnginePage.MediaAudioCapture: {
                QWebEnginePage.PermissionGrantedByUser: [],
                QWebEnginePage.PermissionDeniedByUser: [],
            },
            QWebEnginePage.MediaVideoCapture: {
                QWebEnginePage.PermissionGrantedByUser: [],
                QWebEnginePage.PermissionDeniedByUser: [],
            },
            QWebEnginePage.MediaAudioVideoCapture: {
                QWebEnginePage.PermissionGrantedByUser: [],
                QWebEnginePage.PermissionDeniedByUser: [],
            },
            QWebEnginePage.MouseLock: {
                QWebEnginePage.PermissionGrantedByUser: [],
                QWebEnginePage.PermissionDeniedByUser: [],
            },
        }
        try:
            # these are defined as of Qt 5.10.0/PyQt 5.10.0
            self.__featurePermissions.update({
                QWebEnginePage.DesktopVideoCapture: {
                    QWebEnginePage.PermissionGrantedByUser: [],
                    QWebEnginePage.PermissionDeniedByUser: [],
                },
                QWebEnginePage.DesktopAudioVideoCapture: {
                    QWebEnginePage.PermissionGrantedByUser: [],
                    QWebEnginePage.PermissionDeniedByUser: [],
                },
            })
        except AttributeError:
            pass
        try:
            # this was re-added in Qt 5.13.0
            self.__featurePermissions[QWebEnginePage.Notifications] = {
                QWebEnginePage.PermissionGrantedByUser: [],
                QWebEnginePage.PermissionDeniedByUser: [],
            }
        except AttributeError:
            pass
        
        self.__featurePermissionsKeys = {
            (QWebEnginePage.Geolocation,
             QWebEnginePage.PermissionGrantedByUser):
            "GeolocationGranted",
            (QWebEnginePage.Geolocation,
             QWebEnginePage.PermissionDeniedByUser):
            "GeolocationDenied",
            (QWebEnginePage.MediaAudioCapture,
             QWebEnginePage.PermissionGrantedByUser):
            "MediaAudioCaptureGranted",
            (QWebEnginePage.MediaAudioCapture,
             QWebEnginePage.PermissionDeniedByUser):
            "MediaAudioCaptureDenied",
            (QWebEnginePage.MediaVideoCapture,
             QWebEnginePage.PermissionGrantedByUser):
            "MediaVideoCaptureGranted",
            (QWebEnginePage.MediaVideoCapture,
             QWebEnginePage.PermissionDeniedByUser):
            "MediaVideoCaptureDenied",
            (QWebEnginePage.MediaAudioVideoCapture,
             QWebEnginePage.PermissionGrantedByUser):
            "MediaAudioVideoCaptureGranted",
            (QWebEnginePage.MediaAudioVideoCapture,
             QWebEnginePage.PermissionDeniedByUser):
            "MediaAudioVideoCaptureDenied",
            (QWebEnginePage.MouseLock,
             QWebEnginePage.PermissionGrantedByUser):
            "MouseLockGranted",
            (QWebEnginePage.MouseLock,
             QWebEnginePage.PermissionDeniedByUser):
            "MouseLockDenied",
        }
        try:
            # these are defined as of Qt 5.10.0/PyQt 5.10.0
            self.__featurePermissionsKeys.update({
                (QWebEnginePage.DesktopVideoCapture,
                 QWebEnginePage.PermissionGrantedByUser):
                "DesktopVideoCaptureGranted",
                (QWebEnginePage.DesktopVideoCapture,
                 QWebEnginePage.PermissionDeniedByUser):
                "DesktopVideoCaptureDenied",
                (QWebEnginePage.DesktopAudioVideoCapture,
                 QWebEnginePage.PermissionGrantedByUser):
                "DesktopAudioVideoCaptureGranted",
                (QWebEnginePage.DesktopAudioVideoCapture,
                 QWebEnginePage.PermissionDeniedByUser):
                "DesktopAudioVideoCaptureDenied",
            })
        except AttributeError:
            pass
        try:
            # this was re-added in Qt 5.13.0
            self.__featurePermissionsKeys.update({
                (QWebEnginePage.Notifications,
                 QWebEnginePage.PermissionGrantedByUser):
                "NotificationsGranted",
                (QWebEnginePage.Notifications,
                 QWebEnginePage.PermissionDeniedByUser):
                "NotificationsDenied",
            })
        except AttributeError:
            pass
        
        self.__loaded = False

    def requestFeaturePermission(self, page, origin, feature):
        """
        Public method to request a feature permission.
        
        @param page reference to the requesting web page
        @type QWebEnginePage
        @param origin security origin requesting the feature
        @type QUrl
        @param feature requested feature
        @type QWebEnginePage.Feature
        """
        if origin is None or origin.isEmpty():
            return
        
        if not self.__loaded:
            self.__loadSettings()
        
        host = origin.host()
        
        if feature in self.__featurePermissions:
            for permission in self.__featurePermissions[feature]:
                if host in self.__featurePermissions[feature][permission]:
                    page.setFeaturePermission(origin, feature, permission)
                    return
        
        from .FeaturePermissionBar import FeaturePermissionBar
        bar = FeaturePermissionBar(page, origin, feature, self)
        bar.show()
    
    def rememberFeaturePermission(self, host, feature, permission):
        """
        Public method to remember a user decision for a feature permission.
        
        @param host host name to remember the decision for
        @type str
        @param feature feature to be remembered
        @type QWebEnginePage.Feature
        @param permission feature permission to be remembered
        @type QWebEnginePage.PermissionPolicy
        """
        if feature in self.__featurePermissions:
            if host not in self.__featurePermissions[feature][permission]:
                self.__featurePermissions[feature][permission].append(host)
                self.__saveSettings()
    
    def __loadSettings(self):
        """
        Private method to load the remembered feature permissions.
        """
        if self.__loaded:
            # no reloading allowed
            return
        
        for (feature, permission), key in (
            self.__featurePermissionsKeys.items()
        ):
            self.__featurePermissions[feature][permission] = (
                Globals.toList(Preferences.Prefs.settings.value(
                    FeaturePermissionManager.SettingsKeyFormat.format(key),
                    []
                ))
            )
        
        self.__loaded = True
    
    def __saveSettings(self):
        """
        Private method to save the remembered feature permissions.
        """
        if not self.__loaded:
            return
        
        import WebBrowser.WebBrowserWindow
        if WebBrowser.WebBrowserWindow.WebBrowserWindow.isPrivate():
            return
        
        for (feature, permission), key in (
                self.__featurePermissionsKeys.items()
        ):
            Preferences.Prefs.settings.setValue(
                FeaturePermissionManager.SettingsKeyFormat.format(key),
                self.__featurePermissions[feature][permission])
    
    def showFeaturePermissionsDialog(self):
        """
        Public method to show a dialog to manage the remembered feature
        permissions.
        """
        if not self.__loaded:
            self.__loadSettings()
        
        from .FeaturePermissionsDialog import FeaturePermissionsDialog
        dlg = FeaturePermissionsDialog(self.__featurePermissions)
        if dlg.exec_() == QDialog.Accepted:
            newFeaturePermissions = dlg.getData()
            self.__featurePermissions = newFeaturePermissions
            self.__saveSettings()
