# -*- coding: utf-8 -*-

# Copyright (c) 2010 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#


"""
Module implementing a class for reading a highlighting styles XML file.
"""


from PyQt5.QtGui import QColor, QFont

from .Config import highlightingStylesFileFormatVersion
from .XMLStreamReaderBase import XMLStreamReaderBase


class HighlightingStylesReader(XMLStreamReaderBase):
    """
    Class for reading a highlighting styles XML file.
    """
    supportedVersions = ["4.3", "6.0"]
    
    def __init__(self, device, lexers):
        """
        Constructor
        
        @param device reference to the I/O device to read from (QIODevice)
        @param lexers list of lexer objects for which to export the styles
        """
        XMLStreamReaderBase.__init__(self, device)
        
        self.lexers = lexers
        
        self.version = ""
    
    def readXML(self):
        """
        Public method to read and parse the XML document.
        """
        while not self.atEnd():
            self.readNext()
            if self.isStartElement():
                if self.name() == "HighlightingStyles":
                    self.version = self.attribute(
                        "version",
                        highlightingStylesFileFormatVersion)
                    if self.version not in self.supportedVersions:
                        self.raiseUnsupportedFormatVersion(self.version)
                elif self.name() == "Lexer":
                    self.__readLexer()
                else:
                    self.raiseUnexpectedStartTag(self.name())
        
        self.showErrorMessage()
    
    def __readLexer(self):
        """
        Private method to read the lexer info.
        """
        language = self.attribute("name")
        if language and language in self.lexers:
            lexer = self.lexers[language]
        else:
            lexer = None
        
        while not self.atEnd():
            self.readNext()
            if self.isEndElement() and self.name() == "Lexer":
                break
            
            if self.isStartElement():
                if self.name() == "Style":
                    self.__readStyle(lexer)
                else:
                    self.raiseUnexpectedStartTag(self.name())
    
    def __readStyle(self, lexer):
        """
        Private method to read the style info.
        
        @param lexer reference to the lexer object
        """
        if lexer is not None:
            style = self.attribute("style")
            if style:
                style = int(style)
                substyle = int(self.attribute("substyle", "-1"))
                # -1 is default for base styles
                
                # add sub-style if not already there
                if not lexer.hasStyle(style, substyle):
                    substyle = lexer.addSubstyle(style)
                
                color = self.attribute("color")
                if color:
                    color = QColor(color)
                else:
                    color = lexer.defaultColor(style, substyle)
                lexer.setColor(color, style, substyle)
                
                paper = self.attribute("paper")
                if paper:
                    paper = QColor(paper)
                else:
                    paper = lexer.defaultPaper(style, substyle)
                lexer.setPaper(paper, style, substyle)
                
                fontStr = self.attribute("font")
                if fontStr:
                    font = QFont()
                    font.fromString(fontStr)
                else:
                    font = lexer.defaultFont(style, substyle)
                lexer.setFont(font, style, substyle)
                
                eolfill = self.attribute("eolfill")
                if eolfill:
                    eolfill = self.toBool(eolfill)
                    if eolfill is None:
                        eolfill = lexer.defaulEolFill(style, substyle)
                else:
                    eolfill = lexer.defaulEolFill(style, substyle)
                lexer.setEolFill(eolfill, style, substyle)
        
                while not self.atEnd():
                    self.readNext()
                    if self.isStartElement():
                        if self.name() == "Description" and substyle >= 0:
                            # description can only be set for sub-styles
                            description = self.readElementText().strip()
                            if not description:
                                description = lexer.defaultDescription(
                                    style, substyle)
                            lexer.setDescription(description, style, substyle)
                        elif self.name() == "Words" and substyle >= 0:
                            # words can only be set for sub-styles
                            words = self.readElementText().strip()
                            if not words:
                                words = lexer.defaultWords(style, substyle)
                            lexer.setWords(words, style, substyle)
                    
                    if self.isEndElement() and self.name() == "Style":
                        return
        
        while not self.atEnd():
            self.readNext()
            if self.isEndElement() and self.name() == "Style":
                break
