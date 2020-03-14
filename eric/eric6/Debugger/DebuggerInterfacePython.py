# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Python3 debugger interface for the debug server.
"""


import sys
import os
import logging

from PyQt5.QtCore import (
    QObject, QTextCodec, QProcess, QProcessEnvironment, QTimer
)
from PyQt5.QtWidgets import QInputDialog

from E5Gui.E5Application import e5App
from E5Gui import E5MessageBox

from . import DebugClientCapabilities

import Preferences
import Utilities

from eric6config import getConfig


ClientDefaultCapabilities = DebugClientCapabilities.HasAll


class DebuggerInterfacePython(QObject):
    """
    Class implementing the debugger interface for the debug server for Python 2
    and Python 3.
    """
    def __init__(self, debugServer, passive, pythonVariant):
        """
        Constructor
        
        @param debugServer reference to the debug server
        @type DebugServer
        @param passive flag indicating passive connection mode
        @type bool
        @param pythonVariant Python variant to instantiate for
        @type str (one of Python2 or Python3)
        """
        super(DebuggerInterfacePython, self).__init__()
        
        self.__isNetworked = True
        self.__autoContinue = False
        
        self.debugServer = debugServer
        self.passive = passive
        self.process = None
        self.__variant = pythonVariant
        self.__startedVenv = ""
        
        self.qsock = None
        self.queue = []
        
        # set default values for capabilities of clients
        self.clientCapabilities = ClientDefaultCapabilities
        
        # set translation function
        self.translate = self.__identityTranslation
        
        self.codec = QTextCodec.codecForName(
            str(Preferences.getSystem("StringEncoding")))
        
        if passive:
            # set translation function
            if Preferences.getDebugger("PathTranslation"):
                self.translateRemote = Preferences.getDebugger(
                    "PathTranslationRemote")
                self.translateRemoteWindows = "\\" in self.translateRemote
                self.translateLocal = Preferences.getDebugger(
                    "PathTranslationLocal")
                self.translateLocalWindows = "\\" in self.translateLocal
                self.translate = self.__remoteTranslation
            else:
                self.translate = self.__identityTranslation
        
        # attribute to remember the name of the executed script
        self.__scriptName = ""

    def __identityTranslation(self, fn, remote2local=True):
        """
        Private method to perform the identity path translation.
        
        @param fn filename to be translated (string)
        @param remote2local flag indicating the direction of translation
            (False = local to remote, True = remote to local [default])
        @return translated filename (string)
        """
        return fn
        
    def __remoteTranslation(self, fn, remote2local=True):
        """
        Private method to perform the path translation.
        
        @param fn filename to be translated (string)
        @param remote2local flag indicating the direction of translation
            (False = local to remote, True = remote to local [default])
        @return translated filename (string)
        """
        if remote2local:
            path = fn.replace(self.translateRemote, self.translateLocal)
            if self.translateLocalWindows:
                path = path.replace("/", "\\")
        else:
            path = fn.replace(self.translateLocal, self.translateRemote)
            if not self.translateRemoteWindows:
                path = path.replace("\\", "/")
        
        return path
        
    def __startProcess(self, program, arguments, environment=None,
                       workingDir=None):
        """
        Private method to start the debugger client process.
        
        @param program name of the executable to start
        @type str
        @param arguments arguments to be passed to the program
        @type list of str
        @param environment dictionary of environment settings to pass
        @type dict of str
        @param workingDir directory to start the debugger client in
        @type str
        @return the process object
        @rtype QProcess or None
        """
        proc = QProcess()
        if environment is not None:
            env = QProcessEnvironment()
            for key, value in list(environment.items()):
                env.insert(key, value)
            proc.setProcessEnvironment(env)
        args = arguments[:]
        if workingDir:
            proc.setWorkingDirectory(workingDir)
        proc.start(program, args)
        if not proc.waitForStarted(10000):
            proc = None
        
        return proc
        
    def startRemote(self, port, runInConsole, venvName, originalPathString,
                    workingDir=None):
        """
        Public method to start a remote Python interpreter.
        
        @param port port number the debug server is listening on
        @type int
        @param runInConsole flag indicating to start the debugger in a
            console window
        @type bool
        @param venvName name of the virtual environment to be used
        @type str
        @param originalPathString original PATH environment variable
        @type str
        @param workingDir directory to start the debugger client in
        @type str
        @return client process object, a flag to indicate a network connection
            and the name of the interpreter in case of a local execution
        @rtype tuple of (QProcess, bool, str)
        """
        global origPathEnv
        
        if not venvName:
            if self.__variant == "Python2":
                venvName = Preferences.getDebugger("Python2VirtualEnv")
            else:
                venvName = Preferences.getDebugger("Python3VirtualEnv")
        venvManager = e5App().getObject("VirtualEnvManager")
        interpreter = venvManager.getVirtualenvInterpreter(venvName)
        execPath = venvManager.getVirtualenvExecPath(venvName)
        if (interpreter == "" and
                int(self.__variant[-1]) == sys.version_info[0]):
            # use the interpreter used to run eric for identical variants
            interpreter = sys.executable.replace("w.exe", ".exe")
        if interpreter == "":
            E5MessageBox.critical(
                None,
                self.tr("Start Debugger"),
                self.tr(
                    """<p>No suitable {0} environment configured.</p>""")
                .format(self.__variant))
            return None, False, ""
        
        if self.__variant == "Python2":
            debugClientType = Preferences.getDebugger("DebugClientType")
        else:
            debugClientType = Preferences.getDebugger("DebugClientType3")
        if debugClientType == "standard":
            debugClient = os.path.join(getConfig('ericDir'),
                                       "DebugClients", "Python",
                                       "DebugClient.py")
        else:
            if self.__variant == "Python2":
                debugClient = Preferences.getDebugger("DebugClient")
            else:
                debugClient = Preferences.getDebugger("DebugClient3")
            if debugClient == "":
                debugClient = os.path.join(sys.path[0],
                                           "DebugClients", "Python",
                                           "DebugClient.py")
        
        if self.__variant == "Python2":
            redirect = str(Preferences.getDebugger("PythonRedirect"))
            noencoding = (Preferences.getDebugger("PythonNoEncoding") and
                          '--no-encoding' or '')
        else:
            redirect = str(Preferences.getDebugger("Python3Redirect"))
            noencoding = (Preferences.getDebugger("Python3NoEncoding") and
                          '--no-encoding' or '')
        
        if Preferences.getDebugger("RemoteDbgEnabled"):
            ipaddr = self.debugServer.getHostAddress(False)
            rexec = Preferences.getDebugger("RemoteExecution")
            rhost = Preferences.getDebugger("RemoteHost")
            if rhost == "":
                rhost = "localhost"
            if rexec:
                args = Utilities.parseOptionString(rexec) + [
                    rhost, interpreter, debugClient, noencoding, str(port),
                    redirect, ipaddr]
                if Utilities.isWindowsPlatform():
                    if not os.path.splitext(args[0])[1]:
                        for ext in [".exe", ".com", ".cmd", ".bat"]:
                            prog = Utilities.getExecutablePath(args[0] + ext)
                            if prog:
                                args[0] = prog
                                break
                else:
                    args[0] = Utilities.getExecutablePath(args[0])
                process = self.__startProcess(args[0], args[1:],
                                              workingDir=workingDir)
                if process is None:
                    E5MessageBox.critical(
                        None,
                        self.tr("Start Debugger"),
                        self.tr(
                            """<p>The debugger backend could not be"""
                            """ started.</p>"""))
                
                # set translation function
                if Preferences.getDebugger("PathTranslation"):
                    self.translateRemote = Preferences.getDebugger(
                        "PathTranslationRemote")
                    self.translateRemoteWindows = "\\" in self.translateRemote
                    self.translateLocal = Preferences.getDebugger(
                        "PathTranslationLocal")
                    self.translate = self.__remoteTranslation
                    self.translateLocalWindows = "\\" in self.translateLocal
                else:
                    self.translate = self.__identityTranslation
                return process, self.__isNetworked, ""
        
        # set translation function
        self.translate = self.__identityTranslation
        
        # setup the environment for the debugger
        if Preferences.getDebugger("DebugEnvironmentReplace"):
            clientEnv = {}
        else:
            clientEnv = os.environ.copy()
            if originalPathString:
                clientEnv["PATH"] = originalPathString
        envlist = Utilities.parseEnvironmentString(
            Preferences.getDebugger("DebugEnvironment"))
        for el in envlist:
            try:
                key, value = el.split('=', 1)
                if value.startswith('"') or value.startswith("'"):
                    value = value[1:-1]
                clientEnv[str(key)] = str(value)
            except ValueError:
                pass
        if execPath:
            if "PATH" in clientEnv:
                clientEnv["PATH"] = os.pathsep.join(
                    [execPath, clientEnv["PATH"]])
            else:
                clientEnv["PATH"] = execPath
        
        ipaddr = self.debugServer.getHostAddress(True)
        if runInConsole or Preferences.getDebugger("ConsoleDbgEnabled"):
            ccmd = Preferences.getDebugger("ConsoleDbgCommand")
            if ccmd:
                args = Utilities.parseOptionString(ccmd) + [
                    interpreter, os.path.abspath(debugClient), noencoding,
                    str(port), '0', ipaddr]
                args[0] = Utilities.getExecutablePath(args[0])
                process = self.__startProcess(args[0], args[1:], clientEnv,
                                              workingDir=workingDir)
                if process is None:
                    E5MessageBox.critical(
                        None,
                        self.tr("Start Debugger"),
                        self.tr(
                            """<p>The debugger backend could not be"""
                            """ started.</p>"""))
                return process, self.__isNetworked, interpreter
        
        process = self.__startProcess(
            interpreter,
            [debugClient, noencoding, str(port), redirect, ipaddr],
            clientEnv,
            workingDir=workingDir)
        if process is None:
            self.__startedVenv = ""
            E5MessageBox.critical(
                None,
                self.tr("Start Debugger"),
                self.tr(
                    """<p>The debugger backend could not be started.</p>"""))
        else:
            self.__startedVenv = venvName
        
        return process, self.__isNetworked, interpreter

    def startRemoteForProject(self, port, runInConsole, venvName,
                              originalPathString, workingDir=None):
        """
        Public method to start a remote Python interpreter for a project.
        
        @param port port number the debug server is listening on
        @type int
        @param runInConsole flag indicating to start the debugger in a
            console window
        @type bool
        @param venvName name of the virtual environment to be used
        @type str
        @param originalPathString original PATH environment variable
        @type str
        @param workingDir directory to start the debugger client in
        @type str
        @return client process object, a flag to indicate a network connection
            and the name of the interpreter in case of a local execution
        @rtype tuple of (QProcess, bool, str)
        """
        global origPathEnv
        
        project = e5App().getObject("Project")
        if not project.isDebugPropertiesLoaded():
            return None, self.__isNetworked, ""
        
        # start debugger with project specific settings
        debugClient = project.getDebugProperty("DEBUGCLIENT")
        if not venvName:
            venvName = project.getDebugProperty("VIRTUALENV")
        if not venvName:
            if project.getProjectLanguage() == "Python2":
                venvName = Preferences.getDebugger("Python2VirtualEnv")
            elif project.getProjectLanguage() == "Python3":
                venvName = Preferences.getDebugger("Python3VirtualEnv")
        
        redirect = str(project.getDebugProperty("REDIRECT"))
        noencoding = (
            project.getDebugProperty("NOENCODING") and '--no-encoding' or '')
        
        venvManager = e5App().getObject("VirtualEnvManager")
        interpreter = venvManager.getVirtualenvInterpreter(venvName)
        execPath = venvManager.getVirtualenvExecPath(venvName)
        if (interpreter == "" and
            project.getProjectLanguage().startswith("Python") and
                sys.version_info[0] == int(project.getProjectLanguage()[-1])):
            interpreter = sys.executable.replace("w.exe", ".exe")
        if interpreter == "":
            E5MessageBox.critical(
                None,
                self.tr("Start Debugger"),
                self.tr(
                    """<p>No suitable {0} environment configured.</p>""")
                .format(self.__variant))
            return None, self.__isNetworked, ""
        
        if project.getDebugProperty("REMOTEDEBUGGER"):
            ipaddr = self.debugServer.getHostAddress(False)
            rexec = project.getDebugProperty("REMOTECOMMAND")
            rhost = project.getDebugProperty("REMOTEHOST")
            if rhost == "":
                rhost = "localhost"
            if rexec:
                args = Utilities.parseOptionString(rexec) + [
                    rhost, interpreter, debugClient, noencoding, str(port),
                    redirect, ipaddr]
                if Utilities.isWindowsPlatform():
                    if not os.path.splitext(args[0])[1]:
                        for ext in [".exe", ".com", ".cmd", ".bat"]:
                            prog = Utilities.getExecutablePath(args[0] + ext)
                            if prog:
                                args[0] = prog
                                break
                else:
                    args[0] = Utilities.getExecutablePath(args[0])
                process = self.__startProcess(args[0], args[1:],
                                              workingDir=workingDir)
                if process is None:
                    E5MessageBox.critical(
                        None,
                        self.tr("Start Debugger"),
                        self.tr(
                            """<p>The debugger backend could not be"""
                            """ started.</p>"""))
                # set translation function
                if project.getDebugProperty("PATHTRANSLATION"):
                    self.translateRemote = project.getDebugProperty(
                        "REMOTEPATH")
                    self.translateRemoteWindows = "\\" in self.translateRemote
                    self.translateLocal = project.getDebugProperty("LOCALPATH")
                    self.translateLocalWindows = "\\" in self.translateLocal
                    self.translate = self.__remoteTranslation
                else:
                    self.translate = self.__identityTranslation
                return process, self.__isNetworked, ""
            else:
                # remote shell command is missing
                return None, self.__isNetworked, ""
    
        # set translation function
        self.translate = self.__identityTranslation
        
        # setup the environment for the debugger
        if project.getDebugProperty("ENVIRONMENTOVERRIDE"):
            clientEnv = {}
        else:
            clientEnv = os.environ.copy()
            if originalPathString:
                clientEnv["PATH"] = originalPathString
        envlist = Utilities.parseEnvironmentString(
            project.getDebugProperty("ENVIRONMENTSTRING"))
        for el in envlist:
            try:
                key, value = el.split('=', 1)
                if value.startswith('"') or value.startswith("'"):
                    value = value[1:-1]
                clientEnv[str(key)] = str(value)
            except ValueError:
                pass
        if execPath:
            if "PATH" in clientEnv:
                clientEnv["PATH"] = os.pathsep.join(
                    [execPath, clientEnv["PATH"]])
            else:
                clientEnv["PATH"] = execPath
        
        ipaddr = self.debugServer.getHostAddress(True)
        if runInConsole or project.getDebugProperty("CONSOLEDEBUGGER"):
            ccmd = (project.getDebugProperty("CONSOLECOMMAND") or
                    Preferences.getDebugger("ConsoleDbgCommand"))
            if ccmd:
                args = Utilities.parseOptionString(ccmd) + [
                    interpreter, os.path.abspath(debugClient), noencoding,
                    str(port), '0', ipaddr]
                args[0] = Utilities.getExecutablePath(args[0])
                process = self.__startProcess(args[0], args[1:], clientEnv,
                                              workingDir=workingDir)
                if process is None:
                    E5MessageBox.critical(
                        None,
                        self.tr("Start Debugger"),
                        self.tr(
                            """<p>The debugger backend could not be"""
                            """ started.</p>"""))
                return process, self.__isNetworked, interpreter
        
        process = self.__startProcess(
            interpreter,
            [debugClient, noencoding, str(port), redirect, ipaddr],
            clientEnv,
            workingDir=workingDir)
        if process is None:
            self.__startedVenv = ""
            E5MessageBox.critical(
                None,
                self.tr("Start Debugger"),
                self.tr(
                    """<p>The debugger backend could not be started.</p>"""))
        else:
            self.__startedVenv = venvName
        
        return process, self.__isNetworked, interpreter

    def getClientCapabilities(self):
        """
        Public method to retrieve the debug clients capabilities.
        
        @return debug client capabilities (integer)
        """
        return self.clientCapabilities
    
    def newConnection(self, sock):
        """
        Public slot to handle a new connection.
        
        @param sock reference to the socket object (QTcpSocket)
        @return flag indicating success (boolean)
        """
        # If we already have a connection, refuse this one.  It will be closed
        # automatically.
        if self.qsock is not None:
            return False
        
        sock.disconnected.connect(self.debugServer.startClient)
        sock.readyRead.connect(self.__parseClientLine)
        
        self.qsock = sock
        
        # Get the remote clients capabilities
        self.remoteCapabilities()
        return True
    
    def flush(self):
        """
        Public slot to flush the queue.
        """
        if self.qsock is not None:
            # Send commands that were waiting for the connection.
            for cmd in self.queue:
                self.__writeJsonCommandToSocket(cmd)
            
            self.queue = []
    
    def shutdown(self):
        """
        Public method to cleanly shut down.
        
        It closes our socket and shuts down
        the debug client. (Needed on Win OS)
        """
        if self.qsock is None:
            return
        
        # do not want any slots called during shutdown
        self.qsock.disconnected.disconnect(self.debugServer.startClient)
        self.qsock.readyRead.disconnect(self.__parseClientLine)
        
        # close down socket, and shut down client as well.
        self.__sendJsonCommand("RequestShutdown", {})
        self.qsock.flush()
        self.qsock.close()
        
        # reinitialize
        self.qsock = None
        self.queue = []
    
    def isConnected(self):
        """
        Public method to test, if a debug client has connected.
        
        @return flag indicating the connection status (boolean)
        """
        return self.qsock is not None
    
    def remoteEnvironment(self, env):
        """
        Public method to set the environment for a program to debug, run, ...
        
        @param env environment settings (dictionary)
        """
        self.__sendJsonCommand("RequestEnvironment", {"environment": env})
    
    def remoteLoad(self, fn, argv, wd, traceInterpreter=False,
                   autoContinue=True, autoFork=False, forkChild=False):
        """
        Public method to load a new program to debug.
        
        @param fn the filename to debug (string)
        @param argv the commandline arguments to pass to the program (string)
        @param wd the working directory for the program (string)
        @keyparam traceInterpreter flag indicating if the interpreter library
            should be traced as well (boolean)
        @keyparam autoContinue flag indicating, that the debugger should not
            stop at the first executable line (boolean)
        @keyparam autoFork flag indicating the automatic fork mode (boolean)
        @keyparam forkChild flag indicating to debug the child after forking
            (boolean)
        """
        self.__autoContinue = autoContinue
        self.__scriptName = os.path.abspath(fn)
        
        wd = self.translate(wd, False)
        fn = self.translate(os.path.abspath(fn), False)
        self.__sendJsonCommand("RequestLoad", {
            "workdir": wd,
            "filename": fn,
            "argv": Utilities.parseOptionString(argv),
            "traceInterpreter": traceInterpreter,
            "autofork": autoFork,
            "forkChild": forkChild,
        })
    
    def remoteRun(self, fn, argv, wd, autoFork=False, forkChild=False):
        """
        Public method to load a new program to run.
        
        @param fn the filename to run (string)
        @param argv the commandline arguments to pass to the program (string)
        @param wd the working directory for the program (string)
        @keyparam autoFork flag indicating the automatic fork mode (boolean)
        @keyparam forkChild flag indicating to debug the child after forking
            (boolean)
        """
        self.__scriptName = os.path.abspath(fn)
        
        wd = self.translate(wd, False)
        fn = self.translate(os.path.abspath(fn), False)
        self.__sendJsonCommand("RequestRun", {
            "workdir": wd,
            "filename": fn,
            "argv": Utilities.parseOptionString(argv),
            "autofork": autoFork,
            "forkChild": forkChild,
        })
    
    def remoteCoverage(self, fn, argv, wd, erase=False):
        """
        Public method to load a new program to collect coverage data.
        
        @param fn the filename to run (string)
        @param argv the commandline arguments to pass to the program (string)
        @param wd the working directory for the program (string)
        @keyparam erase flag indicating that coverage info should be
            cleared first (boolean)
        """
        self.__scriptName = os.path.abspath(fn)
        
        wd = self.translate(wd, False)
        fn = self.translate(os.path.abspath(fn), False)
        self.__sendJsonCommand("RequestCoverage", {
            "workdir": wd,
            "filename": fn,
            "argv": Utilities.parseOptionString(argv),
            "erase": erase,
        })

    def remoteProfile(self, fn, argv, wd, erase=False):
        """
        Public method to load a new program to collect profiling data.
        
        @param fn the filename to run (string)
        @param argv the commandline arguments to pass to the program (string)
        @param wd the working directory for the program (string)
        @keyparam erase flag indicating that timing info should be cleared
            first (boolean)
        """
        self.__scriptName = os.path.abspath(fn)
        
        wd = self.translate(wd, False)
        fn = self.translate(os.path.abspath(fn), False)
        self.__sendJsonCommand("RequestProfile", {
            "workdir": wd,
            "filename": fn,
            "argv": Utilities.parseOptionString(argv),
            "erase": erase,
        })

    def remoteStatement(self, stmt):
        """
        Public method to execute a Python statement.
        
        @param stmt the Python statement to execute (string). It
              should not have a trailing newline.
        """
        self.__sendJsonCommand("ExecuteStatement", {
            "statement": stmt,
        })

    def remoteStep(self):
        """
        Public method to single step the debugged program.
        """
        self.__sendJsonCommand("RequestStep", {})

    def remoteStepOver(self):
        """
        Public method to step over the debugged program.
        """
        self.__sendJsonCommand("RequestStepOver", {})

    def remoteStepOut(self):
        """
        Public method to step out the debugged program.
        """
        self.__sendJsonCommand("RequestStepOut", {})

    def remoteStepQuit(self):
        """
        Public method to stop the debugged program.
        """
        self.__sendJsonCommand("RequestStepQuit", {})

    def remoteContinue(self, special=False):
        """
        Public method to continue the debugged program.
        
        @param special flag indicating a special continue operation
        """
        self.__sendJsonCommand("RequestContinue", {
            "special": special,
        })

    def remoteMoveIP(self, line):
        """
        Public method to move the instruction pointer to a different line.
        
        @param line the new line, where execution should be continued
        """
        self.__sendJsonCommand("RequestMoveIP", {
            "newLine": line,
        })

    def remoteBreakpoint(self, fn, line, setBreakpoint, cond=None, temp=False):
        """
        Public method to set or clear a breakpoint.
        
        @param fn filename the breakpoint belongs to (string)
        @param line linenumber of the breakpoint (int)
        @param setBreakpoint flag indicating setting or resetting a
            breakpoint (boolean)
        @param cond condition of the breakpoint (string)
        @param temp flag indicating a temporary breakpoint (boolean)
        """
        self.__sendJsonCommand("RequestBreakpoint", {
            "filename": self.translate(fn, False),
            "line": line,
            "temporary": temp,
            "setBreakpoint": setBreakpoint,
            "condition": cond,
        })
    
    def remoteBreakpointEnable(self, fn, line, enable):
        """
        Public method to enable or disable a breakpoint.
        
        @param fn filename the breakpoint belongs to (string)
        @param line linenumber of the breakpoint (int)
        @param enable flag indicating enabling or disabling a breakpoint
            (boolean)
        """
        self.__sendJsonCommand("RequestBreakpointEnable", {
            "filename": self.translate(fn, False),
            "line": line,
            "enable": enable,
        })
    
    def remoteBreakpointIgnore(self, fn, line, count):
        """
        Public method to ignore a breakpoint the next couple of occurrences.
        
        @param fn filename the breakpoint belongs to (string)
        @param line linenumber of the breakpoint (int)
        @param count number of occurrences to ignore (int)
        """
        self.__sendJsonCommand("RequestBreakpointIgnore", {
            "filename": self.translate(fn, False),
            "line": line,
            "count": count,
        })
    
    def remoteWatchpoint(self, cond, setWatch, temp=False):
        """
        Public method to set or clear a watch expression.
        
        @param cond expression of the watch expression (string)
        @param setWatch flag indicating setting or resetting a watch expression
            (boolean)
        @param temp flag indicating a temporary watch expression (boolean)
        """
        # cond is combination of cond and special (s. watch expression viewer)
        self.__sendJsonCommand("RequestWatch", {
            "temporary": temp,
            "setWatch": setWatch,
            "condition": cond,
        })
    
    def remoteWatchpointEnable(self, cond, enable):
        """
        Public method to enable or disable a watch expression.
        
        @param cond expression of the watch expression (string)
        @param enable flag indicating enabling or disabling a watch expression
            (boolean)
        """
        # cond is combination of cond and special (s. watch expression viewer)
        self.__sendJsonCommand("RequestWatchEnable", {
            "condition": cond,
            "enable": enable,
        })
    
    def remoteWatchpointIgnore(self, cond, count):
        """
        Public method to ignore a watch expression the next couple of
        occurrences.
        
        @param cond expression of the watch expression (string)
        @param count number of occurrences to ignore (int)
        """
        # cond is combination of cond and special (s. watch expression viewer)
        self.__sendJsonCommand("RequestWatchIgnore", {
            "condition": cond,
            "count": count,
        })
    
    def remoteRawInput(self, s):
        """
        Public method to send the raw input to the debugged program.
        
        @param s the raw input (string)
        """
        self.__sendJsonCommand("RawInput", {
            "input": s,
        })
    
    def remoteThreadList(self):
        """
        Public method to request the list of threads from the client.
        """
        self.__sendJsonCommand("RequestThreadList", {})
        
    def remoteSetThread(self, tid):
        """
        Public method to request to set the given thread as current thread.
        
        @param tid id of the thread (integer)
        """
        self.__sendJsonCommand("RequestThreadSet", {
            "threadID": tid,
        })
        
    def remoteClientVariables(self, scope, filterList, framenr=0, maxSize=0):
        """
        Public method to request the variables of the debugged program.
        
        @param scope the scope of the variables (0 = local, 1 = global)
        @type int
        @param filterList list of variable types to filter out
        @type list of int
        @param framenr framenumber of the variables to retrieve
        @type int
        @param maxSize maximum size the formatted value of a variable will
            be shown. If it is bigger than that, a 'too big' indication will
            be given (@@TOO_BIG_TO_SHOW@@).
        @type int
        """
        self.__sendJsonCommand("RequestVariables", {
            "frameNumber": framenr,
            "scope": scope,
            "filters": filterList,
            "maxSize": maxSize,
        })
    
    def remoteClientVariable(self, scope, filterList, var, framenr=0,
                             maxSize=0):
        """
        Public method to request the variables of the debugged program.
        
        @param scope the scope of the variables (0 = local, 1 = global)
        @type int
        @param filterList list of variable types to filter out
        @type list of int
        @param var list encoded name of variable to retrieve
        @type list of str
        @param framenr framenumber of the variables to retrieve
        @type int
        @param maxSize maximum size the formatted value of a variable will
            be shown. If it is bigger than that, a 'too big' indication will
            be given (@@TOO_BIG_TO_SHOW@@).
        @type int
        """
        self.__sendJsonCommand("RequestVariable", {
            "variable": var,
            "frameNumber": framenr,
            "scope": scope,
            "filters": filterList,
            "maxSize": maxSize,
        })
    
    def remoteClientSetFilter(self, scope, filterStr):
        """
        Public method to set a variables filter list.
        
        @param scope the scope of the variables (0 = local, 1 = global)
        @param filterStr regexp string for variable names to filter out
            (string)
        """
        self.__sendJsonCommand("RequestSetFilter", {
            "scope": scope,
            "filter": filterStr,
        })
    
    def setCallTraceEnabled(self, on):
        """
        Public method to set the call trace state.
        
        @param on flag indicating to enable the call trace function (boolean)
        """
        self.__sendJsonCommand("RequestCallTrace", {
            "enable": on,
        })
    
    def remoteBanner(self):
        """
        Public slot to get the banner info of the remote client.
        """
        self.__sendJsonCommand("RequestBanner", {})
    
    def remoteCapabilities(self):
        """
        Public slot to get the debug clients capabilities.
        """
        self.__sendJsonCommand("RequestCapabilities", {})
    
    def remoteCompletion(self, text):
        """
        Public slot to get the a list of possible commandline completions
        from the remote client.
        
        @param text the text to be completed (string)
        """
        self.__sendJsonCommand("RequestCompletion", {
            "text": text,
        })
    
    def remoteUTDiscover(self, syspath, workdir, discoveryStart):
        """
        Public method to perform a test case discovery.
        
        @param syspath list of directories to be added to sys.path on the
            remote side
        @type list of str
        @param workdir path name of the working directory
        @type str
        @param discoveryStart directory to start auto-discovery at
        @type str
        """
        self.__sendJsonCommand("RequestUTDiscover", {
            "syspath": [] if syspath is None else syspath,
            "workdir": workdir,
            "discoverystart": discoveryStart,
        })
    
    def remoteUTPrepare(self, fn, tn, tfn, failed, cov, covname, coverase,
                        syspath, workdir, discover, discoveryStart, testCases,
                        debug):
        """
        Public method to prepare a new unittest run.
        
        @param fn name of file to load
        @type str
        @param tn name of test to load
        @type str
        @param tfn test function name to load tests from
        @type str
        @param failed list of failed test, if only failed test should be run
        @type list of str
        @param cov flag indicating collection of coverage data is requested
        @type bool
        @param covname name of file to be used to assemble the coverage caches
            filename
        @type str
        @param coverase flag indicating erasure of coverage data is requested
        @type bool
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
        if fn:
            self.__scriptName = os.path.abspath(fn)
            
            fn = self.translate(os.path.abspath(fn), False)
        else:
            self.__scriptName = "unittest discover"
        
        self.__sendJsonCommand("RequestUTPrepare", {
            "filename": fn,
            "testname": tn,
            "testfunctionname": tfn,
            "failed": failed,
            "coverage": cov,
            "coveragefile": covname,
            "coverageerase": coverase,
            "syspath": [] if syspath is None else syspath,
            "workdir": workdir,
            "discover": discover,
            "discoverystart": discoveryStart,
            "testcases": [] if testCases is None else testCases,
            "debug": debug,
        })
    
    def remoteUTRun(self, debug, failfast):
        """
        Public method to start a unittest run.
        
        @param debug flag indicating to run unittest with debugging
        @type bool
        @param failfast flag indicating to stop at the first error
        @type bool
        """
        if debug:
            self.__autoContinue = True
        self.__sendJsonCommand("RequestUTRun", {
            "debug": debug,
            "failfast": failfast,
        })
    
    def remoteUTStop(self):
        """
        Public method to stop a unittest run.
        """
        self.__sendJsonCommand("RequestUTStop", {})
    
    def __askForkTo(self):
        """
        Private method to ask the user which branch of a fork to follow.
        """
        selections = [self.tr("Parent Process"),
                      self.tr("Child process")]
        res, ok = QInputDialog.getItem(
            None,
            self.tr("Client forking"),
            self.tr("Select the fork branch to follow."),
            selections,
            0, False)
        if not ok or res == selections[0]:
            self.__sendJsonCommand("ResponseForkTo", {
                "target": "parent",
            })
        else:
            self.__sendJsonCommand("ResponseForkTo", {
                "target": "child",
            })
    
    def __parseClientLine(self):
        """
        Private method to handle data from the client.
        """
        while self.qsock and self.qsock.canReadLine():
            qs = self.qsock.readLine()
            if self.codec is not None:
                line = self.codec.toUnicode(qs)
            else:
                line = bytes(qs).decode()
            
            logging.debug("<Debug-Server> %s", line)
