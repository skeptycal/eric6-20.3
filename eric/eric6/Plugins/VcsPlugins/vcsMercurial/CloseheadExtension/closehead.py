# -*- coding: utf-8 -*-

# Copyright (c) 2019 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the closehead extension interface.
"""


import os

from PyQt5.QtWidgets import QDialog

from ..HgExtension import HgExtension
from ..HgDialog import HgDialog


class Closehead(HgExtension):
    """
    Class implementing the strip extension interface.
    """
    def __init__(self, vcs):
        """
        Constructor
        
        @param vcs reference to the Mercurial vcs object
        @type Hg
        """
        super(Closehead, self).__init__(vcs)
    
    def hgCloseheads(self, name, revisions=None):
        """
        Public method to close arbitrary heads.
        
        @param name file/directory name
        @type str
        @param revisions revisions of branch heads to be closed
        @type str
        """
        # find the root of the repo
        repodir = self.vcs.splitPath(name)[0]
        while not os.path.isdir(os.path.join(repodir, self.vcs.adminDir)):
            repodir = os.path.dirname(repodir)
            if os.path.splitdrive(repodir)[1] == os.sep:
                return
        
        message = ""
        if not revisions:
            from .HgCloseHeadSelectionDialog import HgCloseHeadSelectionDialog
            dlg = HgCloseHeadSelectionDialog(self.vcs, name)
            if dlg.exec_() == QDialog.Accepted:
                revisions, message = dlg.getData()
        
        if not revisions:
            # still no revisions given; abort...
            return
        
        args = self.vcs.initCommand("close-head")
        if not message:
            if len(revisions) == 1:
                message = self.tr("Revision <{0}> closed.").format(
                    revisions[0])
            else:
                message = self.tr("Revisions <{0}> closed.").format(
                    ", ".join(revisions))
        args += ["--message", message]
        for revision in revisions:
            args += ["--rev", revision]
        
        dia = HgDialog(self.tr("Closing Heads"), self.vcs)
        res = dia.startProcess(args, repodir)
        if res:
            dia.exec_()
