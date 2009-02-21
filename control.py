import wx
import wx.stc as stc
import os
from settings import settings

EXTENSIONS = {
'.ada': 'ada',
'.asp': 'asp',
'.bat': 'batch',
'.conf': 'conf',
'.cpp': 'cpp',
'.diff': 'diff',
'.xhtml': 'hypertext',
'.html': 'hypertext',
'.htm': 'hypertext',
'.lisp': 'lisp',
'.lua': 'lua',
'makefile': 'makefile',
'.tab': 'nncrontab',
'.pascal': 'pascal',
'.pl': 'perl',
'.php': 'php',
'.props': 'props',
'.py': 'python',
'.pyw': 'python',
'.rb': 'ruby',
'.sql': 'sql',
'.tcl': 'tcl',
'.vb': 'vb',
'.vbscript': 'vbscript',
'.xml': 'xml',
}

class EditorControl(stc.StyledTextCtrl):
    LINE_MARGIN = 0
    BOOKMARK_MARGIN = 1
    FOLDING_MARGIN = 2
    def __init__(self, *args, **kwargs):
        super(EditorControl, self).__init__(*args, **kwargs)
        self.file_path = None
        self.edited = False
        self.apply_settings()
        self.SetEOLMode(stc.STC_EOL_LF)
        self.SetModEventMask(stc.STC_MOD_INSERTTEXT | stc.STC_MOD_DELETETEXT | stc.STC_PERFORMED_USER | stc.STC_PERFORMED_UNDO | stc.STC_PERFORMED_REDO)
        self.Bind(stc.EVT_STC_CHANGE, self.on_change)
        self.Bind(stc.EVT_STC_UPDATEUI, self.on_updateui)
        self.Bind(stc.EVT_STC_CHARADDED, self.on_charadded)
        self.Bind(stc.EVT_STC_MARGINCLICK, self.on_marginclick)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
    def apply_settings(self):
        self.SetUseHorizontalScrollBar(settings.USE_HORIZONTAL_SCROLL_BAR)
        self.SetBackSpaceUnIndents(settings.BACKSPACE_UNINDENTS)
        self.SetEdgeColumn(settings.EDGE_COLUMN)
        self.SetEdgeMode(settings.EDGE_MODE)
        self.SetEndAtLastLine(settings.END_AT_LAST_LINE)
        self.SetIndentationGuides(settings.INDENTATION_GUIDES)
        self.SetTabIndents(settings.TAB_INDENTS)
        self.SetTabWidth(settings.TAB_WIDTH)
        self.SetUseTabs(settings.USE_TABS)
        self.SetViewWhiteSpace(settings.VIEW_WHITESPACE)
        self.SetMargins(settings.MARGIN_LEFT, settings.MARGIN_RIGHT)
        
        self.SetLexerLanguage(settings.LANGUAGE.lower())
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT, 'face:%s,size:%d' % (settings.FONT_FACE, settings.FONT_SIZE))
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT, 'face:%s,size:%d,bold,fore:#FF0000' % (settings.FONT_FACE, settings.FONT_SIZE+2))
        
        self.StyleSetSpec(stc.STC_P_CHARACTER, 'face:%s,size:%d,fore:grey' % (settings.FONT_FACE, settings.FONT_SIZE))
        self.StyleSetSpec(stc.STC_P_CLASSNAME, 'face:%s,size:%d,bold' % (settings.FONT_FACE, settings.FONT_SIZE))
        self.StyleSetSpec(stc.STC_P_COMMENTBLOCK, 'face:%s,size:%d' % (settings.FONT_FACE, settings.FONT_SIZE))
        self.StyleSetSpec(stc.STC_P_COMMENTLINE, 'face:%s,size:%d,fore:forest green' % (settings.FONT_FACE, settings.FONT_SIZE))
        self.StyleSetSpec(stc.STC_P_DEFAULT, 'face:%s,size:%d' % (settings.FONT_FACE, settings.FONT_SIZE))
        self.StyleSetSpec(stc.STC_P_DEFNAME, 'face:%s,size:%d,bold,fore:#ff00dc' % (settings.FONT_FACE, settings.FONT_SIZE))
        self.StyleSetSpec(stc.STC_P_IDENTIFIER, 'face:%s,size:%d' % (settings.FONT_FACE, settings.FONT_SIZE))
        self.StyleSetSpec(stc.STC_P_NUMBER, 'face:%s,size:%d,fore:red' % (settings.FONT_FACE, settings.FONT_SIZE))
        self.StyleSetSpec(stc.STC_P_OPERATOR, 'face:%s,size:%d,bold' % (settings.FONT_FACE, settings.FONT_SIZE))
        self.StyleSetSpec(stc.STC_P_STRING, 'face:%s,size:%d,fore:grey' % (settings.FONT_FACE, settings.FONT_SIZE))
        self.StyleSetSpec(stc.STC_P_STRINGEOL, 'face:%s,size:%d' % (settings.FONT_FACE, settings.FONT_SIZE))
        self.StyleSetSpec(stc.STC_P_TRIPLE, 'face:%s,size:%d,fore:#ff6a00' % (settings.FONT_FACE, settings.FONT_SIZE))
        self.StyleSetSpec(stc.STC_P_TRIPLEDOUBLE, 'face:%s,size:%d,fore:#ff6a00' % (settings.FONT_FACE, settings.FONT_SIZE))
        self.StyleSetSpec(stc.STC_P_WORD, 'face:%s,size:%d,bold,fore:#0000ee' % (settings.FONT_FACE, settings.FONT_SIZE))
        
        self.SetKeyWords(0, ' '.join(settings.PYTHON_KEYWORDS.split()))
        
        self.apply_bookmark_settings()
        self.apply_folding_settings()
    def apply_bookmark_settings(self):
        if settings.BOOKMARKS:
            self.SetMarginType(self.BOOKMARK_MARGIN, stc.STC_MARGIN_SYMBOL)
            self.SetMarginSensitive(self.BOOKMARK_MARGIN, True)
            self.SetMarginWidth(self.BOOKMARK_MARGIN, settings.BOOKMARK_MARGIN_SIZE)
        else:
            self.SetMarginSensitive(self.BOOKMARK_MARGIN, False)
            self.SetMarginWidth(self.BOOKMARK_MARGIN, 0)
    def apply_folding_settings(self):
        if settings.FOLDING:
            self.SetProperty("fold", "1")
            self.SetMarginType(self.FOLDING_MARGIN, stc.STC_MARGIN_SYMBOL)
            self.SetMarginMask(self.FOLDING_MARGIN, stc.STC_MASK_FOLDERS)
            self.SetMarginSensitive(self.FOLDING_MARGIN, True)
            self.SetMarginWidth(self.FOLDING_MARGIN, settings.FOLDING_MARGIN_SIZE)
            self.MarkerDefine(stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_BOXPLUSCONNECTED, "white", "#666666")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_BOXMINUSCONNECTED, "white", "#666666")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNER, "white", "#666666")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_LCORNER, "white", "#666666")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_VLINE, "white", "#666666")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDER, stc.STC_MARK_BOXPLUS, "white", "#666666")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_BOXMINUS, "white", "#666666")
        else:
            self.SetProperty("fold", "0")
            self.SetMarginSensitive(self.FOLDING_MARGIN, False)
            self.SetMarginWidth(self.FOLDING_MARGIN, 0)
    def open_file(self, path):
        file = None
        try:
            file = open(path, 'r')
            text = file.read()
            self.SetText(text)
            self.EmptyUndoBuffer()
            self.file_path = path
            self.detect_language()
        except IOError:
            self.SetText('')
        finally:
            if file:
                file.close()
            self.Colourise(0, self.GetLength())
    def save_file(self, path=None):
        path = path or self.file_path
        if not path:
            return False
        file = None
        try:
            file = open(path, 'w')
            text = self.GetText()
            file.write(text)
            self.file_path = path
            return True
        finally:
            if file:
                file.close()
        return False
    def detect_language(self):
        path = self.file_path
        if path:
            pre, ext = os.path.splitext(path)
            ext = ext.lower()
            if ext in EXTENSIONS:
                self.SetLexerLanguage(EXTENSIONS[ext])
                return
        self.SetLexer(stc.STC_LEX_AUTOMATIC)
    def match_brace(self):
        invalid = stc.STC_INVALID_POSITION
        if settings.MATCH_BRACES:
            for i in (1, 0):
                a = self.GetCurrentPos() - i
                b = self.BraceMatch(a)
                if b != invalid:
                    self.BraceHighlight(a, b)
                    return
        self.BraceHighlight(invalid, invalid)
    def show_line_numbers(self):
        if settings.LINE_NUMBERS:
            lines = self.GetLineCount()
            text = '%d ' % lines
            n = len(text)
            if n < 4: text += ' ' * (4-n)
            width = self.TextWidth(stc.STC_STYLE_LINENUMBER, text)
        else:
            width = 0
        self.SetMarginType(self.LINE_MARGIN, stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(self.LINE_MARGIN, width)
    def lower(self):
        text = self.GetSelectedText()
        self.ReplaceSelection(text.lower())
    def upper(self):
        text = self.GetSelectedText()
        self.ReplaceSelection(text.upper())
    def on_key_down(self, event):
        code = event.GetKeyCode()
        if code == wx.WXK_F3 and settings.USE_SELECTION_FOR_F3: # find next
            # TODO: EnsureVisible when Folding
            text = self.GetSelectedText()
            if text:
                start, end = self.GetSelection()
                for index in (end, 0):
                    index = self.FindText(index, self.GetLength(), text, 0)
                    if index >= 0:
                        self.SetSelection(index, index + len(text))
                        break
        event.Skip()
    def highlight_selection(self):
        self.IndicatorSetStyle(2, stc.STC_INDIC_ROUNDBOX)
        self.IndicatorSetForeground(2, wx.RED)
        self.StartStyling(0, stc.STC_INDIC2_MASK)
        self.SetStyling(self.GetLength(), 0)
        if not settings.HIGHLIGHT_SELECTION:
            return
        text = self.GetSelectedText()
        if not text or '\n' in text:
            return
        index = -1
        n = len(text)
        while True:
            index = self.FindText(index, self.GetLength(), text, stc.STC_FIND_WHOLEWORD|stc.STC_FIND_MATCHCASE)
            if index < 0: break
            self.StartStyling(index, stc.STC_INDIC2_MASK)
            self.SetStyling(n, stc.STC_INDIC2_MASK)
            index += 1
    def highlight_line(self):
        marker = 0
        self.MarkerDeleteAll(marker)
        if settings.HIGHLIGHT_LINE:
            line = self.GetCurrentLine()
            self.MarkerDefine(marker, stc.STC_MARK_BACKGROUND)
            self.MarkerSetBackground(marker, '#EEEEEE')
            self.MarkerAdd(line, marker)
    def on_change(self, event):
        pass
    def on_charadded(self, event):
        code = event.GetKey()
        if code == ord('\n'): # auto indent
            line = self.GetCurrentLine() - 1
            if line >= 0:
                text = self.GetLine(line)
                if False and text[:-2].isspace():
                    start = self.PositionFromLine(line)
                    end = start + self.LineLength(line) - 2
                    self.SetSelection(start, end)
                    self.ReplaceSelection('')
                    pos = self.PositionFromLine(line+1)
                    self.SetCurrentPos(pos)
                    self.SetSelection(pos, pos)
                else:
                    index = -1
                    for i, ch in enumerate(text):
                        if ch in (' ', '\t'):
                            index = i
                        else:
                            break
                    if index >= 0:
                        self.ReplaceSelection(text[:index+1])
    def on_marginclick(self, event):
        margin = event.GetMargin()
        line = self.LineFromPosition(event.GetPosition())
        if margin == self.BOOKMARK_MARGIN:
            marker = 1
            symbol = settings.BOOKMARK_SYMBOL
            self.MarkerDefine(marker, symbol)
            self.MarkerSetBackground(marker, 'light blue')
            if self.MarkerGet(line) & (1 << marker):
                self.MarkerDelete(line, marker)
            else:
                self.MarkerAdd(line, marker)
        if margin == self.FOLDING_MARGIN:
            self.ToggleFold(line)
    def on_updateui(self, event):
        self.match_brace()
        self.show_line_numbers()
        self.highlight_selection()
        self.highlight_line()
        
if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = wx.Frame(None, -1, 'Editor Control')
    control = EditorControl(frame, -1)
    frame.SetSize((800, 600))
    frame.Show()
    app.MainLoop()
    