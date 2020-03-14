# -*- coding: utf-8 -*-

# Copyright (c) 2005 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module defining type strings for the different Python types.
"""

#
# Keep this list in sync with Debugger.Config.ConfigVarTypeFilters
#
ConfigVarTypeStrings = [
    '__', 'NoneType', 'type',
    'bool', 'int', 'long', 'float', 'complex',
    'str', 'unicode', 'tuple', 'list',
    'dict', 'dict-proxy', 'set', 'file', 'xrange',
    'slice', 'buffer', 'class', 'instance',
    'method', 'property', 'generator',
    'function', 'builtin_function_or_method', 'code', 'module',
    'ellipsis', 'traceback', 'frame', 'other', 'frozenset', 'bytes',
    # Special case for Python 2: don't add 'instancemethod' to
    # ConfigVarTypeFilters and leave it always at last position
    'instancemethod'
]

BatchSize = 200
ConfigQtNames = (
    'PyQt5.', 'PyQt4.', 'PySide2.', 'PySide.', 'Shiboken.EnumType'
)
ConfigKnownQtTypes = (
    '.QChar', '.QByteArray', '.QString', '.QStringList', '.QPoint', '.QPointF',
    '.QRect', '.QRectF', '.QSize', '.QSizeF', '.QColor', '.QDate', '.QTime',
    '.QDateTime', '.QDir', '.QFile', '.QFont', '.QUrl', '.QModelIndex',
    '.QRegExp', '.QAction', '.QKeySequence', '.QDomAttr', '.QDomCharacterData',
    '.QDomComment', '.QDomDocument', '.QDomElement', '.QDomText',
    '.QHostAddress', '.EnumType'
)

#
# eflag: noqa = M702
