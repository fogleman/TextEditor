import wx
import wx.stc as stc
import util
from settings import settings

class Find(wx.Dialog):
    def __init__(self, parent, replace=False):
        super(Find, self).__init__(parent, -1, 'Replace' if replace else 'Find')
        self.replace = replace
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.create_controls(), 1, wx.EXPAND|wx.ALL, 10)
        sizer.Add(self.create_buttons(), 0, wx.EXPAND|wx.ALL&~wx.LEFT, 10)
        self.SetSizerAndFit(sizer)
        self.Bind(wx.EVT_ACTIVATE, self.on_activate)
        self.SetIcon(wx.IconFromBitmap(util.get_icon('find.png')))
        self.load_state()
    def get_control(self):
        return self.GetParent().notebook.get_window()
    def on_find(self, event, mark_all=False):
        text = self.input.GetValue()
        if self.extended.GetValue():
            text = self.convert_backslashes(text)
        flags = self.create_flags()
        control = self.get_control()
        previous = self.up.GetValue()
        wrap = self.wrap.GetValue()
        close = self.close.GetValue()
        if text and control:
            if mark_all:
                control.mark_text(text, flags)
            else:
                control.find(text, previous, wrap, flags, False)
        self.input.SetMark(-1, -1)
        self.input.SetFocus()
        self.save_state()
        if close:
            self.Close()
    def on_replace(self, event):
        control = self.get_control()
        selection = control.GetSelectedText()
        a, b = control.GetSelection()
        replacement = self.replacement.GetValue()
        if selection:
            # TODO: make smart, don't replace non-matching string
            control.ReplaceSelection(replacement)
        if self.up.GetValue():
            control.SetSelection(a, a)
        self.on_find(event)
    def on_replace_all(self, event):
        text = self.input.GetValue()
        if self.extended.GetValue():
            text = self.convert_backslashes(text)
        flags = self.create_flags()
        control = self.get_control()
        replacement = self.replacement.GetValue()
        control.replace_all(text, replacement, flags)
    def on_mark_all(self, event):
        self.on_find(event, mark_all=True)
    def convert_backslashes(self, text):
        text = text.replace(r'\n', '\n')
        text = text.replace(r'\r', '\r')
        text = text.replace(r'\t', '\t')
        text = text.replace(r'\f', '\f')
        text = text.replace(r'\a', '\a')
        text = text.replace(r'\b', '\b')
        text = text.replace(r'\v', '\v')
        text = text.replace(r'\\', '\\')
        text = text.replace(r'\"', '"')
        text = text.replace(r"\'", "'")
        return text
    def create_flags(self):
        flags = 0
        if self.whole_word.GetValue():
            flags |= stc.STC_FIND_WHOLEWORD
        if self.case.GetValue():
            flags |= stc.STC_FIND_MATCHCASE
        if self.regex.GetValue():
            flags |= stc.STC_FIND_REGEXP
        return flags
    def load_state(self):
        control = self.get_control()
        text = control.GetSelectedText()
        self.input.SetValue(text if text else settings.FIND_TEXT)
        for text in settings.FIND_HISTORY:
            self.input.Append(text)
        self.input.SetMark(-1, -1)
        if self.replace:
            self.replacement.SetValue(settings.REPLACE_TEXT)
            for text in settings.REPLACE_HISTORY:
                self.replacement.Append(text)
        self.whole_word.SetValue(settings.FIND_WHOLE_WORD)
        self.case.SetValue(settings.FIND_MATCH_CASE)
        self.normal.SetValue(settings.FIND_NORMAL)
        self.extended.SetValue(settings.FIND_EXTENDED)
        self.regex.SetValue(settings.FIND_REGEX)
        self.close.SetValue(settings.FIND_CLOSE_DIALOG)
        self.up.SetValue(not settings.FIND_DOWN)
        self.down.SetValue(settings.FIND_DOWN)
        self.wrap.SetValue(settings.FIND_WRAP)
    def save_state(self):
        text = self.input.GetValue()
        settings.FIND_TEXT = text
        settings.FIND_HISTORY = util.add_history(text, settings.FIND_HISTORY, 10)
        if self.replace:
            replacement = self.replacement.GetValue()
            settings.REPLACE_TEXT = replacement
            settings.REPLACE_HISTORY = util.add_history(replacement, settings.REPLACE_HISTORY, 10)
        settings.FIND_WHOLE_WORD = self.whole_word.GetValue()
        settings.FIND_MATCH_CASE = self.case.GetValue()
        settings.FIND_NORMAL = self.normal.GetValue()
        settings.FIND_EXTENDED = self.extended.GetValue()
        settings.FIND_REGEX = self.regex.GetValue()
        settings.FIND_CLOSE_DIALOG = self.close.GetValue()
        settings.FIND_DOWN = self.down.GetValue()
        settings.FIND_WRAP = self.wrap.GetValue()
    def on_activate(self, event):
        self.SetTransparent(255 if event.GetActive() else 128)
    def create_controls(self):
        search_controls = self.create_search_controls()
        options = self.create_options()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer((200, 0))
        sizer.Add(search_controls, 0, wx.EXPAND|wx.BOTTOM, 5)
        sizer.Add(options)
        return sizer
    def create_search_controls(self):
        label1 = wx.StaticText(self, -1, 'Find What:')
        self.input = wx.ComboBox(self, -1)
        self.input.SetFocus()
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer = wx.FlexGridSizer(2, 2, 5, 5)
        sizer.AddGrowableCol(1, 1)
        sizer.Add(label1, 0, wx.ALIGN_CENTRE_VERTICAL)
        sizer.Add(self.input, 1, wx.EXPAND)
        if self.replace:
            label2 = wx.StaticText(self, -1, 'Replace With:')
            self.replacement = wx.ComboBox(self, -1)
            sizer.Add(label2, 0, wx.ALIGN_CENTRE_VERTICAL)
            sizer.Add(self.replacement, 1, wx.EXPAND)
        return sizer
    def create_options(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.create_options1(), 0, wx.EXPAND)
        sizer.AddSpacer(5)
        sizer.Add(self.create_options3(), 0, wx.EXPAND)
        sizer.AddSpacer(5)
        sizer.Add(self.create_options2(), 0, wx.EXPAND)
        return sizer
    def create_options1(self):
        self.case = wx.CheckBox(self, -1, 'Match Case')
        self.whole_word = wx.CheckBox(self, -1, 'Match Whole Word')
        self.close = wx.CheckBox(self, -1, 'Close Dialog')
        box = wx.StaticBox(self, -1, 'Options')
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        sizer.Add(self.case, 0, wx.ALL, 5)
        sizer.Add(self.whole_word, 0, wx.ALL&~wx.TOP, 5)
        sizer.Add(self.close, 0, wx.ALL&~wx.TOP, 5)
        return sizer
    def create_options2(self):
        self.up = wx.RadioButton(self, -1, 'Up', style=wx.RB_GROUP)
        self.down = wx.RadioButton(self, -1, 'Down')
        self.wrap = wx.CheckBox(self, -1, 'Wrap')
        box = wx.StaticBox(self, -1, 'Direction')
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        sizer.Add(self.up, 0, wx.ALL, 5)
        sizer.Add(self.down, 0, wx.ALL&~wx.TOP, 5)
        sizer.Add(self.wrap, 0, wx.ALL&~wx.TOP, 5)
        return sizer
    def create_options3(self):
        self.normal = wx.RadioButton(self, -1, 'Normal', style=wx.RB_GROUP)
        self.extended = wx.RadioButton(self, -1, '\\n, \\t, etc.')
        self.regex = wx.RadioButton(self, -1, 'Regex')
        box = wx.StaticBox(self, -1, 'Mode')
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        sizer.Add(self.normal, 0, wx.ALL, 5)
        sizer.Add(self.regex, 0, wx.ALL&~wx.TOP, 5)
        sizer.Add(self.extended, 0, wx.ALL&~wx.TOP, 5)
        return sizer
    def create_buttons(self):
        find = util.button(self, 'Find Next', self.on_find)
        find.SetDefault()
        if self.replace:
            replace = util.button(self, 'Replace', self.on_replace)
            replace_all = util.button(self, 'Replace All', self.on_replace_all)
        mark_all = util.button(self, 'Mark All', self.on_mark_all)
        cancel = util.button(self, 'Cancel', id=wx.ID_CANCEL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(find)
        sizer.AddSpacer(5)
        if self.replace:
            sizer.Add(replace)
            sizer.AddSpacer(5)
            sizer.Add(replace_all)
            sizer.AddSpacer(5)
        sizer.Add(mark_all)
        sizer.AddSpacer(5)
        sizer.Add(cancel)
        return sizer
        
class GotoLine(wx.Panel):
    def __init__(self, parent, control):
        super(GotoLine, self).__init__(parent, -1)
        self.control = control
        count = control.GetLineCount()
        label = wx.StaticText(self, -1, 'Goto Line: (1 - %d)' % count)
        input = wx.TextCtrl(self, -1, style=wx.TE_PROCESS_ENTER)
        input.Bind(wx.EVT_TEXT, self.on_text)
        input.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer((150,0))
        sizer.Add(label, 0, wx.ALL, 5)
        sizer.Add(input, 0, wx.EXPAND|wx.ALL&~wx.TOP, 5)
        self.SetSizerAndFit(sizer)
    def on_text_enter(self, event):
        self.on_text(event)
        self.control.SetFocus()
    def on_text(self, event):
        value = event.GetEventObject().GetValue()
        control = self.control
        try:
            value = int(value)
            max = control.GetLineCount()
            if value > 0 and value <= max:
                pos = control.PositionFromLine(value-1)
                control.SetSelection(pos, pos)
        except:
            pass
            