##            print("Server: ", line)          ##debug
            
            self.__handleJsonCommand(line)
            continue
    
    def __handleJsonCommand(self, jsonStr):
        """
        Private method to handle a command or response serialized as a
        JSON string.
        
        @param jsonStr string containing the command or response received
            from the debug backend
        @type str
        """
        import json
        
        try:
            commandDict = json.loads(jsonStr.strip())
        except (TypeError, ValueError) as err:
            E5MessageBox.critical(
                None,
                self.tr("Debug Protocol Error"),
                self.tr("""<p>The response received from the debugger"""
                        """ backend could not be decoded. Please report"""
                        """ this issue with the received data to the"""
                        """ eric bugs email address.</p>"""
                        """<p>Error: {0}</p>"""
                        """<p>Data:<br/>{1}</p>""").format(
                    str(err), Utilities.html_encode(jsonStr.strip())),
                E5MessageBox.StandardButtons(
                    E5MessageBox.Ok))
            return
        
        method = commandDict["method"]
        params = commandDict["params"]
        
        if method == "ClientOutput":
            self.debugServer.signalClientOutput(params["text"])
        
        elif method in ["ResponseLine", "ResponseStack"]:
            # Check if obsolet thread was clicked
            if params["stack"] == []:
                # Request updated list
                self.remoteThreadList()
                return
            for s in params["stack"]:
                s[0] = self.translate(s[0], True)
            cf = params["stack"][0]
            if self.__autoContinue:
                self.__autoContinue = False
                QTimer.singleShot(0, self.remoteContinue)
            else:
                self.debugServer.signalClientLine(
                    cf[0], int(cf[1]),
                    method == "ResponseStack")
                self.debugServer.signalClientStack(params["stack"])
        
        elif method == "CallTrace":
            isCall = params["event"].lower() == "c"
            fromInfo = params["from"]
            toInfo = params["to"]
            self.debugServer.signalClientCallTrace(
                isCall,
                fromInfo["filename"], str(fromInfo["linenumber"]),
                fromInfo["codename"],
                toInfo["filename"], str(toInfo["linenumber"]),
                toInfo["codename"])
        
        elif method == "ResponseVariables":
            self.debugServer.signalClientVariables(
                params["scope"], params["variables"])
        
        elif method == "ResponseVariable":
            self.debugServer.signalClientVariable(
                params["scope"], [params["variable"]] + params["variables"])
        
        elif method == "ResponseThreadList":
            self.debugServer.signalClientThreadList(
                params["currentID"], params["threadList"])
        
        elif method == "ResponseThreadSet":
            self.debugServer.signalClientThreadSet()
        
        elif method == "ResponseCapabilities":
            self.clientCapabilities = params["capabilities"]
            self.debugServer.signalClientCapabilities(
                params["capabilities"],
                params["clientType"],
                self.__startedVenv,
            )
        
        elif method == "ResponseBanner":
            self.debugServer.signalClientBanner(
                params["version"],
                params["platform"],
                params["dbgclient"],
                self.__startedVenv,
            )
        
        elif method == "ResponseOK":
            self.debugServer.signalClientStatement(False)
        
        elif method == "ResponseContinue":
            self.debugServer.signalClientStatement(True)
        
        elif method == "RequestRaw":
            self.debugServer.signalClientRawInput(
                params["prompt"], params["echo"])
        
        elif method == "ResponseBPConditionError":
            fn = self.translate(params["filename"], True)
            self.debugServer.signalClientBreakConditionError(
                fn, params["line"])
        
        elif method == "ResponseClearBreakpoint":
            fn = self.translate(params["filename"], True)
            self.debugServer.signalClientClearBreak(fn, params["line"])
        
        elif method == "ResponseWatchConditionError":
            self.debugServer.signalClientWatchConditionError(
                params["condition"])
        
        elif method == "ResponseClearWatch":
            self.debugServer.signalClientClearWatch(params["condition"])
        
        elif method == "ResponseException":
            if params:
                exctype = params["type"]
                excmessage = params["message"]
                stack = params["stack"]
                if stack:
                    for stackEntry in stack:
                        stackEntry[0] = self.translate(stackEntry[0], True)
                    if stack[0] and stack[0][0] == "<string>":
                        for stackEntry in stack:
                            if stackEntry[0] == "<string>":
                                stackEntry[0] = self.__scriptName
                            else:
                                break
            else:
                exctype = ''
                excmessage = ''
                stack = []
            
            self.debugServer.signalClientException(
                exctype, excmessage, stack)
        
        elif method == "ResponseSyntax":
            self.debugServer.signalClientSyntaxError(
                params["message"], self.translate(params["filename"], True),
                params["linenumber"], params["characternumber"])
        
        elif method == "ResponseSignal":
            self.debugServer.signalClientSignal(
                params["message"], self.translate(params["filename"], True),
                params["linenumber"], params["function"], params["arguments"])
        
        elif method == "ResponseExit":
            self.__scriptName = ""
            self.debugServer.signalClientExit(
                params["status"], params["message"])
        
        elif method == "PassiveStartup":
            self.debugServer.passiveStartUp(
                self.translate(params["filename"], True), params["exceptions"])
        
        elif method == "ResponseCompletion":
            self.debugServer.signalClientCompletionList(
                params["completions"], params["text"])
        
        elif method == "ResponseUTDiscover":
            self.debugServer.clientUtDiscovered(
                params["testCasesList"], params["exception"],
                params["message"])
        
        elif method == "ResponseUTPrepared":
            self.debugServer.clientUtPrepared(
                params["count"], params["exception"], params["message"])
        
        elif method == "ResponseUTFinished":
            self.debugServer.clientUtFinished(params["status"])
        
        elif method == "ResponseUTStartTest":
            self.debugServer.clientUtStartTest(
                params["testname"], params["description"])
        
        elif method == "ResponseUTStopTest":
            self.debugServer.clientUtStopTest()
        
        elif method == "ResponseUTTestFailed":
            self.debugServer.clientUtTestFailed(
                params["testname"], params["traceback"], params["id"])
        
        elif method == "ResponseUTTestErrored":
            self.debugServer.clientUtTestErrored(
                params["testname"], params["traceback"], params["id"])
        
        elif method == "ResponseUTTestSkipped":
            self.debugServer.clientUtTestSkipped(
                params["testname"], params["reason"], params["id"])
        
        elif method == "ResponseUTTestFailedExpected":
            self.debugServer.clientUtTestFailedExpected(
                params["testname"], params["traceback"], params["id"])
        
        elif method == "ResponseUTTestSucceededUnexpected":
            self.debugServer.clientUtTestSucceededUnexpected(
                params["testname"], params["id"])
        
        elif method == "RequestForkTo":
            self.__askForkTo()
    
    def __sendJsonCommand(self, command, params):
        """
        Private method to send a single command to the client.
        
        @param command command name to be sent
        @type str
        @param params dictionary of named parameters for the command
        @type dict
        """
        import json
        
        commandDict = {
            "jsonrpc": "2.0",
            "method": command,
            "params": params,
        }
        cmd = json.dumps(commandDict) + '\n'
        if self.qsock is not None:
            self.__writeJsonCommandToSocket(cmd)
        else:
            self.queue.append(cmd)
    
    def __writeJsonCommandToSocket(self, cmd):
        """
        Private method to write a JSON command to the socket.
        
        @param cmd JSON command to be sent
        @type str
        """
        data = cmd.encode('utf8', 'backslashreplace')
        length = "{0:09d}".format(len(data))
        self.qsock.write(length.encode() + data)
        self.qsock.flush()


