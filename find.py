import wx

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
            