import wx
import wx.stc as stc

'''
Implemented
===========
View Whitespace
Auto-Indent
Tab Width
Spaces for Tabs
Smart Backspace
Indentation Guides
Scroll Past EOF
Syntax Highlighting
Show Line Numbers
Show Column Edge
Folding
Brace Matching
Find Next (by selection)
Highlight Selection
Highlight Current Line

Not Yet Implemented
===================
Mark All
Tabbed Interface
Load/Save Files
Printing
Indent Selection
Auto-Completion
Bookmarking
Options Dialog
Style Dialog
Menu Configuration Dialog
Unicode, etc.
Macro Recording
Execute/Run Script
Plugins
FTP Integration
SVN Integration?
Search
Search Files
Class/Function List/TOC
Task List
Line Ending Type

'''

KEYWORDS = \
'''
and       del       from      not       while
as        elif      global    or        with
assert    else      if        pass      yield
break     except    import    print
class     exec      in        raise
continue  finally   is        return
def       for       lambda    try
'''

class StyledTextCtrl(stc.StyledTextCtrl):
    def __init__(self, *args, **kwargs):
        super(StyledTextCtrl, self).__init__(*args, **kwargs)
        self.SetViewWhiteSpace(True)
        self.SetTabWidth(4)
        self.SetUseTabs(False)
        self.SetTabIndents(True)
        self.SetBackSpaceUnIndents(True)
        self.SetIndentationGuides(True)
        self.SetEndAtLastLine(False)
        self.SetLexer(stc.STC_LEX_PYTHON)
        self.SetProperty("fold", "1")
        #self.SetProperty("fold.comment.python", "1")
        #self.SetProperty("fold.quotes.python", "1")
        #self.SetProperty("tab.timmy.whinge.level", "0")
        self.SetKeyWords(0, ' '.join(KEYWORDS.split()))
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT, 'face:Bitstream Vera Sans Mono,size:10')
        self.StyleSetSpec(stc.STC_P_WORD, 'face:Bitstream Vera Sans Mono,size:10,bold,fore:#000099')
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT, 'face:Bitstream Vera Sans Mono,size:12,bold,fore:#FF0000')
        self.SetMarginType(2, stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(2, stc.STC_MASK_FOLDERS)
        self.SetMarginSensitive(2, True)
        self.SetMarginWidth(2, 11)
        self.SetMarginType(1, stc.STC_MARGIN_SYMBOL)
        #self.SetMarginWidth(1, 0)
        self.SetEdgeMode(stc.STC_EDGE_LINE)
        self.SetEdgeColumn(80)
        self.show_line_numbers()
        self.setup_folding_markers()
        self.Bind(stc.EVT_STC_UPDATEUI, self.on_updateui)
        self.Bind(stc.EVT_STC_CHARADDED, self.on_charadded)
        self.Bind(stc.EVT_STC_MARGINCLICK, self.on_marginclick)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
    def setup_folding_markers(self):
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_BOXPLUSCONNECTED, "white", "#666666")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_BOXMINUSCONNECTED, "white", "#666666")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNER, "white", "#666666")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_LCORNER, "white", "#666666")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_VLINE, "white", "#666666")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDER, stc.STC_MARK_BOXPLUS, "white", "#666666")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_BOXMINUS, "white", "#666666")
    def match_brace(self):
        invalid = stc.STC_INVALID_POSITION
        for i in (1, 0):
            a = self.GetCurrentPos() - i
            b = self.BraceMatch(a)
            if b != invalid:
                self.BraceHighlight(a, b)
                return
        self.BraceHighlight(invalid, invalid)
    def show_line_numbers(self):
        lines = self.GetLineCount()
        width = self.TextWidth(stc.STC_STYLE_LINENUMBER, '  %d'%lines)
        self.SetMarginType(0, stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(0, width)
    def on_key_down(self, event):
        code = event.GetKeyCode()
        if code == wx.WXK_F3: # find next
            # TODO: EnsureVisible
            text = self.GetSelectedText()
            if text:
                start, end = self.GetSelection()
                for index in (end, 0):
                    index = self.FindText(index, self.GetLength(), text, 0)
                    if index >= 0:
                        self.SetSelection(index, index + len(text))
                        break
        event.Skip()
    def highlight_occurrences(self):
        self.IndicatorSetStyle(2, stc.STC_INDIC_ROUNDBOX)
        self.IndicatorSetForeground(2, wx.RED)
        self.StartStyling(0, stc.STC_INDIC2_MASK)
        self.SetStyling(self.GetLength(), 0)
        text = self.GetSelectedText()
        if not text: return
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
        line = self.GetCurrentLine()
        self.MarkerDefine(marker, stc.STC_MARK_BACKGROUND)
        self.MarkerSetBackground(marker, '#EEEEEE')
        self.MarkerDeleteAll(marker)
        self.MarkerAdd(line, marker)
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
        if margin == 2:
            self.ToggleFold(line)
    def on_updateui(self, event):
        self.match_brace()
        self.show_line_numbers()
        self.highlight_occurrences()
        self.highlight_line()
        
if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = wx.Frame(None, -1, 'Scintilla')
    control = StyledTextCtrl(frame, -1)
    frame.SetSize((800, 600))
    frame.Show()
    app.MainLoop()
    