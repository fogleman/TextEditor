import wx
import wx.stc as stc
import util

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
        self.font = None
        self.size = None
        self.bold = None
        self.italic = None
        self.underline = None
        self.foreground = None
        self.background = None
    def create_font(self):
        return create_font(self.font, self.size, self.bold, self.italic, self.underline)
    def create_foreground(self):
        return create_color(*self.foreground)
    def create_background(self):
        return create_color(*self.background)
        
        
        
def create_color(red, green, blue):
    return wx.Colour(red, green, blue)
    
def create_font(name, size, bold=False, italic=False, underline=False):
    weight = wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL
    style = wx.FONTSTYLE_ITALIC if italic else wx.FONTSTYLE_NORMAL
    font = wx.Font(size, wx.FONTFAMILY_DEFAULT, style, weight, underline, name)
    return font
    
def color_tuple(color):
    return color.Red(), color.Green(), color.Blue()
    
def font_tuple(font):
    bold = font.GetWeight() == wx.FONTWEIGHT_BOLD
    italic = font.GetStyle() == wx.FONTSTYLE_ITALIC
    underline = font.GetUnderlined()
    return font.GetFaceName(), font.GetPointSize(), bold, italic, underline
    
class StyleEvent(wx.PyEvent):
    def __init__(self, event_object, type):
        super(StyleEvent, self).__init__()
        self.SetEventType(type.typeId)
        self.SetEventObject(event_object)
        
EVT_STYLE_CHANGED = wx.PyEventBinder(wx.NewEventType())

class StyleControls(wx.Panel):
    def __init__(self, parent, style=None):
        super(StyleControls, self).__init__(parent, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.create_font_box(), 0, wx.EXPAND)
        sizer.AddSpacer(8)
        sizer.Add(self.create_style_box(), 0, wx.EXPAND)
        sizer.AddSpacer(8)
        sizer.Add(self.create_color_box(), 0, wx.EXPAND)
        self.SetSizer(sizer)
        self.controls = [
            self.font, self.size, self.bold, self.italic, self.underline, 
            self.foreground, self.background
        ]
        self.set_style(style)
    def set_style(self, style):
        self.style = style
        enable = bool(style)
        if enable:
            self.update_controls()
        for control in self.controls:
            control.Enable(enable)
    def on_event(self, event):
        self.update_style()
        wx.PostEvent(self, StyleEvent(self, EVT_STYLE_CHANGED))
    def update_style(self):
        style = self.style
        style.font = self.font.GetStringSelection()
        style.size = self.size.GetValue()
        style.bold = self.bold.GetValue()
        style.italic = self.italic.GetValue()
        style.underline = self.underline.GetValue()
        style.foreground = color_tuple(self.foreground.GetColour())
        style.background = color_tuple(self.background.GetColour())
    def update_controls(self):
        style = self.style
        fonts = self.font.GetStrings()
        if style.font in fonts:
            self.font.SetSelection(fonts.index(style.font))
        else:
            self.font.SetSelection(wx.NOT_FOUND)
        self.size.SetValue(style.size)
        self.bold.SetValue(style.bold)
        self.italic.SetValue(style.italic)
        self.underline.SetValue(style.underline)
        self.foreground.SetColour(create_color(*style.foreground))
        self.background.SetColour(create_color(*style.background))
    def create_font_box(self):
        grid = wx.FlexGridSizer(2, 2, 3, 10)
        grid.AddGrowableCol(0)
        grid.Add(wx.StaticText(self, -1, 'Font'))
        grid.Add(wx.StaticText(self, -1, 'Size'))
        font = wx.Choice(self, -1)
        font.Bind(wx.EVT_CHOICE, self.on_event)
        fonts = util.get_fonts()
        for f in fonts:
            font.Append(f)
        grid.Add(font, 0, wx.EXPAND)
        size = wx.SpinCtrl(self, -1, size=(60,-1), min=4, max=32)
        size.Bind(wx.EVT_SPINCTRL, self.on_event)
        grid.Add(size)
        self.font = font
        self.size = size
        return grid
    def create_style_box(self):
        box = wx.StaticBox(self, -1, 'Font Styles')
        sizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
        bold = wx.CheckBox(self, -1, 'Bold')
        bold.Bind(wx.EVT_CHECKBOX, self.on_event)
        sizer.Add(bold, 0, wx.ALL, 5)
        italic = wx.CheckBox(self, -1, 'Italic')
        italic.Bind(wx.EVT_CHECKBOX, self.on_event)
        sizer.Add(italic, 0, wx.ALL, 5)
        underline = wx.CheckBox(self, -1, 'Underline')
        underline.Bind(wx.EVT_CHECKBOX, self.on_event)
        sizer.Add(underline, 0, wx.ALL, 5)
        self.bold = bold
        self.italic = italic
        self.underline = underline
        return sizer
    def create_color_box(self):
        box = wx.StaticBox(self, -1, 'Font Colors')
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        grid = wx.FlexGridSizer(2, 3, 3, 10)
        grid.AddGrowableCol(2)
        grid.Add(wx.StaticText(self, -1, 'Foreground'))
        grid.Add(wx.StaticText(self, -1, 'Background'))
        grid.AddSpacer(0)
        foreground = wx.ColourPickerCtrl(self, -1, style=wx.CLRP_SHOW_LABEL)
        foreground.Bind(wx.EVT_COLOURPICKER_CHANGED, self.on_event)
        grid.Add(foreground, 0, wx.EXPAND)
        background = wx.ColourPickerCtrl(self, -1, style=wx.CLRP_SHOW_LABEL)
        background.Bind(wx.EVT_COLOURPICKER_CHANGED, self.on_event)
        grid.Add(background, 0, wx.EXPAND)
        grid.AddSpacer(0)
        sizer.Add(grid, 1, wx.EXPAND|wx.ALL, 5)
        self.foreground = foreground
        self.background = background
        return sizer
        
