# -*- coding: utf-8 -*-

# Copyright (c) 2019 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing some file system commands for MicroPython.
"""


import ast
import time
import os

from PyQt5.QtCore import (
    pyqtSlot, pyqtSignal, QObject, QThread, QTimer, QCoreApplication,
    QEventLoop
)

from .MicroPythonSerialPort import MicroPythonSerialPort

import Preferences


class MicroPythonCommandsInterface(QObject):
    """
    Class implementing some file system commands for MicroPython.
    
    Commands are provided to perform operations on the file system of a
    connected MicroPython device. Supported commands are:
    <ul>
    <li>ls: directory listing</li>
    <li>lls: directory listing with meta data</li>
    <li>cd: change directory</li>
    <li>pwd: get the current directory</li>
    <li>put: copy a file to the connected device</li>
    <li>get: get a file from the connected device</li>
    <li>rm: remove a file from the connected device</li>
    <li>rmrf: remove a file/directory recursively (like 'rm -rf' in bash)
    <li>mkdir: create a new directory</li>
    <li>rmdir: remove an empty directory</li>
    </ul>
    
    There are additional commands related to time and version.
    <ul>
    <li>version: get version info about MicroPython</li>
    <li>getImplementation: get some implementation information</li>
    <li>syncTime: synchronize the time of the connected device</li>
    <li>showTime: show the current time of the connected device</li>
    </ul>
    
    @signal executeAsyncFinished() emitted to indicate the end of an
        asynchronously executed list of commands (e.g. a script)
    @signal dataReceived(data) emitted to send data received via the serial
        connection for further processing
    """
    executeAsyncFinished = pyqtSignal()
    dataReceived = pyqtSignal(bytes)
    
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent object
        @type QObject
        """
        super(MicroPythonCommandsInterface, self).__init__(parent)
        
        self.__repl = parent
        
        self.__blockReadyRead = False
        
        self.__serial = MicroPythonSerialPort(
            timeout=Preferences.getMicroPython("SerialTimeout"),
            parent=self)
        self.__serial.readyRead.connect(self.__readSerial)
    
    @pyqtSlot()
    def __readSerial(self):
        """
        Private slot to read all available serial data and emit it with the
        "dataReceived" signal for further processing.
        """
        if not self.__blockReadyRead:
            data = bytes(self.__serial.readAll())
            self.dataReceived.emit(data)
    
    @pyqtSlot()
    def connectToDevice(self, port):
        """
        Public slot to start the manager.
        
        @param port name of the port to be used
        @type str
        @return flag indicating success
        @rtype bool
        """
        return self.__serial.openSerialLink(port)
    
    @pyqtSlot()
    def disconnectFromDevice(self):
        """
        Public slot to stop the thread.
        """
        self.__serial.closeSerialLink()
    
    def isConnected(self):
        """
        Public method to get the connection status.
        
        @return flag indicating the connection status
        @rtype bool
        """
        return self.__serial.isConnected()
    
    @pyqtSlot()
    def handlePreferencesChanged(self):
        """
        Public slot to handle a change of the preferences.
        """
        self.__serial.setTimeout(Preferences.getMicroPython("SerialTimeout"))
    
    def write(self, data):
        """
        Public method to write data to the connected device.
        
        @param data data to be written
        @type bytes or bytearray
        """
        self.__serial.isConnected() and self.__serial.write(data)
    
    def __rawOn(self):
        """
        Private method to switch the connected device to 'raw' mode.
        
        Note: switching to raw mode is done with synchronous writes.
        
        @return flag indicating success
        @@rtype bool
        """
        if not self.__serial:
            return False
        
        rawReplMessage = b"raw REPL; CTRL-B to exit\r\n>"
        
        self.__serial.write(b"\x02")        # end raw mode if required
        self.__serial.waitForBytesWritten()
        for _i in range(3):
            # CTRL-C three times to break out of loops
            self.__serial.write(b"\r\x03")
            self.__serial.waitForBytesWritten()
            QThread.msleep(10)
        self.__serial.readAll()             # read all data and discard it
        self.__serial.write(b"\r\x01")      # send CTRL-A to enter raw mode
        self.__serial.readUntil(rawReplMessage)
        if self.__serial.hasTimedOut():
            # it timed out; try it again and than fail
            self.__serial.write(b"\r\x01")  # send CTRL-A again
            self.__serial.readUntil(rawReplMessage)
            if self.__serial.hasTimedOut():
                return False
        
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
        self.__serial.readAll()             # read all data and discard it
        return True
    
    def __rawOff(self):
        """
        Private method to switch 'raw' mode off.
        """
        if self.__serial:
            self.__serial.write(b"\x02")      # send CTRL-B to cancel raw mode
            self.__serial.readUntil(b">>> ")  # read until Python prompt
            self.__serial.readAll()           # read all data and discard it
    
    def execute(self, commands):
        """
        Public method to send commands to the connected device and return the
        result.
        
        If no serial connection is available, empty results will be returned.
        
        @param commands list of commands to be executed
        @type str
        @return tuple containing stdout and stderr output of the device
        @rtype tuple of (bytes, bytes)
        """
        if not self.__serial:
            return b"", b""
        
        if not self.__serial.isConnected():
            return b"", b"Device not connected or not switched on."
        
        result = bytearray()
        err = b""
        
        # switch on raw mode
        self.__blockReadyRead = True
        ok = self.__rawOn()
        if not ok:
            self.__blockReadyRead = False
            return (
                b"",
                b"Could not switch to raw mode. Is the device switched on?"
            )
        
        # send commands
        QThread.msleep(10)
        for command in commands:
            if command:
                commandBytes = command.encode("utf-8")
                self.__serial.write(commandBytes + b"\x04")
                QCoreApplication.processEvents(
                    QEventLoop.ExcludeUserInputEvents)
                ok = self.__serial.readUntil(b"OK")
                if ok != b"OK":
                    return (
                        b"",
                        "Expected 'OK', got '{0}', followed by '{1}'".format(
                            ok, self.__serial.readAll()).encode("utf-8")
                    )
                
                # read until prompt
                response = self.__serial.readUntil(b"\x04>")
                if self.__serial.hasTimedOut():
                    self.__blockReadyRead = False
                    return b"", b"Timeout while processing commands."
                if b"\x04" in response[:-2]:
                    # split stdout, stderr
                    out, err = response[:-2].split(b"\x04")
                    result += out
                else:
                    err = b"invalid response received: " + response
                if err:
                    self.__blockReadyRead = False
                    return b"", err
        
        # switch off raw mode
        QThread.msleep(10)
        self.__rawOff()
        self.__blockReadyRead = False
        
        return bytes(result), err
    
    def executeAsync(self, commandsList):
        """
        Public method to execute a series of commands over a period of time
        without returning any result (asynchronous execution).
        
        @param commandsList list of commands to be execute on the device
        @type list of bytes
        """
        def remainingTask(commands):
            self.executeAsync(commands)
        
        if commandsList:
            command = commandsList[0]
            self.__serial.write(command)
            remainder = commandsList[1:]
            QTimer.singleShot(2, lambda: remainingTask(remainder))
        else:
            self.executeAsyncFinished.emit()
    
    def __shortError(self, error):
        """
        Private method to create a shortened error message.
        
        @param error verbose error message
        @type bytes
        @return shortened error message
        @rtype str
        """
        if error:
            decodedError = error.decode("utf-8")
            try:
                return decodedError.split["\r\n"][-2]
            except Exception:
                return decodedError
        return self.tr("Detected an error without indications.")
    
    ##################################################################
    ## Methods below implement the file system commands
    ##################################################################
    
    def ls(self, dirname=""):
        """
        Public method to get a directory listing of the connected device.
        
        @param dirname name of the directory to be listed
        @type str
        @return tuple containg the directory listing
        @rtype tuple of str
        @exception IOError raised to indicate an issue with the device
        """
        if self.__repl.isMicrobit():
            # BBC micro:bit does not support directories
            commands = [
                "import os as __os_",
                "print(__os_.listdir())",
                "del __os_",
            ]
        else:
            commands = [
                "import os as __os_",
                "print(__os_.listdir('{0}'))".format(dirname),
                "del __os_",
            ]
        out, err = self.execute(commands)
        if err:
            raise IOError(self.__shortError(err))
        return ast.literal_eval(out.decode("utf-8"))
    
    def lls(self, dirname="", fullstat=False, showHidden=False):
        """
        Public method to get a long directory listing of the connected device
        including meta data.
        
        @param dirname name of the directory to be listed
        @type str
        @param fullstat flag indicating to return the full stat() tuple
        @type bool
        @param showHidden flag indicating to show hidden files as well
        @type bool
        @return list containing the directory listing with tuple entries of
            the name and and a tuple of mode, size and time (if fullstat is
            false) or the complete stat() tuple. 'None' is returned in case the
            directory doesn't exist.
        @rtype tuple of (str, tuple)
        @exception IOError raised to indicate an issue with the device
        """
        if self.__repl.isMicrobit():
            # BBC micro:bit does not support directories
            commands = [
                "import os as __os_",
                "\n".join([
                    "def is_visible(filename, showHidden):",
                    "    return showHidden or "
                    "(filename[0] != '.' and filename[-1] != '~')",
                ]),
                "\n".join([
                    "def stat(filename):",
                    "    size = __os_.size(filename)",
                    "    return (0, 0, 0, 0, 0, 0, size, 0, 0, 0)"
                ]),
                "\n".join([
                    "def listdir_stat(showHidden):",
                    "    files = __os_.listdir()",
                    "    return list((f, stat(f)) for f in files if"
                    " is_visible(f,showHidden))",
                ]),
                "print(listdir_stat({0}))".format(showHidden),
                "del __os_, stat, listdir_stat, is_visible",
            ]
        else:
            commands = [
                "import os as __os_",
                "\n".join([
                    "def is_visible(filename, showHidden):",
                    "    return showHidden or "
                    "(filename[0] != '.' and filename[-1] != '~')",
                ]),
                "\n".join([
                    "def stat(filename):",
                    "    try:",
                    "        rstat = __os_.lstat(filename)",
                    "    except:",
                    "        rstat = __os_.stat(filename)",
                    "    return tuple(rstat)",
                ]),
                "\n".join([
                    "def listdir_stat(dirname, showHidden):",
                    "    try:",
                    "        files = __os_.listdir(dirname)",
                    "    except OSError:",
                    "        return None",
                    "    if dirname in ('', '/'):",
                    "        return list((f, stat(f)) for f in files if"
                    " is_visible(f, showHidden))",
                    "    return list((f, stat(dirname + '/' + f))"
                    " for f in files if is_visible(f, showHidden))",
                ]),
                "print(listdir_stat('{0}', {1}))".format(dirname, showHidden),
                "del __os_, stat, listdir_stat, is_visible",
            ]
        out, err = self.execute(commands)
        if err:
            raise IOError(self.__shortError(err))
        fileslist = ast.literal_eval(out.decode("utf-8"))
        if fileslist is None:
            return None
        else:
            if fullstat:
                return fileslist
            else:
                return [(f, (s[0], s[6], s[8])) for f, s in fileslist]
    
    def cd(self, dirname):
        """
        Public method to change the current directory on the connected device.
        
        @param dirname directory to change to
        @type str
        @exception IOError raised to indicate an issue with the device
        """
        assert dirname
        
        commands = [
            "import os as __os_",
            "__os_.chdir('{0}')".format(dirname),
            "del __os_",
        ]
        out, err = self.execute(commands)
        if err:
            raise IOError(self.__shortError(err))
    
    def pwd(self):
        """
        Public method to get the current directory of the connected device.
        
        @return current directory
        @rtype str
        @exception IOError raised to indicate an issue with the device
        """
        if self.__repl.isMicrobit():
            # BBC micro:bit does not support directories
            return ""
        
        commands = [
            "import os as __os_",
            "print(__os_.getcwd())",
            "del __os_",
        ]
        out, err = self.execute(commands)
        if err:
            raise IOError(self.__shortError(err))
        return out.decode("utf-8").strip()
    
    def rm(self, filename):
        """
        Public method to remove a file from the connected device.
        
        @param filename name of the file to be removed
        @type str
        @exception IOError raised to indicate an issue with the device
        """
        assert filename
        
        commands = [
            "import os as __os_",
            "__os_.remove('{0}')".format(filename),
            "del __os_",
        ]
        out, err = self.execute(commands)
        if err:
            raise IOError(self.__shortError(err))
    
    def rmrf(self, name, recursive=False, force=False):
        """
        Public method to remove a file or directory recursively.
        
        @param name of the file or directory to remove
        @type str
        @param recursive flag indicating a recursive deletion
        @type bool
        @param force flag indicating to ignore errors
        @type bool
        @return flag indicating success
        @rtype bool
        @exception IOError raised to indicate an issue with the device
        """
        assert name
        
        commands = [
            "import os as __os_",
            "\n".join([
                "def remove_file(name, recursive=False, force=False):",
                "    try:",
                "        mode = __os_.stat(name)[0]",
                "        if mode & 0x4000 != 0:",
                "            if recursive:",
                "                for file in __os_.listdir(name):",
                "                    success = remove_file(name + '/' + file,"
                " recursive, force)",
                "                    if not success and not force:",
                "                        return False",
                "                __os_.rmdir(name)",
                "            else:",
                "                if not force:",
                "                    return False",
                "        else:",
                "            __os_.remove(name)",
                "    except:",
                "        if not force:",
                "            return False",
                "    return True",
            ]),
            "print(remove_file('{0}', {1}, {2}))".format(name, recursive,
                                                         force),
            "del __os_, remove_file",
        ]
        out, err = self.execute(commands)
        if err:
            raise IOError(self.__shortError(err))
        return ast.literal_eval(out.decode("utf-8"))
    
    def mkdir(self, dirname):
        """
        Public method to create a new directory.
        
        @param dirname name of the directory to create
        @type str
        @exception IOError raised to indicate an issue with the device
        """
        assert dirname
   
        commands = [
            "import os as __os_",
            "__os_.mkdir('{0}')".format(dirname),
            "del __os_",
        ]
        out, err = self.execute(commands)
        if err:
            raise IOError(self.__shortError(err))
    
    def rmdir(self, dirname):
        """
        Public method to remove a directory.
        
        @param dirname name of the directory to be removed
        @type str
        @exception IOError raised to indicate an issue with the device
        """
        assert dirname
   
        commands = [
            "import os as __os_",
            "__os_.rmdir('{0}')".format(dirname),
            "del __os_",
        ]
        out, err = self.execute(commands)
        if err:
            raise IOError(self.__shortError(err))
    
    def put(self, hostFileName, deviceFileName=None):
        """
        Public method to copy a local file to the connected device.
        
        @param hostFileName name of the file to be copied
        @type str
        @param deviceFileName name of the file to copy to
        @type str
        @return flag indicating success
        @rtype bool
        @exception IOError raised to indicate an issue with the device
        """
        if not os.path.isfile(hostFileName):
            raise IOError("No such file: {0}".format(hostFileName))
        
        with open(hostFileName, "rb") as hostFile:
            content = hostFile.read()
            # convert eol '\r'
            content = content.replace(b"\r\n", b"\r")
            content = content.replace(b"\n", b"\r")
        
        if not deviceFileName:
            deviceFileName = os.path.basename(hostFileName)
        
        commands = [
            "fd = open('{0}', 'wb')".format(deviceFileName),
            "f = fd.write",
        ]
        while content:
            chunk = content[:64]
            commands.append("f(" + repr(chunk) + ")")
            content = content[64:]
        commands.extend([
            "fd.close()",
            "del f, fd",
        ])
        
        out, err = self.execute(commands)
        if err:
            raise IOError(self.__shortError(err))
        return True
    
    def get(self, deviceFileName, hostFileName=None):
        """
        Public method to copy a file from the connected device.
        
        @param deviceFileName name of the file to copy
        @type str
        @param hostFileName name of the file to copy to
        @type str
        @return flag indicating success
        @rtype bool
        @exception IOError raised to indicate an issue with the device
        """
        if not hostFileName:
            hostFileName = deviceFileName
        
        commands = [
            "\n".join([
                "def send_data():",
                "    try:",
                "        from microbit import uart as u",
                "    except ImportError:",
                "        try:",
                "            from machine import UART",
                "            u = UART(0, {0})".format(115200),
                "        except Exception:",
                "            try:",
                "                from sys import stdout as u",
                "            except Exception:",
                "                raise Exception('Could not find UART module"
                " in device.')",
                "    f = open('{0}', 'rb')".format(deviceFileName),
                "    r = f.read",
                "    result = True",
                "    while result:",
                "        result = r(32)",
                "        if result:",
                "            u.write(result)",
                "    f.close()",
            ]),
            "send_data()",
        ]
        out, err = self.execute(commands)
        if err:
            raise IOError(self.__shortError(err))
        
        # write the received bytes to the local file
        # convert eol to "\n"
        out = out.replace(b"\r\n", b"\n")
        out = out.replace(b"\r", b"\n")
        with open(hostFileName, "wb") as hostFile:
            hostFile.write(out)
        return True
    
    def fileSystemInfo(self):
        """
        Public method to obtain information about the currently mounted file
        systems.
        
        @return tuple of tuples containing the file system name, the total
            size, the used size and the free size
        @rtype tuple of tuples of (str, int, int, int)
        @exception IOError raised to indicate an issue with the device
        """
        commands = [
            "import os as __os_",
            "\n".join([
                "def fsinfo():",
                "    infolist = []",
                "    info = __os_.statvfs('/')",
                "    if info[0] == 0:",
                # assume it is just mount points
                "        fsnames = __os_.listdir('/')",
                "        for fs in fsnames:",
                "            fs = '/' + fs",
                "            infolist.append((fs, __os_.statvfs(fs)))",
                "    else:",
                "        infolist.append(('/', info))",
                "    return infolist",
            ]),
            "print(fsinfo())",
            "del __os_, fsinfo",
        ]
        out, err = self.execute(commands)
        if err:
            raise IOError(self.__shortError(err))
        infolist = ast.literal_eval(out.decode("utf-8"))
        if infolist is None:
            return None
        else:
            filesystemInfos = []
            for fs, info in infolist:
                totalSize = info[2] * info[1]
                freeSize = info[4] * info[1]
                usedSize = totalSize - freeSize
                filesystemInfos.append((fs, totalSize, usedSize, freeSize))
        
        return tuple(filesystemInfos)
    
    ##################################################################
    ## non-filesystem related methods below
    ##################################################################
    
    def version(self):
        """
        Public method to get the MicroPython version information of the
        connected device.
        
        @return dictionary containing the version information
        @rtype dict
        @exception IOError raised to indicate an issue with the device
        """
        commands = [
            "import os as __os_",
            "print(__os_.uname())",
            "del __os_",
        ]
        out, err = self.execute(commands)
        if err:
            raise IOError(self.__shortError(err))
        
        rawOutput = out.decode("utf-8").strip()
        rawOutput = rawOutput[1:-1]
        items = rawOutput.split(",")
        result = {}
        for item in items:
            key, value = item.strip().split("=")
            result[key.strip()] = value.strip()[1:-1]
        return result
    
    def getImplementation(self):
        """
        Public method to get some implementation information of the connected
        device.
        
        @return dictionary containing the implementation information
        @rtype dict
        @exception IOError raised to indicate an issue with the device
        """
        commands = [
            "import sys as __sys_",
            "res = {}",                             # __IGNORE_WARNING_M613__
            "\n".join([
                "try:",
                "    res['name'] = __sys_.implementation.name",
                "except AttributeError:",
                "    res['name'] = 'unknown'",
            ]),
            "\n".join([
                "try:",
                "    res['version'] = '.'.join((str(i) for i in"
                " __sys_.implementation.version))",
                "except AttributeError:",
                "    res['version'] = 'unknown'",
            ]),
            "print(res)",
            "del res, __sys_",
        ]
        out, err = self.execute(commands)
        if err:
            raise IOError(self.__shortError(err))
        return ast.literal_eval(out.decode("utf-8"))
    
    def syncTime(self):
        """
        Public method to set the time of the connected device to the local
        computer's time.
        
        @exception IOError raised to indicate an issue with the device
        """
        now = time.localtime(time.time())
        commands = [
            "\n".join([
                "def set_time(rtc_time):",
                "    rtc = None",
                "    try:",           # Pyboard (it doesn't have machine.RTC())
                "        import pyb as __pyb_",
                "        rtc = __pyb_.RTC()",
                "        clock_time = rtc_time[:3] +"
                " (rtc_time[6] + 1,) + rtc_time[3:6] + (0,)",
                "        rtc.datetime(clock_time)",
                "        del __pyb_",
                "    except Exception:",
                "        try:",
                "            import machine as __machine_",
                "            rtc = __machine_.RTC()",
                "            try:",     # ESP8266 may use rtc.datetime()
                "                clock_time = rtc_time[:3] +"
                " (rtc_time[6],) + rtc_time[3:6] + (0,)",
                "                rtc.datetime(clock_time)",
                "            except Exception:",  # ESP32 uses rtc.init()
                "                import os",
                "                if 'LoBo' in os.uname()[0]:",  # LoBo MPy
                "                    clock_time = rtc_time + (0,)",
                "                else:",
                "                    clock_time = rtc_time[:3] +"
                " (rtc_time[6],) + rtc_time[3:6] + (0,)",
                "                rtc.init(clock_time)",
                "            del __machine_",
                "        except:",
                "            try:",
                "                import rtc as __rtc_",
                "                import time as __time_",
                "                clock=__rtc_.RTC()",
                "                clock.datetime = __time_.struct_time("
                "rtc_time + (-1, -1))",
                "                del __rtc_, __time_",
                "            except:",
                "                pass",
            ]),
            "set_time({0})".format((now.tm_year, now.tm_mon, now.tm_mday,
                                    now.tm_hour, now.tm_min, now.tm_sec,
                                    now.tm_wday)),
            "del set_time",
        ]
        out, err = self.execute(commands)
        if err:
            raise IOError(self.__shortError(err))
    
    def getTime(self):
        """
        Public method to get the current time of the device.
        
        @return time of the device
        @rtype str
        @exception IOError raised to indicate an issue with the device
        """
        commands = [
            "import time as __time_",
            "\n".join([
                "try:",
                "    print(__time_.strftime('%Y-%m-%d %H:%M:%S',"
                # __IGNORE_WARNING_M601__
                " __time_.localtime()))",
                "except AttributeError:",
                "    tm = __time_.localtime()",
                "    print('{0:04d}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}'"
                ".format(tm[0], tm[1], tm[2], tm[3], tm[4], tm[5]))",
                "    del tm",
            ]),
            "del __time_"
        ]
        out, err = self.execute(commands)
        if err:
            raise IOError(self.__shortError(err))
        return out.decode("utf-8").strip()
