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

class EditorEvent(wx.PyEvent):
    def __init__(self, type, object=None):
        super(EditorEvent, self).__init__()
        self.SetEventType(type.typeId)
        self.SetEventObject(object)
        
EVT_EDITOR_STATUS_CHANGED = wx.PyEventBinder(wx.NewEventType())

class EditorControl(stc.StyledTextCtrl):
    LINE_MARGIN = 0
    BOOKMARK_MARGIN = 1
    FOLDING_MARGIN = 2
    def __init__(self, *args, **kwargs):
        super(EditorControl, self).__init__(*args, **kwargs)
        self.file_path = None
        self._edited = False
        self.apply_settings()
        self.SetEOLMode(stc.STC_EOL_LF)
        self.SetModEventMask(stc.STC_MOD_INSERTTEXT | stc.STC_MOD_DELETETEXT | stc.STC_PERFORMED_USER | stc.STC_PERFORMED_UNDO | stc.STC_PERFORMED_REDO)
        self.Bind(stc.EVT_STC_CHANGE, self.on_change)
        self.Bind(stc.EVT_STC_UPDATEUI, self.on_updateui)
        self.Bind(stc.EVT_STC_CHARADDED, self.on_charadded)
        self.Bind(stc.EVT_STC_MARGINCLICK, self.on_marginclick)
    def get_name(self):
        if self.file_path:
            pre, name = os.path.split(self.file_path)
            return name
        else:
            return '(Untitled)'
    def get_edited(self):
        return self._edited
    def set_edited(self, edited):
        if self._edited != edited:
            self._edited = edited
            wx.PostEvent(self, EditorEvent(EVT_EDITOR_STATUS_CHANGED, self))
    edited = property(get_edited, set_edited)
    def confirm_close(self, frame, can_veto=True):
        if self.edited and settings.CONFIRM_CLOSE_WITH_EDITS:
            name = self.file_path or self.get_name()
            style = wx.YES_NO | wx.YES_DEFAULT | wx.ICON_QUESTION
            if can_veto:
                style |= wx.CANCEL
            dialog = wx.MessageDialog(frame, 'Save changes to file "%s"?' % name, 'Save Changes?', style)
            result = dialog.ShowModal()
            if result == wx.ID_YES:
                frame.save(self)
            elif result == wx.ID_CANCEL:
                return False
        return True
    def apply_settings(self):
        self.SetCaretForeground(settings.CARET_FOREGROUND)
        self.SetCaretLineVisible(settings.CARET_LINE_VISIBLE)
        self.SetCaretLineBack(settings.CARET_LINE_BACKGROUND)
        self.SetCaretPeriod(settings.CARET_PERIOD)
        self.SetCaretWidth(settings.CARET_WIDTH)
        
        self.SetWrapMode(stc.STC_WRAP_WORD if settings.WORD_WRAP else stc.STC_WRAP_NONE)
        self.SetSelBackground(bool(settings.SELECTION_BACKGROUND), settings.SELECTION_BACKGROUND)
        self.SetSelForeground(bool(settings.SELECTION_FOREGROUND), settings.SELECTION_FOREGROUND)
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
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD, 'face:%s,size:%d,bold,fore:pink' % (settings.FONT_FACE, settings.FONT_SIZE+2))
        
        self.StyleSetSpec(stc.STC_P_CHARACTER, 'face:%s,size:%d,fore:grey' % (settings.FONT_FACE, settings.FONT_SIZE))
        self.StyleSetSpec(stc.STC_P_CLASSNAME, 'face:%s,size:%d,bold' % (settings.FONT_FACE, settings.FONT_SIZE))
        self.StyleSetSpec(stc.STC_P_COMMENTBLOCK, 'face:%s,size:%d' % (settings.FONT_FACE, settings.FONT_SIZE))
        self.StyleSetSpec(stc.STC_P_COMMENTLINE, 'face:%s,size:%d,fore:forest green' % (settings.FONT_FACE, settings.FONT_SIZE))
        self.StyleSetSpec(stc.STC_P_DEFAULT, 'face:%s,size:%d' % (settings.FONT_FACE, settings.FONT_SIZE))
        self.StyleSetSpec(stc.STC_P_DEFNAME, 'face:%s,size:%d,bold,fore:maroon' % (settings.FONT_FACE, settings.FONT_SIZE))
        self.StyleSetSpec(stc.STC_P_IDENTIFIER, 'face:%s,size:%d' % (settings.FONT_FACE, settings.FONT_SIZE))
        self.StyleSetSpec(stc.STC_P_NUMBER, 'face:%s,size:%d,fore:red' % (settings.FONT_FACE, settings.FONT_SIZE))
        self.StyleSetSpec(stc.STC_P_OPERATOR, 'face:%s,size:%d,bold,fore:navy' % (settings.FONT_FACE, settings.FONT_SIZE))
        self.StyleSetSpec(stc.STC_P_STRING, 'face:%s,size:%d,fore:grey' % (settings.FONT_FACE, settings.FONT_SIZE))
        self.StyleSetSpec(stc.STC_P_STRINGEOL, 'face:%s,size:%d' % (settings.FONT_FACE, settings.FONT_SIZE))
        self.StyleSetSpec(stc.STC_P_TRIPLE, 'face:%s,size:%d,fore:#ff6a00' % (settings.FONT_FACE, settings.FONT_SIZE))
        self.StyleSetSpec(stc.STC_P_TRIPLEDOUBLE, 'face:%s,size:%d,fore:#ff6a00' % (settings.FONT_FACE, settings.FONT_SIZE))
        self.StyleSetSpec(stc.STC_P_WORD, 'face:%s,size:%d,bold,fore:medium blue' % (settings.FONT_FACE, settings.FONT_SIZE))
        
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
            self.edited = False
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
        if not self.edited:
            return True
        file = None
        try:
            file = open(path, 'w')
            text = self.GetText()
            file.write(text)
            self.edited = False
            self.file_path = path
            self.detect_language()
            return True
        finally:
            if file:
                file.close()
            self.Colourise(0, self.GetLength())
        return False
    def reload_file(self):
        if self.file_path:
            self.open_file(self.file_path)
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
    def sort(self):
        text = self.GetSelectedText()
        lines = text.split('\n')
        lines.sort()
        self.ReplaceSelection('\n'.join(lines))
    def indent(self):
        self.CmdKeyExecute(stc.STC_CMD_TAB)
    def unindent(self):
        self.CmdKeyExecute(stc.STC_CMD_BACKTAB)
    def word_wrap(self):
        mode = self.GetWrapMode()
        if mode == stc.STC_WRAP_WORD:
            self.SetWrapMode(stc.STC_WRAP_NONE)
            return False
        else:
            self.SetWrapMode(stc.STC_WRAP_WORD)
            return True
    def find(self, text=None, previous=False, wrap=True, flags=0, use_selection=True):
        if use_selection and settings.USE_SELECTION_FOR_F3:
            text = self.GetSelectedText() or text
        if text:
            pos = self.GetSelectionStart() if previous else self.GetSelectionEnd()
            wrap_pos = self.GetLength() if previous else 0
            for index in (pos, wrap_pos):
                self.SetSelection(index, index)
                self.SearchAnchor()
                func = self.SearchPrev if previous else self.SearchNext
                if func(flags, text) >= 0:
                    break
                if not wrap:
                    break
            else:
                self.SetSelection(pos, pos)
            self.EnsureCaretVisible()
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
        start = self.GetSelectionStart()
        index = -1
        n = len(text)
        while True:
            index = self.FindText(index, self.GetLength(), text, stc.STC_FIND_WHOLEWORD|stc.STC_FIND_MATCHCASE)
            if index < 0: break
            if index != start:
                self.StartStyling(index, stc.STC_INDIC2_MASK)
                self.SetStyling(n, stc.STC_INDIC2_MASK)
            index += 1
    def on_change(self, event):
        self.edited = True
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
        
if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = wx.Frame(None, -1, 'Editor Control')
    control = EditorControl(frame, -1)
    frame.SetSize((800, 600))
    frame.Show()
    app.MainLoop()
    