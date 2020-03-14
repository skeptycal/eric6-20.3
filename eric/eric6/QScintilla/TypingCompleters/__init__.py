# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Package implementing lexers for the various supported programming languages.
"""


def getCompleter(language, editor, parent=None):
    """
    Module function to instantiate a lexer object for a given language.
    
    @param language language of the lexer (string)
    @param editor reference to the editor object (QScintilla.Editor)
    @param parent reference to the parent object (QObject)
    @return reference to the instanciated lexer object (QsciLexer)
    """
    try:
        if language in ["Python", "Python2", "Python3", "MicroPython"]:
            from .CompleterPython import CompleterPython
            return CompleterPython(editor, parent)
        elif language == "Ruby":
            from .CompleterRuby import CompleterRuby
            return CompleterRuby(editor, parent)
        elif language == "YAML":
            from .CompleterYaml import CompleterYaml
            return CompleterYaml(editor, parent)
        else:
            return None
    except ImportError:
        return None
