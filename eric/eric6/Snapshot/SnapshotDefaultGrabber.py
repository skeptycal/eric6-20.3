# -*- coding: utf-8 -*-

# Copyright (c) 2019 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a grabber object for non-Wayland desktops.
"""


from PyQt5.QtCore import pyqtSignal, Qt, QObject, QTimer, QEvent
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtWidgets import QWidget, QApplication

from .SnapshotModes import SnapshotModes

import Globals


class SnapshotDefaultGrabber(QObject):
    """
    Class implementing a grabber object for non-Wayland desktops.
    
    @signal grabbed(QPixmap) emitted after the grab operation is finished
    """
    grabbed = pyqtSignal(QPixmap)
    
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent object
        @type QObject
        """
        super(SnapshotDefaultGrabber, self).__init__(parent)
        
        self.__grabber = None
        self.__grabberWidget = QWidget(None, Qt.X11BypassWindowManagerHint)
        self.__grabberWidget.move(-10000, -10000)
        self.__grabberWidget.installEventFilter(self)
        
        from .SnapshotTimer import SnapshotTimer
        self.__grabTimer = SnapshotTimer()
        self.__grabTimer.timeout.connect(self.__grabTimerTimeout)
    
    def supportedModes(self):
        """
        Public method to get the supported screenshot modes.
        
        @return tuple of supported screenshot modes
        @rtype tuple of SnapshotModes
        """
        return (
            SnapshotModes.Fullscreen,
            SnapshotModes.SelectedScreen,
            SnapshotModes.Rectangle,
            SnapshotModes.Freehand,
            SnapshotModes.Ellipse,
        )
    
    def grab(self, mode, delay=0, captureCursor=False,
             captureDecorations=False):
        """
        Public method to perform a grab operation potentially after a delay.
        
        @param mode screenshot mode
        @type ScreenshotModes
        @param delay delay in seconds
        @type int
        @param captureCursor flag indicating to include the mouse cursor
            (not used)
        @type bool
        @param captureDecorations flag indicating to include the window
            decorations (not used)
        @type bool
        """
        self.__mode = mode
        if delay:
            self.__grabTimer.start(delay)
        else:
            QTimer.singleShot(200, self.__startUndelayedGrab)
    
    def __grabTimerTimeout(self):
        """
        Private slot to perform a delayed grab operation.
        """
        if self.__mode == SnapshotModes.Rectangle:
            self.__grabRectangle()
        elif self.__mode == SnapshotModes.Ellipse:
            self.__grabEllipse()
        elif self.__mode == SnapshotModes.Freehand:
            self.__grabFreehand()
        else:
            self.__performGrab(self.__mode)
    
    def __startUndelayedGrab(self):
        """
        Private slot to perform an undelayed grab operation.
        """
        if self.__mode == SnapshotModes.Rectangle:
            self.__grabRectangle()
        elif self.__mode == SnapshotModes.Ellipse:
            self.__grabEllipse()
        elif self.__mode == SnapshotModes.Freehand:
            self.__grabFreehand()
        else:
            if Globals.isMacPlatform():
                self.__performGrab(self.__mode)
            else:
                self.__grabberWidget.show()
                self.__grabberWidget.grabMouse(Qt.CrossCursor)
    
    def __grabRectangle(self):
        """
        Private method to grab a rectangular screen region.
        """
        from .SnapshotRegionGrabber import SnapshotRegionGrabber
        self.__grabber = SnapshotRegionGrabber(
            mode=SnapshotRegionGrabber.Rectangle)
        self.__grabber.grabbed.connect(self.__captured)
    
    def __grabEllipse(self):
        """
        Private method to grab an elliptical screen region.
        """
        from .SnapshotRegionGrabber import SnapshotRegionGrabber
        self.__grabber = SnapshotRegionGrabber(
            mode=SnapshotRegionGrabber.Ellipse)
        self.__grabber.grabbed.connect(self.__captured)
    
    def __grabFreehand(self):
        """
        Private method to grab a non-rectangular screen region.
        """
        from .SnapshotFreehandGrabber import SnapshotFreehandGrabber
        self.__grabber = SnapshotFreehandGrabber()
        self.__grabber.grabbed.connect(self.__captured)
    
    def __performGrab(self, mode):
        """
        Private method to perform a screen grab other than a selected region.
        
        @param mode screenshot mode
        @type SnapshotModes
        """
        self.__grabberWidget.releaseMouse()
        self.__grabberWidget.hide()
        self.__grabTimer.stop()
        
        if mode == SnapshotModes.Fullscreen:
            desktop = QApplication.desktop()
            snapshot = QApplication.screens()[0].grabWindow(
                desktop.winId(), desktop.x(), desktop.y(),
                desktop.width(), desktop.height())
        elif mode == SnapshotModes.SelectedScreen:
            desktop = QApplication.desktop()
            if Globals.qVersionTuple() >= (5, 10, 0):
                screen = QApplication.screenAt(QCursor.pos())
                geom = screen.geometry()
            else:
                screenId = desktop.screenNumber(QCursor.pos())
                geom = desktop.screenGeometry(screenId)
            x = geom.x()
            y = geom.y()
            snapshot = QApplication.screens()[0].grabWindow(
                desktop.winId(), x, y, geom.width(), geom.height())
        else:
            snapshot = QPixmap()
        
        self.grabbed.emit(snapshot)
    
    def __captured(self, pixmap):
        """
        Private slot to show a preview of the snapshot.
        
        @param pixmap pixmap of the snapshot (QPixmap)
        """
        self.__grabber.close()
        snapshot = QPixmap(pixmap)
        
        self.__grabber.grabbed.disconnect(self.__captured)
        self.__grabber = None
        
        self.grabbed.emit(snapshot)
    
    def eventFilter(self, obj, evt):
        """
        Public method to handle event for other objects.
        
        @param obj reference to the object (QObject)
        @param evt reference to the event (QEvent)
        @return flag indicating that the event should be filtered out (boolean)
        """
        if (
            obj == self.__grabberWidget and
            evt.type() == QEvent.MouseButtonPress
        ):
            if QWidget.mouseGrabber() != self.__grabberWidget:
                return False
            if evt.button() == Qt.LeftButton:
                self.__performGrab(self.__mode)
        
        return False