def createDebuggerInterfacePython2(debugServer, passive):
    """
    Module function to create a debugger interface instance.
    
        
    @param debugServer reference to the debug server
    @type DebugServer
    @param passive flag indicating passive connection mode
    @type bool
    @return instantiated debugger interface
    @rtype DebuggerInterfacePython
    """
    return DebuggerInterfacePython(debugServer, passive, "Python2")
    

def createDebuggerInterfacePython3(debugServer, passive):
    """
    Module function to create a debugger interface instance.
    
        
    @param debugServer reference to the debug server
    @type DebugServer
    @param passive flag indicating passive connection mode
    @type bool
    @return instantiated debugger interface
    @rtype DebuggerInterfacePython
    """
    return DebuggerInterfacePython(debugServer, passive, "Python3")


def getRegistryData():
    """
    Module function to get characterizing data for the supported debugger
    interfaces.
    
    @return list of tuples containing the client type, the client capabilities,
        the client file type associations and a reference to the creation
        function
    @rtype list of tuple of (str, int, list of str, function)
    """
    py2Exts = []
    for ext in Preferences.getDebugger("PythonExtensions").split():
        if ext.startswith("."):
            py2Exts.append(ext)
        else:
            py2Exts.append(".{0}".format(ext))
    
    py3Exts = []
    for ext in Preferences.getDebugger("Python3Extensions").split():
        if ext.startswith("."):
            py3Exts.append(ext)
        else:
            py3Exts.append(".{0}".format(ext))
    
    registryData = []
    if py2Exts and (Preferences.getDebugger("Python2VirtualEnv") or
                    sys.version_info[0] == 2):
        registryData.append(
            ("Python2", ClientDefaultCapabilities, py2Exts,
             createDebuggerInterfacePython2)
        )
    
    if py3Exts and (Preferences.getDebugger("Python3VirtualEnv") or
                    sys.version_info[0] >= 3):
        registryData.append(
            ("Python3", ClientDefaultCapabilities, py3Exts,
                createDebuggerInterfacePython3)
        )
    
    return registryData
