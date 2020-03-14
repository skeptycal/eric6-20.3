# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the debug server.
"""


import os
import sys

from PyQt5.QtCore import pyqtSignal, QModelIndex
from PyQt5.QtNetwork import (
    QTcpServer, QHostAddress, QHostInfo, QNetworkInterface
)

from E5Gui.E5Application import e5App
from E5Gui import E5MessageBox

from .BreakPointModel import BreakPointModel
from .WatchPointModel import WatchPointModel
from . import DebugClientCapabilities

import Preferences
import Utilities


DebuggerInterfaces = {
    "Python": "DebuggerInterfacePython",
    "None": "DebuggerInterfaceNone",
}


class DebugServer(QTcpServer):
    """
    Class implementing the debug server embedded within the IDE.
    
    @signal clientProcessStdout(str) emitted after the client has sent some
        output via stdout
    @signal clientProcessStderr(str) emitted after the client has sent some
        output via stderr
    @signal clientOutput(str) emitted after the client has sent some output
    @signal clientRawInputSent() emitted after the data was sent to the
        debug client
    @signal clientLine(filename, lineno, forStack) emitted after the
        debug client has executed a line of code
    @signal clientStack(stack) emitted after the debug client has executed a
        line of code
    @signal clientThreadList(currentId, threadList) emitted after a thread list
        has been received
    @signal clientThreadSet() emitted after the client has acknowledged the
        change of the current thread
    @signal clientVariables(scope, variables) emitted after a variables dump
        has been received
    @signal clientVariable(scope, variables) emitted after a dump for one class
        variable has been received
    @signal clientStatement(bool) emitted after an interactive command has
        been executed. The parameter is 0 to indicate that the command is
        complete and 1 if it needs more input.
    @signal clientException(exception) emitted after an exception occured on
        the client side
    @signal clientSyntaxError(exception) emitted after a syntax error has been
        detected on the client side
    @signal clientSignal(signal) emitted after a signal has been generated on
        the client side
    @signal clientExit(int, str, bool) emitted after the client has exited
        giving the exit status, an exit message and an indication to be quiet
    @signal clientClearBreak(filename, lineno) emitted after the debug client
        has decided to clear a temporary breakpoint
    @signal clientBreakConditionError(fn, lineno) emitted after the client has
        signaled a syntax error in a breakpoint condition
    @signal clientClearWatch(condition) emitted after the debug client
            has decided to clear a temporary watch expression
    @signal clientWatchConditionError(condition) emitted after the client has
        signaled a syntax error in a watch expression
    @signal clientRawInput(prompt, echo) emitted after a raw input request was
        received
    @signal clientBanner(version, platform, dbgclient, venvname) emitted after
        the client banner data was received
    @signal clientCapabilities(capabilities, cltype, venvname) emitted after
        the clients capabilities were received
    @signal clientCompletionList(completionList, text) emitted after the client
        the commandline completion list and the reworked searchstring was
        received from the client
    @signal passiveDebugStarted(str, bool) emitted after the debug client has
        connected in passive debug mode
    @signal clientGone(bool) emitted if the client went away (planned or
        unplanned)
    @signal clientInterpreterChanged(str) emitted to signal a change of the
        client interpreter
    @signal utDiscovered(testCases, exc_type, exc_value) emitted after the
        client has performed a test case discovery action
    @signal utPrepared(nrTests, exc_type, exc_value) emitted after the client
        has loaded a unittest suite
    @signal utFinished() emitted after the client signalled the end of the
        unittest
    @signal utStartTest(testname, testdocu) emitted after the client has
        started a test
    @signal utStopTest() emitted after the client has finished a test
    @signal utTestFailed(testname, exc_info, id) emitted after the client
        reported a failed test
    @signal utTestErrored(testname, exc_info, id) emitted after the client
        reported an errored test
    @signal utTestSkipped(testname, reason, id) emitted after the client
        reported a skipped test
    @signal utTestFailedExpected(testname, exc_info, id) emitted after the
        client reported an expected test failure
    @signal utTestSucceededUnexpected(testname, id) emitted after the client
        reported an unexpected test success
    @signal callTraceInfo emitted after the client reported the call trace
        data (isCall, fromFile, fromLine, fromFunction, toFile, toLine,
        toFunction)
    @signal appendStdout(msg) emitted when a passive debug connection is
        established or lost
    """
    clientClearBreak = pyqtSignal(str, int)
    clientClearWatch = pyqtSignal(str)
    clientGone = pyqtSignal(bool)
    clientProcessStdout = pyqtSignal(str)
    clientProcessStderr = pyqtSignal(str)
    clientRawInputSent = pyqtSignal()
    clientOutput = pyqtSignal(str)
    clientLine = pyqtSignal(str, int, bool)
    clientStack = pyqtSignal(list)
    clientThreadList = pyqtSignal('PyQt_PyObject', list)
    clientThreadSet = pyqtSignal()
    clientVariables = pyqtSignal(int, list)
    clientVariable = pyqtSignal(int, list)
    clientStatement = pyqtSignal(bool)
    clientException = pyqtSignal(str, str, list)
    clientSyntaxError = pyqtSignal(str, str, int, int)
    clientSignal = pyqtSignal(str, str, int, str, str)
    clientExit = pyqtSignal(int, str, bool)
    clientBreakConditionError = pyqtSignal(str, int)
    clientWatchConditionError = pyqtSignal(str)
    clientRawInput = pyqtSignal(str, bool)
    clientBanner = pyqtSignal(str, str, str, str)
    clientCapabilities = pyqtSignal(int, str, str)
    clientCompletionList = pyqtSignal(list, str)
    clientInterpreterChanged = pyqtSignal(str)
    utDiscovered = pyqtSignal(list, str, str)
    utPrepared = pyqtSignal(int, str, str)
    utStartTest = pyqtSignal(str, str)
    utStopTest = pyqtSignal()
    utTestFailed = pyqtSignal(str, str, str)
    utTestErrored = pyqtSignal(str, str, str)
    utTestSkipped = pyqtSignal(str, str, str)
    utTestFailedExpected = pyqtSignal(str, str, str)
    utTestSucceededUnexpected = pyqtSignal(str, str)
    utFinished = pyqtSignal()
    passiveDebugStarted = pyqtSignal(str, bool)
    callTraceInfo = pyqtSignal(bool, str, str, str, str, str, str)
    appendStdout = pyqtSignal(str)
    
    def __init__(self, originalPathString, preventPassiveDebugging=False):
        """
        Constructor
        
        @param originalPathString original PATH environment variable
        @type str
        @param preventPassiveDebugging flag overriding the PassiveDbgEnabled
            setting
        @type bool
        """
        super(DebugServer, self).__init__()
        
        self.__originalPathString = originalPathString
        
        self.__debuggerInterfaces = {}
        # the interface name is the key, a function to get the
        # registration data is the value
        self.__debuggerInterfaceRegistry = {}
        # the client language is the key, a list containing the client
        # capabilities, a list of associated file extensions, a
        # function reference to create the debugger interface (see
        # __createDebuggerInterface() below) and the interface name is
        # the value
        
        # create our models
        self.breakpointModel = BreakPointModel(self)
        self.watchpointModel = WatchPointModel(self)
        self.watchSpecialCreated = self.tr(
            "created", "must be same as in EditWatchpointDialog")
        self.watchSpecialChanged = self.tr(
            "changed", "must be same as in EditWatchpointDialog")
        
        self.networkInterface = Preferences.getDebugger("NetworkInterface")
        if self.networkInterface == "all":
            hostAddress = QHostAddress("0.0.0.0")  # QHostAddress.Any)
        elif self.networkInterface == "allv6":
            hostAddress = QHostAddress("::")  # QHostAddress.AnyIPv6)
        else:
            hostAddress = QHostAddress(self.networkInterface)
        self.networkInterfaceName, self.networkInterfaceIndex = (
            self.__getNetworkInterfaceAndIndex(self.networkInterface))
        
        if (not preventPassiveDebugging and
                Preferences.getDebugger("PassiveDbgEnabled")):
            sock = Preferences.getDebugger("PassiveDbgPort")  # default: 42424
            self.listen(hostAddress, sock)
            self.passive = True
            self.passiveClientExited = False
        else:
            if hostAddress.toString().lower().startswith("fe80"):
                hostAddress.setScopeId(self.networkInterfaceName)
            self.listen(hostAddress)
            self.passive = False
        
        self.debuggerInterface = None
        self.debugging = False
        self.running = False
        self.clientProcess = None
        self.clientInterpreter = ""
        self.clientType = Preferences.Prefs.settings.value('DebugClient/Type')
        if self.clientType is None:
            self.clientType = 'Python3'
        # Change clientType if dependent interpreter does not exist anymore
        # (maybe deinstalled,...)
        elif self.clientType == 'Python2' and Preferences.getDebugger(
                "Python2VirtualEnv") == '' and sys.version_info[0] >= 3:
            self.clientType = 'Python3'
        elif self.clientType == 'Python3' and Preferences.getDebugger(
                "Python3VirtualEnv") == '' and sys.version_info[0] == 2:
            self.clientType = 'Python2'
        
        self.lastClientType = ''
        self.__autoClearShell = False
        self.__forProject = False
        
        self.clientClearBreak.connect(self.__clientClearBreakPoint)
        self.clientClearWatch.connect(self.__clientClearWatchPoint)
        self.newConnection.connect(self.__newConnection)
        
        self.breakpointModel.rowsAboutToBeRemoved.connect(
            self.__deleteBreakPoints)
        self.breakpointModel.dataAboutToBeChanged.connect(
            self.__breakPointDataAboutToBeChanged)
        self.breakpointModel.dataChanged.connect(self.__changeBreakPoints)
        self.breakpointModel.rowsInserted.connect(self.__addBreakPoints)
        
        self.watchpointModel.rowsAboutToBeRemoved.connect(
            self.__deleteWatchPoints)
        self.watchpointModel.dataAboutToBeChanged.connect(
            self.__watchPointDataAboutToBeChanged)
        self.watchpointModel.dataChanged.connect(self.__changeWatchPoints)
        self.watchpointModel.rowsInserted.connect(self.__addWatchPoints)
        
        self.__maxVariableSize = Preferences.getDebugger("MaxVariableSize")
        
        self.__registerDebuggerInterfaces()
        
    def getHostAddress(self, localhost):
        """
        Public method to get the IP address or hostname the debug server is
        listening.
        
        @param localhost flag indicating to return the address for localhost
            (boolean)
        @return IP address or hostname (string)
        """
        if self.networkInterface == "all":
            if localhost:
                return "127.0.0.1"
            else:
                return "{0}@@v4".format(QHostInfo.localHostName())
        elif self.networkInterface == "allv6":
            if localhost:
                return "::1"
            else:
                return "{0}@@v6".format(QHostInfo.localHostName())
        else:
            return "{0}@@i{1}".format(self.networkInterface,
                                      self.networkInterfaceIndex)
        
    def __getNetworkInterfaceAndIndex(self, address):
        """
        Private method to determine the network interface and the interface
        index.
        
        @param address address to determine the info for (string)
        @return tuple of network interface name (string) and index (integer)
        """
        if address not in ["all", "allv6"]:
            for networkInterface in QNetworkInterface.allInterfaces():
                addressEntries = networkInterface.addressEntries()
                if len(addressEntries) > 0:
                    for addressEntry in addressEntries:
                        if (addressEntry.ip().toString().lower() ==
                                address.lower()):
                            return (networkInterface.humanReadableName(),
                                    networkInterface.index())
        
        return "", 0
        
    def preferencesChanged(self):
        """
        Public slot to handle the preferencesChanged signal.
        """
        registeredInterfaces = {}
        for interfaceName in self.__debuggerInterfaces:
            registeredInterfaces[interfaceName] = (
                self.__debuggerInterfaces[interfaceName])
        
        self.__debuggerInterfaceRegistry = {}
        for interfaceName, getRegistryData in registeredInterfaces.items():
            self.registerDebuggerInterface(interfaceName, getRegistryData,
                                           reregister=True)
        
        self.__maxVariableSize = Preferences.getDebugger("MaxVariableSize")
        
    def registerDebuggerInterface(self, interfaceName, getRegistryData,
                                  reregister=False):
        """
        Public method to register a debugger interface.
        
        @param interfaceName name of the debugger interface
        @type str
        @param getRegistryData reference to a function to be called
            to get the debugger interface details. This method shall
            return the client language, the client capabilities, the
            list of associated file extensions and a function reference
            to create the debugger interface (see __createDebuggerInterface())
        @type function
        @param reregister flag indicating to re-register the interface
        @type bool
        """
        if interfaceName in self.__debuggerInterfaces and not reregister:
            E5MessageBox.warning(
                None,
                self.tr("Register Debugger Interface"),
                self.tr("""<p>The debugger interface <b>{0}</b> has already"""
                        """ been registered. Ignoring this request.</p>"""))
            return
        
        if not reregister:
            self.__debuggerInterfaces[interfaceName] = getRegistryData
        registryDataList = getRegistryData()
        if registryDataList:
            for (clientLanguage, clientCapabilities, clientExtensions,
                 interfaceCreator) in registryDataList:
                self.__debuggerInterfaceRegistry[clientLanguage] = [
                    clientCapabilities, clientExtensions, interfaceCreator,
                    interfaceName]
        
    def unregisterDebuggerInterface(self, interfaceName):
        """
        Public method to unregister a debugger interface.
        
        @param interfaceName interfaceName of the debugger interface
        @type str
        """
        if interfaceName in self.__debuggerInterfaces:
            clientLanguages = []
            for clientLanguage, registryData in (
                    self.__debuggerInterfaceRegistry.items()):
                if interfaceName == registryData[-1]:
                    clientLanguages.append(clientLanguage)
            for clientLanguage in clientLanguages:
                del self.__debuggerInterfaceRegistry[clientLanguage]
            del self.__debuggerInterfaces[interfaceName]
        
    def __findLanguageForExtension(self, ext):
        """
        Private method to get the language associated with a file extension.
        
        @param ext file extension
        @type str
        @return associated language
        @rtype str
        """
        for language in self.__debuggerInterfaceRegistry:
            if ext in self.__debuggerInterfaceRegistry[language][1]:
                return language
        
        return ""
        
    def __registerDebuggerInterfaces(self):
        """
        Private method to register the available internal debugger interfaces.
        """
        for name, interface in DebuggerInterfaces.items():
            modName = "Debugger.{0}".format(interface)
            mod = __import__(modName)
            components = modName.split('.')
            for comp in components[1:]:
                mod = getattr(mod, comp)
            
            self.registerDebuggerInterface(name, mod.getRegistryData)
        
    def getSupportedLanguages(self, shellOnly=False):
        """
        Public slot to return the supported programming languages.
        
        @param shellOnly flag indicating only languages supporting an
            interactive shell should be returned
        @return list of supported languages (list of strings)
        """
        languages = list(self.__debuggerInterfaceRegistry.keys())
        try:
            languages.remove("None")
        except ValueError:
            pass    # it is not in the list
        
        if shellOnly:
            languages = [lang for lang in languages
                         if self.__debuggerInterfaceRegistry[lang][0] &
                         DebugClientCapabilities.HasShell]
        
        return languages[:]
        
    def getExtensions(self, language):
        """
        Public slot to get the extensions associated with the given language.
        
        @param language language to get extensions for (string)
        @return tuple of extensions associated with the language
            (tuple of strings)
        """
        if language in self.__debuggerInterfaceRegistry:
            return tuple(self.__debuggerInterfaceRegistry[language][1])
        else:
            return ()
        
    def __createDebuggerInterface(self, clientType=None):
        """
        Private slot to create the debugger interface object.
        
        @param clientType type of the client interface to be created (string)
        """
        if self.lastClientType != self.clientType or clientType is not None:
            if clientType is None:
                clientType = self.clientType
            if clientType in self.__debuggerInterfaceRegistry:
                self.debuggerInterface = (
                    self.__debuggerInterfaceRegistry[clientType][2](
                        self, self.passive))
            else:
                self.debuggerInterface = (
                    self.__debuggerInterfaceRegistry["None"][2](
                        self, self.passive))
                self.clientType = "None"
        
    def __setClientType(self, clType):
        """
        Private method to set the client type.
        
        @param clType type of client to be started (string)
        """
        if clType is not None and clType in self.getSupportedLanguages():
            self.clientType = clType
            Preferences.Prefs.settings.setValue(
                'DebugClient/Type', self.clientType)
        
    def startClient(self, unplanned=True, clType=None, forProject=False,
                    runInConsole=False, venvName="", workingDir=None):
        """
        Public method to start a debug client.
        
        @keyparam unplanned flag indicating that the client has died
        @type bool
        @keyparam clType type of client to be started
        @type str
        @keyparam forProject flag indicating a project related action
        @type bool
        @keyparam runInConsole flag indicating to start the debugger in a
            console window
        @type bool
        @keyparam venvName name of the virtual environment to be used
        @type str
        @keyparam workingDir directory to start the debugger client in
        @type str
        """
        self.running = False
        
        if not self.passive or not self.passiveClientExited:
            if self.debuggerInterface and self.debuggerInterface.isConnected():
                self.shutdownServer()
                self.debugging = False
                self.clientGone.emit(unplanned and self.debugging)
        
        if clType:
            if clType not in self.getSupportedLanguages():
                # a not supported client language was requested
                return
            
            self.__setClientType(clType)
        
        # only start the client, if we are not in passive mode
        if not self.passive:
            if self.clientProcess:
                self.clientProcess.kill()
                self.clientProcess.waitForFinished(1000)
                self.clientProcess.deleteLater()
                self.clientProcess = None
            
            self.__forProject = forProject
            self.__createDebuggerInterface()
            if forProject:
                project = e5App().getObject("Project")
                if not project.isDebugPropertiesLoaded():
                    self.clientProcess, isNetworked, clientInterpreter = (
                        self.debuggerInterface.startRemote(
                            self.serverPort(), runInConsole, venvName,
                            self.__originalPathString, workingDir=workingDir))
                else:
                    self.clientProcess, isNetworked, clientInterpreter = (
                        self.debuggerInterface.startRemoteForProject(
                            self.serverPort(), runInConsole, venvName,
                            self.__originalPathString, workingDir=workingDir))
            else:
                self.clientProcess, isNetworked, clientInterpreter = (
                    self.debuggerInterface.startRemote(
                        self.serverPort(), runInConsole, venvName,
                        self.__originalPathString, workingDir=workingDir))
            
            if self.clientProcess:
                self.clientProcess.readyReadStandardError.connect(
                    self.__clientProcessError)
                self.clientProcess.readyReadStandardOutput.connect(
                    self.__clientProcessOutput)
                
                # Perform actions necessary, if client type has changed
                if self.lastClientType != self.clientType:
                    self.lastClientType = self.clientType
                    self.remoteBanner()
                elif self.__autoClearShell:
                    self.__autoClearShell = False
                    self.remoteBanner()
##                self.remoteClientVariables(0, [], 0)
##                self.remoteClientVariables(1, [], 0)
            else:
                if clType and self.lastClientType:
                    self.__setClientType(self.lastClientType)
        else:
            self.__createDebuggerInterface("None")
            clientInterpreter = ""
        
        if clientInterpreter != self.clientInterpreter:
            self.clientInterpreter = clientInterpreter
            self.clientInterpreterChanged.emit(clientInterpreter)

    def __clientProcessOutput(self):
        """
        Private slot to process client output received via stdout.
        """
        output = str(self.clientProcess.readAllStandardOutput(),
                     Preferences.getSystem("IOEncoding"),
                     'replace')
        self.clientProcessStdout.emit(output)
        
    def __clientProcessError(self):
        """
        Private slot to process client output received via stderr.
        """
        error = str(self.clientProcess.readAllStandardError(),
                    Preferences.getSystem("IOEncoding"),
                    'replace')
        self.clientProcessStderr.emit(error)
        
    def __clientClearBreakPoint(self, fn, lineno):
        """
        Private slot to handle the clientClearBreak signal.
        
        @param fn filename of breakpoint to clear (string)
        @param lineno line number of breakpoint to clear (integer)
        """
        if self.debugging:
            index = self.breakpointModel.getBreakPointIndex(fn, lineno)
            self.breakpointModel.deleteBreakPointByIndex(index)

    def __deleteBreakPoints(self, parentIndex, start, end):
        """
        Private slot to delete breakpoints.
        
        @param parentIndex index of parent item (QModelIndex)
        @param start start row (integer)
        @param end end row (integer)
        """
        if self.debugging:
            for row in range(start, end + 1):
                index = self.breakpointModel.index(row, 0, parentIndex)
                fn, lineno = (
                    self.breakpointModel.getBreakPointByIndex(index)[0:2])
                self.remoteBreakpoint(fn, lineno, False)

    def __changeBreakPoints(self, startIndex, endIndex):
        """
        Private slot to set changed breakpoints.
        
        @param startIndex starting index of the change breakpoins (QModelIndex)
        @param endIndex ending index of the change breakpoins (QModelIndex)
        """
        if self.debugging:
            self.__addBreakPoints(
                QModelIndex(), startIndex.row(), endIndex.row())

    def __breakPointDataAboutToBeChanged(self, startIndex, endIndex):
        """
        Private slot to handle the dataAboutToBeChanged signal of the
        breakpoint model.
        
        @param startIndex start index of the rows to be changed (QModelIndex)
        @param endIndex end index of the rows to be changed (QModelIndex)
        """
        if self.debugging:
            self.__deleteBreakPoints(
                QModelIndex(), startIndex.row(), endIndex.row())
        
    def __addBreakPoints(self, parentIndex, start, end):
        """
        Private slot to add breakpoints.
        
        @param parentIndex index of parent item (QModelIndex)
        @param start start row (integer)
        @param end end row (integer)
        """
        if self.debugging:
            for row in range(start, end + 1):
                index = self.breakpointModel.index(row, 0, parentIndex)
                fn, line, cond, temp, enabled, ignorecount = (
                    self.breakpointModel.getBreakPointByIndex(index)[:6])
                self.remoteBreakpoint(fn, line, True, cond, temp)
                if not enabled:
                    self.__remoteBreakpointEnable(fn, line, False)
                if ignorecount:
                    self.__remoteBreakpointIgnore(fn, line, ignorecount)

    def __makeWatchCondition(self, cond, special):
        """
        Private method to construct the condition string.
        
        @param cond condition (string)
        @param special special condition (string)
        @return condition string (string)
        """
        if special == "":
            _cond = cond
        else:
            if special == self.watchSpecialCreated:
                _cond = "{0} ??created??".format(cond)
            elif special == self.watchSpecialChanged:
                _cond = "{0} ??changed??".format(cond)
        return _cond
        
    def __splitWatchCondition(self, cond):
        """
        Private method to split a remote watch expression.
        
        @param cond remote expression (string)
        @return tuple of local expression (string) and special condition
            (string)
        """
        if cond.endswith(" ??created??"):
            cond, special = cond.split()
            special = self.watchSpecialCreated
        elif cond.endswith(" ??changed??"):
            cond, special = cond.split()
            special = self.watchSpecialChanged
        else:
            cond = cond
            special = ""
        
        return cond, special
        
    def __clientClearWatchPoint(self, condition):
        """
        Private slot to handle the clientClearWatch signal.
        
        @param condition expression of watch expression to clear (string)
        """
        if self.debugging:
            cond, special = self.__splitWatchCondition(condition)
            index = self.watchpointModel.getWatchPointIndex(cond, special)
            self.watchpointModel.deleteWatchPointByIndex(index)
        
    def __deleteWatchPoints(self, parentIndex, start, end):
        """
        Private slot to delete watch expressions.
        
        @param parentIndex index of parent item (QModelIndex)
        @param start start row (integer)
        @param end end row (integer)
        """
        if self.debugging:
            for row in range(start, end + 1):
                index = self.watchpointModel.index(row, 0, parentIndex)
                cond, special = (
                    self.watchpointModel.getWatchPointByIndex(index)[0:2])
                cond = self.__makeWatchCondition(cond, special)
                self.__remoteWatchpoint(cond, False)
        
    def __watchPointDataAboutToBeChanged(self, startIndex, endIndex):
        """
        Private slot to handle the dataAboutToBeChanged signal of the
        watch expression model.
        
        @param startIndex start index of the rows to be changed (QModelIndex)
        @param endIndex end index of the rows to be changed (QModelIndex)
        """
        if self.debugging:
            self.__deleteWatchPoints(
                QModelIndex(), startIndex.row(), endIndex.row())
        
    def __addWatchPoints(self, parentIndex, start, end):
        """
        Private slot to set a watch expression.
        
        @param parentIndex index of parent item (QModelIndex)
        @param start start row (integer)
        @param end end row (integer)
        """
        if self.debugging:
            for row in range(start, end + 1):
                index = self.watchpointModel.index(row, 0, parentIndex)
                cond, special, temp, enabled, ignorecount = (
                    self.watchpointModel.getWatchPointByIndex(index)[:5])
                cond = self.__makeWatchCondition(cond, special)
                self.__remoteWatchpoint(cond, True, temp)
                if not enabled:
                    self.__remoteWatchpointEnable(cond, False)
                if ignorecount:
                    self.__remoteWatchpointIgnore(cond, ignorecount)
        
    def __changeWatchPoints(self, startIndex, endIndex):
        """
        Private slot to set changed watch expressions.
        
        @param startIndex start index of the rows to be changed (QModelIndex)
        @param endIndex end index of the rows to be changed (QModelIndex)
        """
        if self.debugging:
            self.__addWatchPoints(
                QModelIndex(), startIndex.row(), endIndex.row())
        
    def getClientCapabilities(self, clientType):
        """
        Public method to retrieve the debug clients capabilities.
        
        @param clientType debug client type (string)
        @return debug client capabilities (integer)
        """
        try:
            return self.__debuggerInterfaceRegistry[clientType][0]
        except KeyError:
            return 0    # no capabilities
        
    def getClientInterpreter(self):
        """
        Public method to get the interpreter of the debug client.
        
        @return interpreter of the debug client (string)
        """
        return self.clientInterpreter
    
    def getClientType(self):
        """
        Public method to get the currently running debug client type.
        
        @return debug client type
        @rtype str
        """
        return self.clientType
    
    def isClientProcessUp(self):
        """
        Public method to check, if the debug client process is up.
        
        @return flag indicating a running debug client process
        @rtype bool
        """
        return self.clientProcess is not None
    
    def __newConnection(self):
        """
        Private slot to handle a new connection.
        """
        sock = self.nextPendingConnection()
        peerAddress = sock.peerAddress().toString()
        if peerAddress not in Preferences.getDebugger("AllowedHosts"):
            # the peer is not allowed to connect
            res = E5MessageBox.yesNo(
                None,
                self.tr("Connection from illegal host"),
                self.tr(
                    """<p>A connection was attempted by the illegal host"""
                    """ <b>{0}</b>. Accept this connection?</p>""")
                .format(peerAddress),
                icon=E5MessageBox.Warning)
            if not res:
                sock.abort()
                return
            else:
                allowedHosts = Preferences.getDebugger("AllowedHosts")
                allowedHosts.append(peerAddress)
                Preferences.setDebugger("AllowedHosts", allowedHosts)
        
        if self.passive:
            self.__createDebuggerInterface(
                Preferences.getDebugger("PassiveDbgType"))
        
        accepted = self.debuggerInterface.newConnection(sock)
        if accepted:
            # Perform actions necessary, if client type has changed
            if self.lastClientType != self.clientType:
                self.lastClientType = self.clientType
                self.remoteBanner()
            elif self.__autoClearShell:
                self.__autoClearShell = False
                self.remoteBanner()
            elif self.passive:
                self.remoteBanner()
            
            self.debuggerInterface.flush()

    def shutdownServer(self):
        """
        Public method to cleanly shut down.
        
        It closes our socket and shuts down
        the debug client. (Needed on Win OS)
        """
        if self.debuggerInterface is not None:
            self.debuggerInterface.shutdown()

    def remoteEnvironment(self, env):
        """
        Public method to set the environment for a program to debug, run, ...
        
        @param env environment settings (string)
        """
        envlist = Utilities.parseEnvironmentString(env)
        envdict = {}
        for el in envlist:
            try:
                key, value = el.split('=', 1)
                if value.startswith('"') or value.startswith("'"):
                    value = value[1:-1]
                envdict[key] = value
            except ValueError:
                pass
        self.debuggerInterface.remoteEnvironment(envdict)
        
    def remoteLoad(self, venvName, fn, argv, wd, env, autoClearShell=True,
                   tracePython=False, autoContinue=True, forProject=False,
                   runInConsole=False, autoFork=False, forkChild=False,
                   clientType="", enableCallTrace=False):
        """
        Public method to load a new program to debug.
        
        @param venvName name of the virtual environment to be used
        @type str
        @param fn the filename to debug
        @type str
        @param argv the command line arguments to pass to the program
        @type str
        @param wd the working directory for the program
        @type str
        @param env environment parameter settings
        @type str
        @keyparam autoClearShell flag indicating, that the interpreter window
            should be cleared
        @type bool
        @keyparam tracePython flag indicating if the Python library should be
            traced as well
        @type bool
        @keyparam autoContinue flag indicating, that the debugger should not
            stop at the first executable line
        @type bool
        @keyparam forProject flag indicating a project related action
        @type bool
        @keyparam runInConsole flag indicating to start the debugger in a
            console window
        @type bool
        @keyparam autoFork flag indicating the automatic fork mode
        @type bool
        @keyparam forkChild flag indicating to debug the child after forking
        @type bool
        @keyparam clientType client type to be used
        @type str
        @keyparam enableCallTrace flag indicating to enable the call trace
            function
        @type bool
        """
        self.__autoClearShell = autoClearShell
        self.__autoContinue = autoContinue
        
        if clientType not in self.getSupportedLanguages():
            # a not supported client language was requested
            E5MessageBox.critical(
                None,
                self.tr("Start Debugger"),
                self.tr(
                    """<p>The debugger type <b>{0}</b> is not supported"""
                    """ or not configured.</p>""").format(clientType)
            )
            return
        
        # Restart the client
        try:
            if clientType:
                self.__setClientType(clientType)
            else:
                self.__setClientType(
                    self.__findLanguageForExtension(os.path.splitext(fn)[1]))
        except KeyError:
            self.__setClientType('Python3')    # assume it is a Python3 file
        self.startClient(False, forProject=forProject,
                         runInConsole=runInConsole, venvName=venvName)
        
        self.setCallTraceEnabled(enableCallTrace)
        self.remoteEnvironment(env)
        
        self.debuggerInterface.remoteLoad(fn, argv, wd, tracePython,
                                          autoContinue, autoFork, forkChild)
        self.debugging = True
        self.running = True
        self.__restoreBreakpoints()
        self.__restoreWatchpoints()

    def remoteRun(self, venvName, fn, argv, wd, env, autoClearShell=True,
                  forProject=False, runInConsole=False, autoFork=False,
                  forkChild=False, clientType=""):
        """
        Public method to load a new program to run.
        
        @param venvName name of the virtual environment to be used
        @type str
        @param fn the filename to debug
        @type str
        @param argv the command line arguments to pass to the program
        @type str
        @param wd the working directory for the program
        @type str
        @param env environment parameter settings
        @type str
        @keyparam autoClearShell flag indicating, that the interpreter window
            should be cleared
        @type bool
        @keyparam forProject flag indicating a project related action
        @type bool
        @keyparam runInConsole flag indicating to start the debugger in a
            console window
        @type bool
        @keyparam autoFork flag indicating the automatic fork mode
        @type bool
        @keyparam forkChild flag indicating to debug the child after forking
        @type bool
        @keyparam clientType client type to be used
        @type str
        """
        self.__autoClearShell = autoClearShell
        
        if clientType not in self.getSupportedLanguages():
            E5MessageBox.critical(
                None,
                self.tr("Start Debugger"),
                self.tr(
                    """<p>The debugger type <b>{0}</b> is not supported"""
                    """ or not configured.</p>""").format(clientType)
            )
            # a not supported client language was requested
            return
        
        # Restart the client
        try:
            if clientType:
                self.__setClientType(clientType)
            else:
                self.__setClientType(
                    self.__findLanguageForExtension(os.path.splitext(fn)[1]))
        except KeyError:
            self.__setClientType('Python3')    # assume it is a Python3 file
        self.startClient(False, forProject=forProject,
                         runInConsole=runInConsole, venvName=venvName)
        
        self.remoteEnvironment(env)
        
        self.debuggerInterface.remoteRun(fn, argv, wd, autoFork, forkChild)
        self.debugging = False
        self.running = True

    def remoteCoverage(self, venvName, fn, argv, wd, env,
                       autoClearShell=True, erase=False, forProject=False,
                       runInConsole=False, clientType=""):
        """
        Public method to load a new program to collect coverage data.
        
        @param venvName name of the virtual environment to be used
        @type str
        @param fn the filename to debug
        @type str
        @param argv the command line arguments to pass to the program
        @type str
        @param wd the working directory for the program
        @type str
        @param env environment parameter settings
        @type str
        @keyparam autoClearShell flag indicating, that the interpreter window
            should be cleared
        @type bool
        @keyparam erase flag indicating that coverage info should be
            cleared first
        @type bool
        @keyparam forProject flag indicating a project related action
        @type bool
        @keyparam runInConsole flag indicating to start the debugger in a
            console window
        @type bool
        @keyparam clientType client type to be used
        @type str
        """
        self.__autoClearShell = autoClearShell
        
        if clientType not in self.getSupportedLanguages():
            # a not supported client language was requested
            E5MessageBox.critical(
                None,
                self.tr("Start Debugger"),
                self.tr(
                    """<p>The debugger type <b>{0}</b> is not supported"""
                    """ or not configured.</p>""").format(clientType)
            )
            return
        
        # Restart the client
        try:
            if clientType:
                self.__setClientType(clientType)
            else:
                self.__setClientType(
                    self.__findLanguageForExtension(os.path.splitext(fn)[1]))
        except KeyError:
            self.__setClientType('Python3')    # assume it is a Python3 file
        self.startClient(False, forProject=forProject,
                         runInConsole=runInConsole, venvName=venvName)
        
        self.remoteEnvironment(env)
        
        self.debuggerInterface.remoteCoverage(fn, argv, wd, erase)
        self.debugging = False
        self.running = True

    def remoteProfile(self, venvName, fn, argv, wd, env,
                      autoClearShell=True, erase=False, forProject=False,
                      runInConsole=False, clientType=""):
        """
        Public method to load a new program to collect profiling data.
        
        @param venvName name of the virtual environment to be used
        @type str
        @param fn the filename to debug
        @type str
        @param argv the command line arguments to pass to the program
        @type str
        @param wd the working directory for the program
        @type str
        @param env environment parameter settings
        @type str
        @keyparam autoClearShell flag indicating, that the interpreter window
            should be cleared
        @type bool
        @keyparam erase flag indicating that coverage info should be
            cleared first
        @type bool
        @keyparam forProject flag indicating a project related action
        @type bool
        @keyparam runInConsole flag indicating to start the debugger in a
            console window
        @type bool
        @keyparam clientType client type to be used
        @type str
        """
        self.__autoClearShell = autoClearShell
        
        if clientType not in self.getSupportedLanguages():
            # a not supported client language was requested
            E5MessageBox.critical(
                None,
                self.tr("Start Debugger"),
                self.tr(
                    """<p>The debugger type <b>{0}</b> is not supported"""
                    """ or not configured.</p>""").format(clientType)
            )
            return
        
        # Restart the client
        try:
            if clientType:
                self.__setClientType(clientType)
            else:
                self.__setClientType(
                    self.__findLanguageForExtension(os.path.splitext(fn)[1]))
        except KeyError:
            self.__setClientType('Python3')    # assume it is a Python3 file
        self.startClient(False, forProject=forProject,
                         runInConsole=runInConsole, venvName=venvName)
        
        self.remoteEnvironment(env)
        
        self.debuggerInterface.remoteProfile(fn, argv, wd, erase)
        self.debugging = False
        self.running = True

    def remoteStatement(self, stmt):
        """
        Public method to execute a Python statement.
        
        @param stmt the Python statement to execute (string). It
              should not have a trailing newline.
        """
        self.debuggerInterface.remoteStatement(stmt)

    def remoteStep(self):
        """
        Public method to single step the debugged program.
        """
        self.debuggerInterface.remoteStep()

    def remoteStepOver(self):
        """
        Public method to step over the debugged program.
        """
        self.debuggerInterface.remoteStepOver()

    def remoteStepOut(self):
        """
        Public method to step out the debugged program.
        """
        self.debuggerInterface.remoteStepOut()

    def remoteStepQuit(self):
        """
        Public method to stop the debugged program.
        """
        self.debuggerInterface.remoteStepQuit()

    def remoteContinue(self, special=False):
        """
        Public method to continue the debugged program.
        
        @param special flag indicating a special continue operation
        """
        self.debuggerInterface.remoteContinue(special)

    def remoteMoveIP(self, line):
        """
        Public method to move the instruction pointer to a different line.
        
        @param line the new line, where execution should be continued
        """
        self.debuggerInterface.remoteMoveIP(line)

    def remoteBreakpoint(self, fn, line, setBreakpoint, cond=None, temp=False):
        """
        Public method to set or clear a breakpoint.
        
        @param fn filename the breakpoint belongs to (string)
        @param line linenumber of the breakpoint (int)
        @param setBreakpoint flag indicating setting or resetting a breakpoint
            (boolean)
        @param cond condition of the breakpoint (string)
        @param temp flag indicating a temporary breakpoint (boolean)
        """
        self.debuggerInterface.remoteBreakpoint(fn, line, setBreakpoint, cond,
                                                temp)
        
    def __remoteBreakpointEnable(self, fn, line, enable):
        """
        Private method to enable or disable a breakpoint.
        
        @param fn filename the breakpoint belongs to (string)
        @param line linenumber of the breakpoint (int)
        @param enable flag indicating enabling or disabling a breakpoint
            (boolean)
        """
        self.debuggerInterface.remoteBreakpointEnable(fn, line, enable)
        
    def __remoteBreakpointIgnore(self, fn, line, count):
        """
        Private method to ignore a breakpoint the next couple of occurrences.
        
        @param fn filename the breakpoint belongs to (string)
        @param line linenumber of the breakpoint (int)
        @param count number of occurrences to ignore (int)
        """
        self.debuggerInterface.remoteBreakpointIgnore(fn, line, count)
        
    def __remoteWatchpoint(self, cond, setWatch, temp=False):
        """
        Private method to set or clear a watch expression.
        
        @param cond expression of the watch expression (string)
        @param setWatch flag indicating setting or resetting a watch expression
            (boolean)
        @param temp flag indicating a temporary watch expression (boolean)
        """
        # cond is combination of cond and special (s. watch expression viewer)
        self.debuggerInterface.remoteWatchpoint(cond, setWatch, temp)
    
    def __remoteWatchpointEnable(self, cond, enable):
        """
        Private method to enable or disable a watch expression.
        
        @param cond expression of the watch expression (string)
        @param enable flag indicating enabling or disabling a watch expression
            (boolean)
        """
        # cond is combination of cond and special (s. watch expression viewer)
        self.debuggerInterface.remoteWatchpointEnable(cond, enable)
    
    def __remoteWatchpointIgnore(self, cond, count):
        """
        Private method to ignore a watch expression the next couple of
        occurrences.
        
        @param cond expression of the watch expression (string)
        @param count number of occurrences to ignore (int)
        """
        # cond is combination of cond and special (s. watch expression viewer)
        self.debuggerInterface.remoteWatchpointIgnore(cond, count)
    
    def remoteRawInput(self, s):
        """
        Public method to send the raw input to the debugged program.
        
        @param s the raw input (string)
        """
        self.debuggerInterface.remoteRawInput(s)
        self.clientRawInputSent.emit()
        
    def remoteThreadList(self):
        """
        Public method to request the list of threads from the client.
        """
        self.debuggerInterface.remoteThreadList()
        
    def remoteSetThread(self, tid):
        """
        Public method to request to set the given thread as current thread.
        
        @param tid id of the thread (integer)
        """
        self.debuggerInterface.remoteSetThread(tid)
        
    def remoteClientVariables(self, scope, filterList, framenr=0):
        """
        Public method to request the variables of the debugged program.
        
        @param scope the scope of the variables (0 = local, 1 = global)
        @param filterList list of variable types to filter out (list of int)
        @param framenr framenumber of the variables to retrieve (int)
        """
        self.debuggerInterface.remoteClientVariables(
            scope, filterList, framenr, self.__maxVariableSize)
        
    def remoteClientVariable(self, scope, filterList, var, framenr=0):
        """
        Public method to request the variables of the debugged program.
        
        @param scope the scope of the variables (0 = local, 1 = global)
        @param filterList list of variable types to filter out (list of int)
        @param var list encoded name of variable to retrieve (string)
        @param framenr framenumber of the variables to retrieve (int)
        """
        self.debuggerInterface.remoteClientVariable(
            scope, filterList, var, framenr, self.__maxVariableSize)
        
    def remoteClientSetFilter(self, scope, filterStr):
        """
        Public method to set a variables filter list.
        
        @param scope the scope of the variables (0 = local, 1 = global)
        @param filterStr regexp string for variable names to filter out
            (string)
        """
        self.debuggerInterface.remoteClientSetFilter(scope, filterStr)
        
    def setCallTraceEnabled(self, on):
        """
        Public method to set the call trace state.
        
        @param on flag indicating to enable the call trace function (boolean)
        """
        self.debuggerInterface.setCallTraceEnabled(on)
        
    def remoteBanner(self):
        """
        Public slot to get the banner info of the remote client.
        """
        self.debuggerInterface.remoteBanner()
        
    def remoteCapabilities(self):
        """
        Public slot to get the debug clients capabilities.
        """
        self.debuggerInterface.remoteCapabilities()
        
    def remoteCompletion(self, text):
        """
        Public slot to get the a list of possible commandline completions
        from the remote client.
        
        @param text the text to be completed (string)
        """
        self.debuggerInterface.remoteCompletion(text)
    
    def remoteUTDiscover(self, clientType, forProject, venvName, syspath,
                         workdir, discoveryStart):
        """
        Public method to perform a test case discovery.
        
        @param clientType client type to be used
        @type str
        @param forProject flag indicating a project related action
        @type bool
        @param venvName name of a virtual environment
        @type str
        @param syspath list of directories to be added to sys.path on the
            remote side
        @type list of str
        @param workdir path name of the working directory
        @type str
        @param discoveryStart directory to start auto-discovery at
        @type str
        """
        if clientType and clientType not in self.getSupportedLanguages():
            # a not supported client language was requested
            E5MessageBox.critical(
                None,
                self.tr("Start Debugger"),
                self.tr(
                    """<p>The debugger type <b>{0}</b> is not supported"""
                    """ or not configured.</p>""").format(clientType)
            )
            return
        
        # Restart the client if there is already a program loaded.
        try:
            if clientType:
                self.__setClientType(clientType)
        except KeyError:
            self.__setClientType('Python3')    # assume it is a Python3 file
        self.startClient(False, forProject=forProject, venvName=venvName)
        
        self.debuggerInterface.remoteUTDiscover(
            syspath, workdir, discoveryStart)
    
    def remoteUTPrepare(self, fn, tn, tfn, failed, cov, covname, coverase,
                        clientType="", forProject=False, venvName="",
                        syspath=None, workdir="", discover=False,
                        discoveryStart="", testCases=None, debug=False):
        """
        Public method to prepare a new unittest run.
        
        @param fn the filename to load
        @type str
        @param tn the testname to load
        @type str
        @param tfn the test function name to load tests from
        @type str
        @param failed list of failed test, if only failed test should be run
        @type list of str
        @param cov flag indicating collection of coverage data is requested
        @type bool
        @param covname filename to be used to assemble the coverage caches
            filename
        @type str
        @param coverase flag indicating erasure of coverage data is requested
        @type bool
        @param clientType client type to be used
        @type str
        @param forProject flag indicating a project related action
        @type bool
        @param venvName name of a virtual environment
        @type str
        @param syspath list of directories to be added to sys.path on the
            remote side
        @type list of str
        @param workdir path name of the working directory
        @type str
        @param discover flag indicating to discover the tests automatically
        @type bool
        @param discoveryStart directory to start auto-discovery at
        @type str
        @param testCases list of test cases to be loaded
        @type list of str
        @param debug flag indicating to run unittest with debugging
        @type bool
        """
        if clientType and clientType not in self.getSupportedLanguages():
            # a not supported client language was requested
            E5MessageBox.critical(
                None,
                self.tr("Start Debugger"),
                self.tr(
                    """<p>The debugger type <b>{0}</b> is not supported"""
                    """ or not configured.</p>""").format(clientType)
            )
            return
        
        # Restart the client if there is already a program loaded.
        try:
            if clientType:
                self.__setClientType(clientType)
            else:
                self.__setClientType(
                    self.__findLanguageForExtension(os.path.splitext(fn)[1]))
        except KeyError:
            self.__setClientType('Python3')    # assume it is a Python3 file
        self.startClient(False, forProject=forProject, venvName=venvName)
        
        self.debuggerInterface.remoteUTPrepare(
            fn, tn, tfn, failed, cov, covname, coverase, syspath, workdir,
            discover, discoveryStart, testCases, debug)
        self.running = True
        self.debugging = debug
        if debug:
            self.__restoreBreakpoints()
            self.__restoreWatchpoints()
        
    def remoteUTRun(self, debug=False, failfast=False):
        """
        Public method to start a unittest run.
        
        @param debug flag indicating to run unittest with debugging
        @type bool
        @param failfast flag indicating to stop at the first error
        @type bool
        """
        self.debuggerInterface.remoteUTRun(debug, failfast)
        
    def remoteUTStop(self):
        """
        public method to stop a unittest run.
        """
        self.debuggerInterface.remoteUTStop()
        
    def signalClientOutput(self, line):
        """
        Public method to process a line of client output.
        
        @param line client output (string)
        """
        self.clientOutput.emit(line)
        
    def signalClientLine(self, filename, lineno, forStack=False):
        """
        Public method to process client position feedback.
        
        @param filename name of the file currently being executed (string)
        @param lineno line of code currently being executed (integer)
        @param forStack flag indicating this is for a stack dump (boolean)
        """
        self.clientLine.emit(filename, lineno, forStack)
        
    def signalClientStack(self, stack):
        """
        Public method to process a client's stack information.
        
        @param stack list of stack entries. Each entry is a tuple of three
            values giving the filename, linenumber and method
            (list of lists of (string, integer, string))
        """
        self.clientStack.emit(stack)
        
    def signalClientThreadList(self, currentId, threadList):
        """
        Public method to process the client thread list info.
        
        @param currentId id of the current thread (integer)
        @param threadList list of dictionaries containing the thread data
        """
        self.clientThreadList.emit(currentId, threadList)
        
    def signalClientThreadSet(self):
        """
        Public method to handle the change of the client thread.
        """
        self.clientThreadSet.emit()
        
    def signalClientVariables(self, scope, variables):
        """
        Public method to process the client variables info.
        
        @param scope scope of the variables (-1 = empty global, 1 = global,
            0 = local)
        @param variables the list of variables from the client
        """
        self.clientVariables.emit(scope, variables)
        
    def signalClientVariable(self, scope, variables):
        """
        Public method to process the client variable info.
        
        @param scope scope of the variables (-1 = empty global, 1 = global,
            0 = local)
        @param variables the list of members of a classvariable from the client
        """
        self.clientVariable.emit(scope, variables)
        
    def signalClientStatement(self, more):
        """
        Public method to process the input response from the client.
        
        @param more flag indicating that more user input is required
        """
        self.clientStatement.emit(more)
        
    def signalClientException(self, exceptionType, exceptionMessage,
                              stackTrace):
        """
        Public method to process the exception info from the client.
        
        @param exceptionType type of exception raised (string)
        @param exceptionMessage message given by the exception (string)
        @param stackTrace list of stack entries with the exception position
            first. Each stack entry is a list giving the filename and the
            linenumber.
        """
        if self.running:
            self.clientException.emit(exceptionType, exceptionMessage,
                                      stackTrace)
        
    def signalClientSyntaxError(self, message, filename, lineNo, characterNo):
        """
        Public method to process the syntax error info from the client.
        
        @param message message of the syntax error (string)
        @param filename translated filename of the syntax error position
            (string)
        @param lineNo line number of the syntax error position (integer)
        @param characterNo character number of the syntax error position
            (integer)
        """
        if self.running:
            self.clientSyntaxError.emit(message, filename, lineNo, characterNo)
        
    def signalClientSignal(self, message, filename, lineNo,
                           funcName, funcArgs):
        """
        Public method to process a signal generated on the client side.
        
        @param message message of the syntax error
        @type str
        @param filename translated filename of the syntax error position
        @type str
        @param lineNo line number of the syntax error position
        @type int
        @param funcName name of the function causing the signal
        @type str
        @param funcArgs function arguments
        @type str
        """
        if self.running:
            self.clientSignal.emit(message, filename, lineNo,
                                   funcName, funcArgs)
        
    def signalClientExit(self, status, message=""):
        """
        Public method to process the client exit status.
        
        @param status exit code
        @type int
        @param message message sent with the exit
        @type str
        """
        if self.passive:
            self.__passiveShutDown()
        self.clientExit.emit(int(status), message, False)
        if Preferences.getDebugger("AutomaticReset") or (self.running and
                                                         not self.debugging):
            self.debugging = False
            self.startClient(False, forProject=self.__forProject)
        if self.passive:
            self.__createDebuggerInterface("None")
            self.signalClientOutput(self.tr('\nNot connected\n'))
            self.signalClientStatement(False)
        self.running = False
        
    def signalClientClearBreak(self, filename, lineno):
        """
        Public method to process the client clear breakpoint command.
        
        @param filename filename of the breakpoint (string)
        @param lineno line umber of the breakpoint (integer)
        """
        self.clientClearBreak.emit(filename, lineno)
        
    def signalClientBreakConditionError(self, filename, lineno):
        """
        Public method to process the client breakpoint condition error info.
        
        @param filename filename of the breakpoint (string)
        @param lineno line umber of the breakpoint (integer)
        """
        self.clientBreakConditionError.emit(filename, lineno)
        
    def signalClientClearWatch(self, condition):
        """
        Public slot to handle the clientClearWatch signal.
        
        @param condition expression of watch expression to clear (string)
        """
        self.clientClearWatch.emit(condition)
        
    def signalClientWatchConditionError(self, condition):
        """
        Public method to process the client watch expression error info.
        
        @param condition expression of watch expression to clear (string)
        """
        self.clientWatchConditionError.emit(condition)
        
    def signalClientRawInput(self, prompt, echo):
        """
        Public method to process the client raw input command.
        
        @param prompt the input prompt (string)
        @param echo flag indicating an echoing of the input (boolean)
        """
        self.clientRawInput.emit(prompt, echo)
        
    def signalClientBanner(self, version, platform, debugClient, venvName):
        """
        Public method to process the client banner info.
        
        @param version interpreter version info
        @type str
        @param platform hostname of the client
        @type str
        @param debugClient additional debugger type info
        @type str
        @param venvName name of the virtual environment
        @type str
        """
        self.clientBanner.emit(version, platform, debugClient, venvName)
    
    def signalClientCapabilities(self, capabilities, clientType, venvName):
        """
        Public method to process the client capabilities info.
        
        @param capabilities bitmaks with the client capabilities
        @type int
        @param clientType type of the debug client
        @type str
        @param venvName name of the virtual environment
        @type str
        """
        try:
            self.__debuggerInterfaceRegistry[clientType][0] = capabilities
            self.clientCapabilities.emit(capabilities, clientType, venvName)
        except KeyError:
            # ignore silently
            pass
        
    def signalClientCompletionList(self, completionList, text):
        """
        Public method to process the client auto completion info.
        
        @param completionList list of possible completions (list of strings)
        @param text the text to be completed (string)
        """
        self.clientCompletionList.emit(completionList, text)
        
    def signalClientCallTrace(self, isCall, fromFile, fromLine, fromFunction,
                              toFile, toLine, toFunction):
        """
        Public method to process the client call trace data.
        
        @param isCall flag indicating a 'call' (boolean)
        @param fromFile name of the originating file (string)
        @param fromLine line number in the originating file (string)
        @param fromFunction name of the originating function (string)
        @param toFile name of the target file (string)
        @param toLine line number in the target file (string)
        @param toFunction name of the target function (string)
        """
        self.callTraceInfo.emit(
            isCall, fromFile, fromLine, fromFunction,
            toFile, toLine, toFunction)
        
    def clientUtDiscovered(self, testCases, exceptionType, exceptionValue):
        """
        Public method to process the client unittest discover info.
        
        @param testCases list of detected test cases
        @type str
        @param exceptionType exception type
        @type str
        @param exceptionValue exception message
        @type str
        """
        self.utDiscovered.emit(testCases, exceptionType, exceptionValue)
        
    def clientUtPrepared(self, result, exceptionType, exceptionValue):
        """
        Public method to process the client unittest prepared info.
        
        @param result number of test cases (0 = error) (integer)
        @param exceptionType exception type (string)
        @param exceptionValue exception message (string)
        """
        self.utPrepared.emit(result, exceptionType, exceptionValue)
        
    def clientUtStartTest(self, testname, doc):
        """
        Public method to process the client start test info.
        
        @param testname name of the test (string)
        @param doc short description of the test (string)
        """
        self.utStartTest.emit(testname, doc)
        
    def clientUtStopTest(self):
        """
        Public method to process the client stop test info.
        """
        self.utStopTest.emit()
        
    def clientUtTestFailed(self, testname, traceback, testId):
        """
        Public method to process the client test failed info.
        
        @param testname name of the test (string)
        @param traceback lines of traceback info (list of strings)
        @param testId id of the test (string)
        """
        self.utTestFailed.emit(testname, traceback, testId)
        
    def clientUtTestErrored(self, testname, traceback, testId):
        """
        Public method to process the client test errored info.
        
        @param testname name of the test (string)
        @param traceback lines of traceback info (list of strings)
        @param testId id of the test (string)
        """
        self.utTestErrored.emit(testname, traceback, testId)
        
    def clientUtTestSkipped(self, testname, reason, testId):
        """
        Public method to process the client test skipped info.
        
        @param testname name of the test (string)
        @param reason reason for skipping the test (string)
        @param testId id of the test (string)
        """
        self.utTestSkipped.emit(testname, reason, testId)
        
    def clientUtTestFailedExpected(self, testname, traceback, testId):
        """
        Public method to process the client test failed expected info.
        
        @param testname name of the test (string)
        @param traceback lines of traceback info (list of strings)
        @param testId id of the test (string)
        """
        self.utTestFailedExpected.emit(testname, traceback, testId)
        
    def clientUtTestSucceededUnexpected(self, testname, testId):
        """
        Public method to process the client test succeeded unexpected info.
        
        @param testname name of the test (string)
        @param testId id of the test (string)
        """
        self.utTestSucceededUnexpected.emit(testname, testId)
        
    def clientUtFinished(self, status):
        """
        Public method to process the client unit test finished info.
        
        @param status exit status of the unit test
        @type int
        """
        self.utFinished.emit()
        
        self.clientExit.emit(int(status), "", True)
        self.debugging = False
        self.running = False
        
    def passiveStartUp(self, fn, exc):
        """
        Public method to handle a passive debug connection.
        
        @param fn filename of the debugged script (string)
        @param exc flag to enable exception reporting of the IDE (boolean)
        """
        self.appendStdout.emit(self.tr("Passive debug connection received\n"))
        self.passiveClientExited = False
        self.debugging = True
        self.running = True
        self.__restoreBreakpoints()
        self.__restoreWatchpoints()
        self.passiveDebugStarted.emit(fn, exc)
        
    def __passiveShutDown(self):
        """
        Private method to shut down a passive debug connection.
        """
        self.passiveClientExited = True
        self.shutdownServer()
        self.appendStdout.emit(self.tr("Passive debug connection closed\n"))
        
    def __restoreBreakpoints(self):
        """
        Private method to restore the breakpoints after a restart.
        """
        if self.debugging:
            self.__addBreakPoints(
                QModelIndex(), 0, self.breakpointModel.rowCount() - 1)
    
    def __restoreWatchpoints(self):
        """
        Private method to restore the watch expressions after a restart.
        """
        if self.debugging:
            self.__addWatchPoints(
                QModelIndex(), 0, self.watchpointModel.rowCount() - 1)
    
    def getBreakPointModel(self):
        """
        Public slot to get a reference to the breakpoint model object.
        
        @return reference to the breakpoint model object (BreakPointModel)
        """
        return self.breakpointModel

    def getWatchPointModel(self):
        """
        Public slot to get a reference to the watch expression model object.
        
        @return reference to the watch expression model object
            (WatchPointModel)
        """
        return self.watchpointModel
    
    def isConnected(self):
        """
        Public method to test, if the debug server is connected to a backend.
        
        @return flag indicating a connection (boolean)
        """
        return self.debuggerInterface and self.debuggerInterface.isConnected()
    
    def isDebugging(self):
        """
        Public method to test, if the debug server is debugging.
        
        @return flag indicating the debugging state
        @rtype bool
        """
        return self.debugging
    
    def setDebugging(self, on):
        """
        Public method to set the debugging state.
        
        @param on flag indicating the new debugging state
        @type bool
        """
        self.debugging = on