class StyleListBox(wx.VListBox):
    def __init__(self, parent, styles=None):
        super(StyleListBox, self).__init__(parent, -1, style=wx.BORDER_SUNKEN)
        self.pad = 6
        self.SetMinSize((200, 0))
        self.set_styles(styles)
    def set_styles(self, styles):
        styles = styles or []
        self.styles = styles
        self.SetItemCount(len(styles))
        self.SetSelection(0 if styles else wx.NOT_FOUND)
    def OnDrawBackground(self, dc, rect, index):
        if self.IsSelected(index):
            p = 3
            x, y, w, h = rect
            x, y, w, h = x+p, y+p, w-p*2, h-p*2
            dc.SetPen(wx.BLACK_PEN)
            dc.DrawRectangle(x, y, w, h)
    def OnDrawItem(self, dc, rect, index):
        style = self.styles[index]
        dc.SetFont(style.create_font())
        dc.SetBackgroundMode(wx.SOLID)
        dc.SetTextForeground(style.create_foreground())
        dc.SetTextBackground(style.create_background())
        p = self.pad
        x, y, w, h = rect
        x, y = x+p, y+p
        dc.DrawText(style.preview, x, y)
    def OnDrawSeparator(self, dc, rect, index):
        if index == 0:
            dc.SetPen(wx.Pen(wx.Colour(192, 192, 192)))
            x, y, w, h = rect
            x1, x2 = x, x+w
            y1 = y+h-1
            dc.DrawLine(x1, y1, x2, y1)
    def OnMeasureItem(self, index):
        style = self.styles[index]
        dc = wx.ClientDC(self)
        dc.SetFont(style.create_font())
        w, h = dc.GetTextExtent(style.preview)
        return h + self.pad * 2
        
class StylePanel(wx.Panel):
    def __init__(self, parent, styles=None):
        super(StylePanel, self).__init__(parent, -1)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        listbox = StyleListBox(self)
        listbox.Bind(wx.EVT_LISTBOX, self.on_listbox)
        sizer.Add(listbox, 1, wx.EXPAND|wx.ALL, 8)
        controls = StyleControls(self)
        controls.Bind(EVT_STYLE_CHANGED, self.on_style_changed)
        sizer.Add(controls, 0, wx.EXPAND|wx.ALL, 8)
        self.SetSizerAndFit(sizer)
        self.listbox = listbox
        self.controls = controls
        self.set_styles(styles)
    def set_styles(self, styles):
        self.listbox.set_styles(styles)
        self.controls.set_style(styles[0] if styles else None)
    def on_listbox(self, event):
        control = self.listbox
        index = control.GetSelection()
        style = control.styles[index] if index != wx.NOT_FOUND else None
        self.controls.set_style(style)
    def on_style_changed(self, event):
        self.listbox.Refresh()
        
        
        
class Frame(wx.Frame):
    def __init__(self):
        super(Frame, self).__init__(None, -1, 'Test')
        styles = create_styles()
        panel = StylePanel(self, styles)
        self.Fit()
        
def create_styles():
    root = Style(None, 0, 'Style', 'Style Preview', 
        'Bitstream Vera Sans Mono', 10, False, False, False, 
        (0,0,0), (255,255,255))
        
    python = Style(root, -1, 'Python Default')
    parent = python
    Style(parent, stc.STC_P_CHARACTER, 'Character')
    Style(parent, stc.STC_P_CLASSNAME, 'Class Name')
    Style(parent, stc.STC_P_COMMENTBLOCK, 'Comment Block')
    Style(parent, stc.STC_P_COMMENTLINE, 'Comment Line')
    Style(parent, stc.STC_P_DEFAULT, 'Whitespace')
    Style(parent, stc.STC_P_DEFNAME, 'Function Name')
    Style(parent, stc.STC_P_IDENTIFIER, 'Identifier')
    Style(parent, stc.STC_P_NUMBER, 'Number')
    Style(parent, stc.STC_P_OPERATOR, 'Operator')
    Style(parent, stc.STC_P_STRING, "String 'Example'")
    Style(parent, stc.STC_P_STRINGEOL, 'String EOL')
    Style(parent, stc.STC_P_TRIPLE, "String '''Example'''")
    Style(parent, stc.STC_P_TRIPLEDOUBLE, 'String """Example"""')
    Style(parent, stc.STC_P_WORD, 'Keyword')
    return [python] + sorted(python.children)
    
if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = Frame()
    frame.Show()
    app.MainLoop()
    