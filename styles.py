import wx
import wx.stc as stc
import pickle
import util

STYLE_PATH = 'styles.dat'

def create_color(red, green, blue):
    return wx.Colour(red, green, blue)
    
def create_font(name, size, bold=False, italic=False, underline=False):
    weight = wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL
    style = wx.FONTSTYLE_ITALIC if italic else wx.FONTSTYLE_NORMAL
    font = wx.Font(size, wx.FONTFAMILY_DEFAULT, style, weight, underline, name)
    return font
    
class StyleManager(object):
    def __init__(self):
        self.load()
    def load(self):
        try:
            file = open(STYLE_PATH, 'rb')
            pickler = pickle.Unpickler(file)
            self.base_style = pickler.load()
            self.app_styles = pickler.load()
            self.languages = pickler.load()
            file.close()
        except:
            self.base_style = create_base_style()
            self.app_styles = create_app_styles(self.base_style)
            self.languages = create_languages(self.base_style)
    def save(self):
        try:
            file = open(STYLE_PATH, 'wb')
            pickler = pickle.Pickler(file, -1)
            pickler.dump(self.base_style)
            pickler.dump(self.app_styles)
            pickler.dump(self.languages)
            file.close()
        except:
            pass
    def get_language(self, extension):
        extension = extension.lower().strip('.')
        for language in self.languages:
            if extension in language.extensions:
                return language
        return None
        
class Style(object):
    def __init__(self, parent=None, number=None, name=None, preview=None, 
        font=None, size=None, bold=None, italic=None, underline=None, 
        foreground=None, background=None):
        self._parent = parent
        self._number = number
        self._name = name
        self._preview = preview or name
        self._font = font
        self._size = size
        self._bold = bold
        self._italic = italic
        self._underline = underline
        self._foreground = foreground
        self._background = background
        self._children = []
        if parent:
            parent._children.append(self)
    def __cmp__(self, other):
        return cmp(self.preview, other.preview)
    def __setattr__(self, name, value):
        if name.startswith('_'):
            super(Style, self).__setattr__(name, value)
        else:
            setattr(self, '_%s' % name, value)
    def __getattr__(self, name):
        if name.startswith('_'):
            return super(Style, self).__getattr__(name)
        value = getattr(self, '_%s' % name)
        if value is None and self._parent:
            return getattr(self._parent, name)
        return value
    def clear(self):
        if self._parent is None:
            return
        self.font = None
        self.size = None
        self.bold = None
        self.italic = None
        self.underline = None
        self.foreground = None
        self.background = None
    def get_child(self, number):
        for child in self._children:
            if child.number == number:
                return child
        return None
    def create_font(self):
        return create_font(self.font, self.size, self.bold, self.italic, self.underline)
    def create_foreground(self):
        return create_color(*self.foreground)
    def create_background(self):
        return create_color(*self.background)
        
class Language(object):
    def __init__(self, name, extensions=[], lexer=stc.STC_LEX_NULL, 
        base_style=None, styles=[], keywords='', keywords2=''):
        self.name = name
        self.extensions = extensions
        self.lexer = lexer
        self.base_style = base_style
        self.styles = styles
        self.keywords = keywords
        self.keywords2 = keywords2
        
def create_base_style():
    base_style = Style(None, stc.STC_STYLE_DEFAULT, 'Global Style', None, 
        util.get_font(), 10, False, False, False, 
        (0,0,0), (255,255,255))
    return base_style
        
def create_app_styles(parent):
    app_styles = [
        Style(parent, stc.STC_STYLE_BRACELIGHT, 'Brace (Matched)'),
        Style(parent, stc.STC_STYLE_BRACEBAD, 'Brace (Unmatched)'),
        Style(parent, stc.STC_STYLE_CONTROLCHAR, 'Control Character'),
        Style(parent, stc.STC_STYLE_INDENTGUIDE, 'Indentation Guides'),
        Style(parent, stc.STC_STYLE_LINENUMBER, 'Line Number Margin'),
    ]
    return app_styles
    
def create_languages(base_style):
    result = []
    
    # Python
    style = Style(base_style, name='Python Base Style')
    python = Language(
        name='Python',
        extensions=['py', 'pyw'],
        lexer=stc.STC_LEX_PYTHON,
        base_style=style,
        styles=[
            Style(style, stc.STC_P_CHARACTER, 'Character'),
            Style(style, stc.STC_P_CLASSNAME, 'Classname'),
            Style(style, stc.STC_P_COMMENTBLOCK, 'Comment Block'),
            Style(style, stc.STC_P_COMMENTLINE, 'Comment Line'),
            Style(style, stc.STC_P_DECORATOR, 'Decorator'),
            Style(style, stc.STC_P_DEFAULT, 'Whitespace'),
            Style(style, stc.STC_P_DEFNAME, 'Defname'),
            Style(style, stc.STC_P_IDENTIFIER, 'Identifier'),
            Style(style, stc.STC_P_NUMBER, 'Number'),
            Style(style, stc.STC_P_OPERATOR, 'Operator'),
            Style(style, stc.STC_P_STRING, 'String'),
            Style(style, stc.STC_P_STRINGEOL, 'String EOL'),
            Style(style, stc.STC_P_TRIPLE, 'Triple'),
            Style(style, stc.STC_P_TRIPLEDOUBLE, 'Tripledouble'),
            Style(style, stc.STC_P_WORD, 'Keyword'),
            Style(style, stc.STC_P_WORD2, 'Keyword 2'),
        ],
        keywords='''
            and del from not while as elif global or with assert else if pass yield
            break except import print class exec in raise continue finally is return
            def for lambda try
        ''',
        keywords2='''
            ArithmeticError AssertionError AttributeError
            BaseException DeprecationWarning EOFError Ellipsis EnvironmentError
            Exception False FloatingPointError FutureWarning GeneratorExit IOError
            ImportError ImportWarning IndentationError IndexError KeyError
            KeyboardInterrupt LookupError MemoryError NameError None NotImplemented
            NotImplementedError OSError OverflowError PendingDeprecationWarning
            ReferenceError RuntimeError RuntimeWarning StandardError
            StopIteration SyntaxError SyntaxWarning SystemError SystemExit
            TabError True TypeError UnboundLocalError UnicodeDecodeError
            UnicodeEncodeError UnicodeError UnicodeTranslateError UnicodeWarning
            UserWarning ValueError Warning WindowsError ZeroDivisionError
            __debug__ __doc__ __import__ __name__ abs all any apply basestring
            bool buffer callable chr classmethod cmp coerce compile complex
            copyright credits delattr dict dir divmod enumerate eval execfile
            exit file filter float frozenset getattr globals hasattr hash help
            hex id input int intern isinstance issubclass iter len license list
            locals long map max min object oct open ord pow property quit range
            raw_input reduce reload repr reversed round set setattr slice sorted
            staticmethod str sum super tuple type unichr unicode vars xrange zip
        '''
    )
    result.append(python)
    
    return result
    
