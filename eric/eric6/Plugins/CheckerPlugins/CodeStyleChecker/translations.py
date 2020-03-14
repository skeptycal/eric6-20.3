# -*- coding: utf-8 -*-

# Copyright (c) 2014 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing message translations for the code style plugin messages.
"""


from PyQt5.QtCore import QCoreApplication

from Globals import translate

__all__ = ["getTranslatedMessage"]

_messages = {
    ##################################################################
    ## pycodestyle messages
    ##################################################################
    "E101": QCoreApplication.translate(
        "pycodestyle",
        "indentation contains mixed spaces and tabs"),
    "E111": QCoreApplication.translate(
        "pycodestyle",
        "indentation is not a multiple of four"),
    "E112": QCoreApplication.translate(
        "pycodestyle",
        "expected an indented block"),
    "E113": QCoreApplication.translate(
        "pycodestyle",
        "unexpected indentation"),
    "E114": QCoreApplication.translate(
        "pycodestyle",
        "indentation is not a multiple of four (comment)"),
    "E115": QCoreApplication.translate(
        "pycodestyle",
        "expected an indented block (comment)"),
    "E116": QCoreApplication.translate(
        "pycodestyle",
        "unexpected indentation (comment)"),
    "E117": QCoreApplication.translate(
        "pycodestyle",
        "over-indented"),
    "E121": QCoreApplication.translate(
        "pycodestyle",
        "continuation line indentation is not a multiple of four"),
    "E122": QCoreApplication.translate(
        "pycodestyle",
        "continuation line missing indentation or outdented"),
    "E123": QCoreApplication.translate(
        "pycodestyle",
        "closing bracket does not match indentation of opening"
        " bracket's line"),
    "E124": QCoreApplication.translate(
        "pycodestyle",
        "closing bracket does not match visual indentation"),
    "E125": QCoreApplication.translate(
        "pycodestyle",
        "continuation line with same indent as next logical line"),
    "E126": QCoreApplication.translate(
        "pycodestyle",
        "continuation line over-indented for hanging indent"),
    "E127": QCoreApplication.translate(
        "pycodestyle",
        "continuation line over-indented for visual indent"),
    "E128": QCoreApplication.translate(
        "pycodestyle",
        "continuation line under-indented for visual indent"),
    "E129": QCoreApplication.translate(
        "pycodestyle",
        "visually indented line with same indent as next logical line"),
    "E131": QCoreApplication.translate(
        "pycodestyle",
        "continuation line unaligned for hanging indent"),
    "E133": QCoreApplication.translate(
        "pycodestyle",
        "closing bracket is missing indentation"),
    "W191": QCoreApplication.translate(
        "pycodestyle",
        "indentation contains tabs"),
    "E201": QCoreApplication.translate(
        "pycodestyle",
        "whitespace after '{0}'"),
    "E202": QCoreApplication.translate(
        "pycodestyle",
        "whitespace before '{0}'"),
    "E203": QCoreApplication.translate(
        "pycodestyle",
        "whitespace before '{0}'"),
    "E211": QCoreApplication.translate(
        "pycodestyle",
        "whitespace before '{0}'"),
    "E221": QCoreApplication.translate(
        "pycodestyle",
        "multiple spaces before operator"),
    "E222": QCoreApplication.translate(
        "pycodestyle",
        "multiple spaces after operator"),
    "E223": QCoreApplication.translate(
        "pycodestyle",
        "tab before operator"),
    "E224": QCoreApplication.translate(
        "pycodestyle",
        "tab after operator"),
    "E225": QCoreApplication.translate(
        "pycodestyle",
        "missing whitespace around operator"),
    "E226": QCoreApplication.translate(
        "pycodestyle",
        "missing whitespace around arithmetic operator"),
    "E227": QCoreApplication.translate(
        "pycodestyle",
        "missing whitespace around bitwise or shift operator"),
    "E228": QCoreApplication.translate(
        "pycodestyle",
        "missing whitespace around modulo operator"),
    "E231": QCoreApplication.translate(
        "pycodestyle",
        "missing whitespace after '{0}'"),
    "E241": QCoreApplication.translate(
        "pycodestyle",
        "multiple spaces after '{0}'"),
    "E242": QCoreApplication.translate(
        "pycodestyle",
        "tab after '{0}'"),
    "E251": QCoreApplication.translate(
        "pycodestyle",
        "unexpected spaces around keyword / parameter equals"),
    "E252": QCoreApplication.translate(
        "pycodestyle",
        "missing whitespace around parameter equals"),
    "E261": QCoreApplication.translate(
        "pycodestyle",
        "at least two spaces before inline comment"),
    "E262": QCoreApplication.translate(
        "pycodestyle",
        "inline comment should start with '# '"),
    "E265": QCoreApplication.translate(
        "pycodestyle",
        "block comment should start with '# '"),
    "E266": QCoreApplication.translate(
        "pycodestyle",
        "too many leading '#' for block comment"),
    "E271": QCoreApplication.translate(
        "pycodestyle",
        "multiple spaces after keyword"),
    "E272": QCoreApplication.translate(
        "pycodestyle",
        "multiple spaces before keyword"),
    "E273": QCoreApplication.translate(
        "pycodestyle",
        "tab after keyword"),
    "E274": QCoreApplication.translate(
        "pycodestyle",
        "tab before keyword"),
    "E275": QCoreApplication.translate(
        "pycodestyle",
        "missing whitespace after keyword"),
    "W291": QCoreApplication.translate(
        "pycodestyle",
        "trailing whitespace"),
    "W292": QCoreApplication.translate(
        "pycodestyle",
        "no newline at end of file"),
    "W293": QCoreApplication.translate(
        "pycodestyle",
        "blank line contains whitespace"),
    "E301": QCoreApplication.translate(
        "pycodestyle",
        "expected {0} blank lines, found {1}"),
    "E302": QCoreApplication.translate(
        "pycodestyle",
        "expected {0} blank lines, found {1}"),
    "E303": QCoreApplication.translate(
        "pycodestyle",
        "too many blank lines ({0}), expected {1}"),
    "E304": QCoreApplication.translate(
        "pycodestyle",
        "blank lines found after function decorator"),
    "E305": QCoreApplication.translate(
        "pycodestyle",
        "expected {0} blank lines after class or function definition,"
        " found {1}"),
    "E306": QCoreApplication.translate(
        "pycodestyle",
        "expected {0} blank lines before a nested definition, found {1}"),
    "E307": QCoreApplication.translate(
        "pycodestyle",
        "too many blank lines ({0}) before a nested definition, expected {1}"),
    "E308": QCoreApplication.translate(
        "pycodestyle",
        "too many blank lines ({0})"),
    "W391": QCoreApplication.translate(
        "pycodestyle",
        "blank line at end of file"),
    "E401": QCoreApplication.translate(
        "pycodestyle",
        "multiple imports on one line"),
    "E402": QCoreApplication.translate(
        "pycodestyle",
        "module level import not at top of file"),
    "E501": QCoreApplication.translate(
        "pycodestyle",
        "line too long ({0} > {1} characters)"),
    "E502": QCoreApplication.translate(
        "pycodestyle",
        "the backslash is redundant between brackets"),
    "W503": QCoreApplication.translate(
        "pycodestyle",
        "line break before binary operator"),
    "W504": QCoreApplication.translate(
        "pycodestyle",
        "line break after binary operator"),
    "W505": QCoreApplication.translate(
        "pycodestyle",
        "doc line too long ({0} > {1} characters)"),
    "W601": QCoreApplication.translate(
        "pycodestyle",
        ".has_key() is deprecated, use 'in'"),
    "W602": QCoreApplication.translate(
        "pycodestyle",
        "deprecated form of raising exception"),
    "W603": QCoreApplication.translate(
        "pycodestyle",
        "'<>' is deprecated, use '!='"),
    "W604": QCoreApplication.translate(
        "pycodestyle",
        "backticks are deprecated, use 'repr()'"),
    "W605": QCoreApplication.translate(
        "pycodestyle",
        "invalid escape sequence '\\{0}'"),
    "W606": QCoreApplication.translate(
        "pycodestyle",
        "'async' and 'await' are reserved keywords starting with Python 3.7"),
    "E701": QCoreApplication.translate(
        "pycodestyle",
        "multiple statements on one line (colon)"),
    "E702": QCoreApplication.translate(
        "pycodestyle",
        "multiple statements on one line (semicolon)"),
    "E703": QCoreApplication.translate(
        "pycodestyle",
        "statement ends with a semicolon"),
    "E704": QCoreApplication.translate(
        "pycodestyle",
        "multiple statements on one line (def)"),
    "E711": QCoreApplication.translate(
        "pycodestyle",
        "comparison to {0} should be {1}"),
    "E712": QCoreApplication.translate(
        "pycodestyle",
        "comparison to {0} should be {1}"),
    "E713": QCoreApplication.translate(
        "pycodestyle",
        "test for membership should be 'not in'"),
    "E714": QCoreApplication.translate(
        "pycodestyle",
        "test for object identity should be 'is not'"),
    "E721": QCoreApplication.translate(
        "pycodestyle",
        "do not compare types, use 'isinstance()'"),
    "E722": QCoreApplication.translate(
        "pycodestyle",
        "do not use bare except"),
    "E731": QCoreApplication.translate(
        "pycodestyle",
        "do not assign a lambda expression, use a def"),
    "E741": QCoreApplication.translate(
        "pycodestyle",
        "ambiguous variable name '{0}'"),
    "E742": QCoreApplication.translate(
        "pycodestyle",
        "ambiguous class definition '{0}'"),
    "E743": QCoreApplication.translate(
        "pycodestyle",
        "ambiguous function definition '{0}'"),
    "E901": QCoreApplication.translate(
        "pycodestyle",
        "{0}: {1}"),
    "E902": QCoreApplication.translate(
        "pycodestyle",
        "{0}"),
    
    ##################################################################
    ## DocStyleChecker messages
    ##################################################################
    "D101": QCoreApplication.translate(
        "DocStyleChecker", "module is missing a docstring"),
    "D102": QCoreApplication.translate(
        "DocStyleChecker",
        "public function/method is missing a docstring"),
    "D103": QCoreApplication.translate(
        "DocStyleChecker",
        "private function/method may be missing a docstring"),
    "D104": QCoreApplication.translate(
        "DocStyleChecker", "public class is missing a docstring"),
    "D105": QCoreApplication.translate(
        "DocStyleChecker", "private class may be missing a docstring"),
    "D111": QCoreApplication.translate(
        "DocStyleChecker", 'docstring not surrounded by """'),
    "D112": QCoreApplication.translate(
        "DocStyleChecker",
        'docstring containing \\ not surrounded by r"""'),
    "D113": QCoreApplication.translate(
        "DocStyleChecker",
        'docstring containing unicode character not surrounded by u"""'),
    "D121": QCoreApplication.translate(
        "DocStyleChecker", "one-liner docstring on multiple lines"),
    "D122": QCoreApplication.translate(
        "DocStyleChecker", "docstring has wrong indentation"),
    "D130": QCoreApplication.translate(
        "DocStyleChecker", "docstring does not contain a summary"),
    "D131": QCoreApplication.translate(
        "DocStyleChecker", "docstring summary does not end with a period"),
    "D132": QCoreApplication.translate(
        "DocStyleChecker",
        "docstring summary is not in imperative mood"
        " (Does instead of Do)"),
    "D133": QCoreApplication.translate(
        "DocStyleChecker",
        "docstring summary looks like a function's/method's signature"),
    "D134": QCoreApplication.translate(
        "DocStyleChecker",
        "docstring does not mention the return value type"),
    "D141": QCoreApplication.translate(
        "DocStyleChecker",
        "function/method docstring is separated by a blank line"),
    "D142": QCoreApplication.translate(
        "DocStyleChecker",
        "class docstring is not preceded by a blank line"),
    "D143": QCoreApplication.translate(
        "DocStyleChecker",
        "class docstring is not followed by a blank line"),
    "D144": QCoreApplication.translate(
        "DocStyleChecker",
        "docstring summary is not followed by a blank line"),
    "D145": QCoreApplication.translate(
        "DocStyleChecker",
        "last paragraph of docstring is not followed by a blank line"),
    
    "D201": QCoreApplication.translate(
        "DocStyleChecker", "module docstring is still a default string"),
    "D202": QCoreApplication.translate(
        "DocStyleChecker", "function docstring is still a default string"),
    "D203": QCoreApplication.translate(
        "DocStyleChecker",
        "private function/method is missing a docstring"),
    "D205": QCoreApplication.translate(
        "DocStyleChecker", "private class is missing a docstring"),
    "D206": QCoreApplication.translate(
        "DocStyleChecker", "class docstring is still a default string"),
    "D221": QCoreApplication.translate(
        "DocStyleChecker",
        "leading quotes of docstring not on separate line"),
    "D222": QCoreApplication.translate(
        "DocStyleChecker",
        "trailing quotes of docstring not on separate line"),
    "D231": QCoreApplication.translate(
        "DocStyleChecker", "docstring summary does not end with a period"),
    "D232": QCoreApplication.translate(
        "DocStyleChecker", "docstring summary does not start with '{0}'"),
    "D234": QCoreApplication.translate(
        "DocStyleChecker",
        "docstring does not contain a @return line but function/method"
        " returns something"),
    "D235": QCoreApplication.translate(
        "DocStyleChecker",
        "docstring contains a @return line but function/method doesn't"
        " return anything"),
    "D236": QCoreApplication.translate(
        "DocStyleChecker",
        "docstring does not contain enough @param/@keyparam lines"),
    "D237": QCoreApplication.translate(
        "DocStyleChecker",
        "docstring contains too many @param/@keyparam lines"),
    "D238": QCoreApplication.translate(
        "DocStyleChecker",
        "keyword only arguments must be documented with @keyparam lines"),
    "D239": QCoreApplication.translate(
        "DocStyleChecker", "order of @param/@keyparam lines does"
        " not match the function/method signature"),
    "D242": QCoreApplication.translate(
        "DocStyleChecker", "class docstring is preceded by a blank line"),
    "D243": QCoreApplication.translate(
        "DocStyleChecker", "class docstring is followed by a blank line"),
    "D244": QCoreApplication.translate(
        "DocStyleChecker",
        "function/method docstring is preceded by a blank line"),
    "D245": QCoreApplication.translate(
        "DocStyleChecker",
        "function/method docstring is followed by a blank line"),
    "D246": QCoreApplication.translate(
        "DocStyleChecker",
        "docstring summary is not followed by a blank line"),
    "D247": QCoreApplication.translate(
        "DocStyleChecker",
        "last paragraph of docstring is followed by a blank line"),
    "D250": QCoreApplication.translate(
        "DocStyleChecker",
        "docstring does not contain a @exception line but function/method"
        " raises an exception"),
    "D251": QCoreApplication.translate(
        "DocStyleChecker",
        "docstring contains a @exception line but function/method doesn't"
        " raise an exception"),
    "D252": QCoreApplication.translate(
        "DocStyleChecker",
        "raised exception '{0}' is not documented in docstring"),
    "D253": QCoreApplication.translate(
        "DocStyleChecker",
        "documented exception '{0}' is not raised"),
    "D260": QCoreApplication.translate(
        "DocStyleChecker",
        "docstring does not contain a @signal line but class defines signals"),
    "D261": QCoreApplication.translate(
        "DocStyleChecker",
        "docstring contains a @signal line but class doesn't define signals"),
    "D262": QCoreApplication.translate(
        "DocStyleChecker",
        "defined signal '{0}' is not documented in docstring"),
    "D263": QCoreApplication.translate(
        "DocStyleChecker",
        "documented signal '{0}' is not defined"),
    
    "D901": QCoreApplication.translate(
        "DocStyleChecker", "{0}: {1}"),
    
    ##################################################################
    ## NamingStyleChecker messages
    ##################################################################
    "N801": QCoreApplication.translate(
        "NamingStyleChecker",
        "class names should use CapWords convention"),
    "N802": QCoreApplication.translate(
        "NamingStyleChecker",
        "function name should be lowercase"),
    "N803": QCoreApplication.translate(
        "NamingStyleChecker",
        "argument name should be lowercase"),
    "N804": QCoreApplication.translate(
        "NamingStyleChecker",
        "first argument of a class method should be named 'cls'"),
    "N805": QCoreApplication.translate(
        "NamingStyleChecker",
        "first argument of a method should be named 'self'"),
    "N806": QCoreApplication.translate(
        "NamingStyleChecker",
        "first argument of a static method should not be named"
        " 'self' or 'cls"),
    "N807": QCoreApplication.translate(
        "NamingStyleChecker",
        "module names should be lowercase"),
    "N808": QCoreApplication.translate(
        "NamingStyleChecker",
        "package names should be lowercase"),
    "N811": QCoreApplication.translate(
        "NamingStyleChecker",
        "constant imported as non constant"),
    "N812": QCoreApplication.translate(
        "NamingStyleChecker",
        "lowercase imported as non lowercase"),
    "N813": QCoreApplication.translate(
        "NamingStyleChecker",
        "camelcase imported as lowercase"),
    "N814": QCoreApplication.translate(
        "NamingStyleChecker",
        "camelcase imported as constant"),
    "N821": QCoreApplication.translate(
        "NamingStyleChecker",
        "variable in function should be lowercase"),
    "N831": QCoreApplication.translate(
        "NamingStyleChecker",
        "names 'l', 'O' and 'I' should be avoided"),
    
    ##################################################################
    ## Code complexity messages
    ##################################################################
    "C101": QCoreApplication.translate(
        "ComplexityChecker", "'{0}' is too complex ({1})"),
    "C111": QCoreApplication.translate(
        "ComplexityChecker", "source code line is too complex ({0})"),
    "C112": QCoreApplication.translate(
        "ComplexityChecker",
        "overall source code line complexity is too high ({0})"),
    "C901": QCoreApplication.translate(
        "ComplexityChecker", "{0}: {1}"),
    
    ##################################################################
    ## Messages of the Miscellaneous Checker
    ##################################################################
    "M101": QCoreApplication.translate(
        "MiscellaneousChecker",
        "coding magic comment not found"),
    "M102": QCoreApplication.translate(
        "MiscellaneousChecker",
        "unknown encoding ({0}) found in coding magic comment"),
    "M111": QCoreApplication.translate(
        "MiscellaneousChecker",
        "copyright notice not present"),
    "M112": QCoreApplication.translate(
        "MiscellaneousChecker",
        "copyright notice contains invalid author"),
    "M131": QCoreApplication.translate(
        "MiscellaneousChecker",
        '"{0}" is a Python builtin and is being shadowed; '
        'consider renaming the variable'),
    "M132": QCoreApplication.translate(
        "MiscellaneousChecker",
        '"{0}" is used as an argument and thus shadows a '
        'Python builtin; consider renaming the argument'),
    "M181": QCoreApplication.translate(
        "MiscellaneousChecker",
        'unnecessary generator - rewrite as a list comprehension'),
    "M182": QCoreApplication.translate(
        "MiscellaneousChecker",
        'unnecessary generator - rewrite as a set comprehension'),
    "M183": QCoreApplication.translate(
        "MiscellaneousChecker",
        'unnecessary generator - rewrite as a dict comprehension'),
    "M184": QCoreApplication.translate(
        "MiscellaneousChecker",
        'unnecessary list comprehension - rewrite as a set comprehension'),
    "M185": QCoreApplication.translate(
        "MiscellaneousChecker",
        'unnecessary list comprehension - rewrite as a dict comprehension'),
    "M186": QCoreApplication.translate(
        "MiscellaneousChecker",
        'unnecessary {0} call - rewrite as a literal'),
    "M187": QCoreApplication.translate(
        "MiscellaneousChecker",
        'unnecessary list comprehension - "{0}" can take a generator'),
    "M191": QCoreApplication.translate(
        "MiscellaneousChecker",
        'unnecessary {0} literal - rewrite as a {1} literal'),
    "M192": QCoreApplication.translate(
        "MiscellaneousChecker",
        'unnecessary {0} passed to tuple() - rewrite as a {1} literal'),
    "M193": QCoreApplication.translate(
        "MiscellaneousChecker",
        'unnecessary {0} passed to list() - rewrite as a {1} literal'),
    "M195": QCoreApplication.translate(
        "MiscellaneousChecker",
        'unnecessary list call - remove the outer call to list()'),
    "M196": QCoreApplication.translate(
        "MiscellaneousChecker",
        'unnecessary list comprehension - "in" can take a generator'),
    "M197": QCoreApplication.translate(
        "MiscellaneousChecker",
        'unnecessary {0} passed to tuple() - remove the outer call to {1}()'),
    "M198": QCoreApplication.translate(
        "MiscellaneousChecker",
        'unnecessary {0} passed to list() - remove the outer call to {1}()'),
    
    "M201": QCoreApplication.translate(
        "MiscellaneousChecker",
        "sort keys - '{0}' should be before '{1}'"),
    
    "M301": QCoreApplication.translate(
        "MiscellaneousChecker",
        "use of 'datetime.datetime()' without 'tzinfo' argument should be"
        " avoided"),
    "M302": QCoreApplication.translate(
        "MiscellaneousChecker",
        "use of 'datetime.datetime.today()' should be avoided.\n"
        "Use 'datetime.datetime.now(tz=)' instead."),
    "M303": QCoreApplication.translate(
        "MiscellaneousChecker",
        "use of 'datetime.datetime.utcnow()' should be avoided.\n"
        "Use 'datetime.datetime.now(tz=)' instead."),
    "M304": QCoreApplication.translate(
        "MiscellaneousChecker",
        "use of 'datetime.datetime.utcfromtimestamp()' should be avoided.\n"
        "Use 'datetime.datetime.fromtimestamp(, tz=)' instead."),
    "M305": QCoreApplication.translate(
        "MiscellaneousChecker",
        "use of 'datetime.datetime.now()' without 'tz' argument should be"
        " avoided"),
    "M306": QCoreApplication.translate(
        "MiscellaneousChecker",
        "use of 'datetime.datetime.fromtimestamp()' without 'tz' argument"
        " should be avoided"),
    "M307": QCoreApplication.translate(
        "MiscellaneousChecker",
        "use of 'datetime.datetime.strptime()' should be followed by"
        " '.replace(tzinfo=)'"),
    "M308": QCoreApplication.translate(
        "MiscellaneousChecker",
        "use of 'datetime.datetime.fromordinal()' should be avoided"),
    "M311": QCoreApplication.translate(
        "MiscellaneousChecker",
        "use of 'datetime.date()' should be avoided.\n"
        "Use 'datetime.datetime(, tzinfo=).date()' instead."),
    "M312": QCoreApplication.translate(
        "MiscellaneousChecker",
        "use of 'datetime.date.today()' should be avoided.\n"
        "Use 'datetime.datetime.now(tz=).date()' instead."),
    "M313": QCoreApplication.translate(
        "MiscellaneousChecker",
        "use of 'datetime.date.fromtimestamp()' should be avoided.\n"
        "Use 'datetime.datetime.fromtimestamp(tz=).date()' instead."),
    "M314": QCoreApplication.translate(
        "MiscellaneousChecker",
        "use of 'datetime.date.fromordinal()' should be avoided"),
    "M315": QCoreApplication.translate(
        "MiscellaneousChecker",
        "use of 'datetime.date.fromisoformat()' should be avoided"),
    "M321": QCoreApplication.translate(
        "MiscellaneousChecker",
        "use of 'datetime.time()' without 'tzinfo' argument should be"
        " avoided"),
    
    "M401": QCoreApplication.translate(
        "MiscellaneousChecker",
        "'sys.version[:3]' referenced (Python 3.10), use 'sys.version_info'"),
    "M402": QCoreApplication.translate(
        "MiscellaneousChecker",
        "'sys.version[2]' referenced (Python 3.10), use 'sys.version_info'"),
    "M403": QCoreApplication.translate(
        "MiscellaneousChecker",
        "'sys.version' compared to string (Python 3.10), use"
        " 'sys.version_info'"),
    "M411": QCoreApplication.translate(
        "MiscellaneousChecker",
        "'sys.version_info[0] == 3' referenced (Python 4), use '>='"),
    "M412": QCoreApplication.translate(
        "MiscellaneousChecker",
        "'six.PY3' referenced (Python 4), use 'not six.PY2'"),
    "M413": QCoreApplication.translate(
        "MiscellaneousChecker",
        "'sys.version_info[1]' compared to integer (Python 4),"
        " compare 'sys.version_info' to tuple"),
    "M414": QCoreApplication.translate(
        "MiscellaneousChecker",
        "'sys.version_info.minor' compared to integer (Python 4),"
        " compare 'sys.version_info' to tuple"),
    "M421": QCoreApplication.translate(
        "MiscellaneousChecker",
        "'sys.version[0]' referenced (Python 10), use 'sys.version_info'"),
    "M422": QCoreApplication.translate(
        "MiscellaneousChecker",
        "'sys.version' compared to string (Python 10),"
        " use 'sys.version_info'"),
    "M423": QCoreApplication.translate(
        "MiscellaneousChecker",
        "'sys.version[:1]' referenced (Python 10), use 'sys.version_info'"),
    
    "M501": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Python does not support the unary prefix increment"),
    "M502": QCoreApplication.translate(
        "MiscellaneousChecker",
        "using .strip() with multi-character strings is misleading"),
    "M503": QCoreApplication.translate(
        "MiscellaneousChecker",
        "do not call assert False since python -O removes these calls"),
    "M504": QCoreApplication.translate(
        "MiscellaneousChecker",
        "'sys.maxint' is not defined in Python 3 - use 'sys.maxsize'"),
    "M505": QCoreApplication.translate(
        "MiscellaneousChecker",
        "'BaseException.message' has been deprecated as of Python 2.6 and is"
        " removed in Python 3 - use 'str(e)'"),
    "M506": QCoreApplication.translate(
        "MiscellaneousChecker",
        "assigning to 'os.environ' does not clear the environment -"
        " use 'os.environ.clear()'"),
    "M507": QCoreApplication.translate(
        "MiscellaneousChecker",
        "loop control variable {0} not used within the loop body -"
        " start the name with an underscore"),
    "M508": QCoreApplication.translate(
        "MiscellaneousChecker",
        "unncessary f-string"),
    "M509": QCoreApplication.translate(
        "MiscellaneousChecker",
        "cannot use 'self.__class__' as first argument of 'super()' call"),
    "M511": QCoreApplication.translate(
        "MiscellaneousChecker",
        """using 'hasattr(x, "__call__")' to test if 'x' is callable is"""
        """ unreliable"""),
    "M512": QCoreApplication.translate(
        "MiscellaneousChecker",
        "do not call getattr with a constant attribute value"),
    "M513": QCoreApplication.translate(
        "MiscellaneousChecker",
        "do not call setattr with a constant attribute value"),
    "M521": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Python 3 does not include '.iter*' methods on dictionaries"),
    "M522": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Python 3 does not include '.view*' methods on dictionaries"),
    "M523": QCoreApplication.translate(
        "MiscellaneousChecker",
        "'.next()' does not exist in Python 3"),
    "M524": QCoreApplication.translate(
        "MiscellaneousChecker",
        "'__metaclass__' does nothing on Python 3 -"
        " use 'class MyClass(BaseClass, metaclass=...)'"),
    
    "M601": QCoreApplication.translate(
        "MiscellaneousChecker",
        "found {0} formatter"),
    "M611": QCoreApplication.translate(
        "MiscellaneousChecker",
        "format string does contain unindexed parameters"),
    "M612": QCoreApplication.translate(
        "MiscellaneousChecker",
        "docstring does contain unindexed parameters"),
    "M613": QCoreApplication.translate(
        "MiscellaneousChecker",
        "other string does contain unindexed parameters"),
    "M621": QCoreApplication.translate(
        "MiscellaneousChecker",
        "format call uses too large index ({0})"),
    "M622": QCoreApplication.translate(
        "MiscellaneousChecker",
        "format call uses missing keyword ({0})"),
    "M623": QCoreApplication.translate(
        "MiscellaneousChecker",
        "format call uses keyword arguments but no named entries"),
    "M624": QCoreApplication.translate(
        "MiscellaneousChecker",
        "format call uses variable arguments but no numbered entries"),
    "M625": QCoreApplication.translate(
        "MiscellaneousChecker",
        "format call uses implicit and explicit indexes together"),
    "M631": QCoreApplication.translate(
        "MiscellaneousChecker",
        "format call provides unused index ({0})"),
    "M632": QCoreApplication.translate(
        "MiscellaneousChecker",
        "format call provides unused keyword ({0})"),
    "M651": QCoreApplication.translate(
        "MiscellaneousChecker",
        "logging statement uses string.format()"),
    "M652": QCoreApplication.translate(
        "MiscellaneousChecker",
        "logging statement uses '%'"),          # __IGNORE_WARNING_M601__
    "M653": QCoreApplication.translate(
        "MiscellaneousChecker",
        "logging statement uses '+'"),
    "M654": QCoreApplication.translate(
        "MiscellaneousChecker",
        "logging statement uses f-string"),
    "M655": QCoreApplication.translate(
        "MiscellaneousChecker",
        "logging statement uses 'warn' instead of 'warning'"),
    
    "M701": QCoreApplication.translate(
        "MiscellaneousChecker",
        "expected these __future__ imports: {0}; but only got: {1}"),
    "M702": QCoreApplication.translate(
        "MiscellaneousChecker",
        "expected these __future__ imports: {0}; but got none"),
    "M711": QCoreApplication.translate(
        "MiscellaneousChecker",
        "gettext import with alias _ found: {0}"),
    
    "M801": QCoreApplication.translate(
        "MiscellaneousChecker",
        "print statement found"),
    "M811": QCoreApplication.translate(
        "MiscellaneousChecker",
        "one element tuple found"),
    "M821": QCoreApplication.translate(
        "MiscellaneousChecker",
        "mutable default argument of type {0}"),
    "M822": QCoreApplication.translate(
        "MiscellaneousChecker",
        "mutable default argument of type {0}"),
    "M823": QCoreApplication.translate(
        "MiscellaneousChecker",
        "mutable default argument of function call '{0}'"),
    "M831": QCoreApplication.translate(
        "MiscellaneousChecker",
        "None should not be added at any return if function has no return"
        " value except None"),
    "M832": QCoreApplication.translate(
        "MiscellaneousChecker",
        "an explicit value at every return should be added if function has"
        " a return value except None"),
    "M833": QCoreApplication.translate(
        "MiscellaneousChecker",
        "an explicit return at the end of the function should be added if"
        " it has a return value except None"),
    "M834": QCoreApplication.translate(
        "MiscellaneousChecker",
        "a value should not be assigned to a variable if it will be used as a"
        " return value only"),
    "M841": QCoreApplication.translate(
        "MiscellaneousChecker",
        "prefer implied line continuation inside parentheses, "
        "brackets and braces as opposed to a backslash"),
    "M891": QCoreApplication.translate(
        "MiscellaneousChecker",
        "commented code lines should be removed"),
    
    "M901": QCoreApplication.translate(
        "MiscellaneousChecker",
        "{0}: {1}"),
    
    
    ##################################################################
    ## Messages of the Annotations Checker
    ##################################################################
    "A001": QCoreApplication.translate(
        "AnnotationsChecker",
        "missing type annotation for function argument '{0}'"),
    "A002": QCoreApplication.translate(
        "AnnotationsChecker",
        "missing type annotation for '*{0}'"),
    "A003": QCoreApplication.translate(
        "AnnotationsChecker",
        "missing type annotation for '**{0}'"),
    "A101": QCoreApplication.translate(
        "AnnotationsChecker",
        "missing type annotation for 'self' in method"),
    "A102": QCoreApplication.translate(
        "AnnotationsChecker",
        "missing type annotation for 'cls' in classmethod"),
    "A201": QCoreApplication.translate(
        "AnnotationsChecker",
        "missing return type annotation for public function"),
    "A202": QCoreApplication.translate(
        "AnnotationsChecker",
        "missing return type annotation for protected function"),
    "A203": QCoreApplication.translate(
        "AnnotationsChecker",
        "missing return type annotation for private function"),
    "A204": QCoreApplication.translate(
        "AnnotationsChecker",
        "missing return type annotation for special method"),
    "A205": QCoreApplication.translate(
        "AnnotationsChecker",
        "missing return type annotation for staticmethod"),
    "A206": QCoreApplication.translate(
        "AnnotationsChecker",
        "missing return type annotation for classmethod"),
    
    "A881": QCoreApplication.translate(
        "AnnotationsChecker",
        "type annotation coverage of {0}% is too low"),
    
    "A891": QCoreApplication.translate(
        "AnnotationsChecker",
        "type annotation is too complex ({0} > {1})"),
    
    "A999": QCoreApplication.translate(
        "AnnotationsChecker",
        "{0}: {1}"),
    
    ##################################################################
    ## CodeStyleFixer messages
    ##################################################################
    "FD111": QCoreApplication.translate(
        'CodeStyleFixer',
        "Triple single quotes converted to triple double quotes."),
    'FD112': QCoreApplication.translate(
        'CodeStyleFixer',
        'Introductory quotes corrected to be {0}"""'),
    "FD121": QCoreApplication.translate(
        'CodeStyleFixer',
        "Single line docstring put on one line."),
    "FD131": QCoreApplication.translate(
        'CodeStyleFixer',
        "Period added to summary line."),
    "FD141": QCoreApplication.translate(
        'CodeStyleFixer',
        "Blank line before function/method docstring removed."),
    "FD142": QCoreApplication.translate(
        'CodeStyleFixer',
        "Blank line inserted before class docstring."),
    "FD143": QCoreApplication.translate(
        'CodeStyleFixer',
        "Blank line inserted after class docstring."),
    "FD144": QCoreApplication.translate(
        'CodeStyleFixer',
        "Blank line inserted after docstring summary."),
    "FD145": QCoreApplication.translate(
        'CodeStyleFixer',
        "Blank line inserted after last paragraph of docstring."),
    "FD221": QCoreApplication.translate(
        'CodeStyleFixer',
        "Leading quotes put on separate line."),
    "FD222": QCoreApplication.translate(
        'CodeStyleFixer',
        "Trailing quotes put on separate line."),
    "FD242": QCoreApplication.translate(
        'CodeStyleFixer',
        "Blank line before class docstring removed."),
    "FD244": QCoreApplication.translate(
        'CodeStyleFixer',
        "Blank line before function/method docstring removed."),
    "FD243": QCoreApplication.translate(
        'CodeStyleFixer',
        "Blank line after class docstring removed."),
    "FD245": QCoreApplication.translate(
        'CodeStyleFixer',
        "Blank line after function/method docstring removed."),
    "FD247": QCoreApplication.translate(
        'CodeStyleFixer',
        "Blank line after last paragraph removed."),
    "FE101": QCoreApplication.translate(
        'CodeStyleFixer',
        "Tab converted to 4 spaces."),
    "FE111": QCoreApplication.translate(
        'CodeStyleFixer',
        "Indentation adjusted to be a multiple of four."),
    "FE121": QCoreApplication.translate(
        'CodeStyleFixer',
        "Indentation of continuation line corrected."),
    "FE124": QCoreApplication.translate(
        'CodeStyleFixer',
        "Indentation of closing bracket corrected."),
    "FE122": QCoreApplication.translate(
        'CodeStyleFixer',
        "Missing indentation of continuation line corrected."),
    "FE123": QCoreApplication.translate(
        'CodeStyleFixer',
        "Closing bracket aligned to opening bracket."),
    "FE125": QCoreApplication.translate(
        'CodeStyleFixer',
        "Indentation level changed."),
    "FE126": QCoreApplication.translate(
        'CodeStyleFixer',
        "Indentation level of hanging indentation changed."),
    "FE127": QCoreApplication.translate(
        'CodeStyleFixer',
        "Visual indentation corrected."),
    "FE201": QCoreApplication.translate(
        'CodeStyleFixer',
        "Extraneous whitespace removed."),
    "FE225": QCoreApplication.translate(
        'CodeStyleFixer',
        "Missing whitespace added."),
    "FE221": QCoreApplication.translate(
        'CodeStyleFixer',
        "Extraneous whitespace removed."),
    "FE231": QCoreApplication.translate(
        'CodeStyleFixer',
        "Missing whitespace added."),
    "FE251": QCoreApplication.translate(
        'CodeStyleFixer',
        "Extraneous whitespace removed."),
    "FE261": QCoreApplication.translate(
        'CodeStyleFixer',
        "Whitespace around comment sign corrected."),
    
    "FE302+": lambda n=1: translate(
        'CodeStyleFixer',
        "%n blank line(s) inserted.", '', n),
    "FE302-": lambda n=1: translate(
        'CodeStyleFixer',
        "%n superfluous lines removed", '', n),
    
    "FE303": QCoreApplication.translate(
        'CodeStyleFixer',
        "Superfluous blank lines removed."),
    "FE304": QCoreApplication.translate(
        'CodeStyleFixer',
        "Superfluous blank lines after function decorator removed."),
    "FE401": QCoreApplication.translate(
        'CodeStyleFixer',
        "Imports were put on separate lines."),
    "FE501": QCoreApplication.translate(
        'CodeStyleFixer',
        "Long lines have been shortened."),
    "FE502": QCoreApplication.translate(
        'CodeStyleFixer',
        "Redundant backslash in brackets removed."),
    "FE701": QCoreApplication.translate(
        'CodeStyleFixer',
        "Compound statement corrected."),
    "FE702": QCoreApplication.translate(
        'CodeStyleFixer',
        "Compound statement corrected."),
    "FE711": QCoreApplication.translate(
        'CodeStyleFixer',
        "Comparison to None/True/False corrected."),
    "FN804": QCoreApplication.translate(
        'CodeStyleFixer',
        "'{0}' argument added."),
    "FN806": QCoreApplication.translate(
        'CodeStyleFixer',
        "'{0}' argument removed."),
    "FW291": QCoreApplication.translate(
        'CodeStyleFixer',
        "Whitespace stripped from end of line."),
    "FW292": QCoreApplication.translate(
        'CodeStyleFixer',
        "newline added to end of file."),
    "FW391": QCoreApplication.translate(
        'CodeStyleFixer',
        "Superfluous trailing blank lines removed from end of file."),
    "FW603": QCoreApplication.translate(
        'CodeStyleFixer',
        "'<>' replaced by '!='."),
        
    "FWRITE_ERROR": QCoreApplication.translate(
        'CodeStyleFixer',
        "Could not save the file! Skipping it. Reason: {0}"),
}

_messages_sample_args = {
    "E201": ["([{"],
    "E202": ["}])"],
    "E203": [",;:"],
    "E211": ["(["],
    "E231": [",;:"],
    "E241": [",;:"],
    "E242": [",;:"],
    "E301": [1, 0],
    "E302": [2, 1],
    "E303": [3, 2],
    "E305": [2, 1],
    "E306": [1, 0],
    "E307": [3, 1],
    "E308": [3],
    "E501": [85, 79],
    "W505": [80, 72],
    "E605": ["A"],
    "E711": ["None", "'if cond is None:'"],
    "E712": ["True", "'if cond is True:' or 'if cond:'"],
    "E741": ["l"],
    "E742": ["l"],
    "E743": ["l"],
    "E901": ["SyntaxError", "Invalid Syntax"],
    "E902": ["IOError"],
    
    "D232": ["public"],
    "D252": ["RuntimeError"],
    "D253": ["RuntimeError"],
    "D262": ["buttonClicked"],
    "D263": ["buttonClicked"],
    "D901": ["SyntaxError", "Invalid Syntax"],
    
    "C101": ["foo.bar", "42"],
    "C111": [42],
    "C112": [12.0],
    "C901": ["SyntaxError", "Invalid Syntax"],
    
    "M102": ["enc42"],
    "M131": ["list"],
    "M132": ["list"],
    "M188": ["sorted"],
    "M186": ["list"],
    "M191": ["list", "set"],
    "M192": ["list", "tuple"],
    "M193": ["tuple", "list"],
    "M197": ["tuple", "tuple"],
    "M198": ["list", "list"],
    "M201": ["bar", "foo"],
    "M507": ["x"],
    "M601": ["%s"],
    "M621": [5],
    "M622": ["foo"],
    "M631": [5],
    "M632": ["foo"],
    "M701": ["print_function, unicode_literals", "print_function"],
    "M702": ["print_function, unicode_literals"],
    "M711": ["lgettext"],
    "M821": ["Dict"],
    "M822": ["Call"],
    "M823": ["dict"],
    "M901": ["SyntaxError", "Invalid Syntax"],
    
    "A001": ["arg1"],
    "A002": ["args"],
    "A003": ["kwargs"],
    "A881": [60],
    "A891": [5, 3],
    "A999": ["SyntaxError", "Invalid Syntax"],
    
    "FWRITE_ERROR": ["IOError"],
}


def getTranslatedMessage(message):
    """
    Module function to get a translated and formatted message for a
    given pyflakes message ID.
    
    @param message the message ID (string)
    @return translated and formatted message (string)
    """
    if isinstance(message, list):
        message, args = message
    else:
        args = []

    if message in _messages:
        if isinstance(args, int):
            # Retranslate with correct plural form
            return _messages[message](args)
        else:
            if message.startswith(('FD', 'FE', 'FN', 'FW')):
                prefix = ''
            else:
                prefix = message + ' '
            return prefix + _messages[message].format(*args)
    elif ' ' in message:
        # already translated
        return message
    else:
        return QCoreApplication.translate(
            "CodeStyleFixer", " no message defined for code '{0}'"
        ).format(message)

#
# eflag: noqa = M201
