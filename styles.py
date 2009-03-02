import wx
import wx.stc as stc
import copy
import pickle
import default_styles
import util

STYLE_PATH = 'styles.dat'

class StyleManager(object):
    instance = None
    def __init__(self):
        assert StyleManager.instance is None
        StyleManager.instance = self
        self.init()
    def init(self):
        try:
            file = open(STYLE_PATH, 'rb')
            styles = pickle.load(file)
            file.close()
        except:
            styles = default_styles.create_style_tree()
        self.styles = styles
    def save_styles(self):
        try:
            file = open(STYLE_PATH, 'wb')
            pickle.dump(self.styles, file, -1)
            file.close()
        except:
            pass
            
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
        style = self.style
        object = event.GetEventObject()
        if object == self.font: style.font = self.font.GetStringSelection()
        if object == self.size: style.size = self.size.GetValue()
        if object == self.bold: style.bold = self.bold.GetValue()
        if object == self.italic: style.italic = self.italic.GetValue()
        if object == self.underline: style.underline = self.underline.GetValue()
        if object == self.foreground: style.foreground = color_tuple(self.foreground.GetColour())
        if object == self.background: style.background = color_tuple(self.background.GetColour())
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
        if not style: return
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
        self.Freeze()
        self.SetItemCount(len(styles))
        self.SetSelection(0 if styles else wx.NOT_FOUND)
        self.Refresh()
        self.Update()
        self.Thaw()
    def reset(self):
        index = self.GetSelection()
        if index != wx.NOT_FOUND:
            style = self.styles[index]
            style.clear()
        self.Refresh()
    def reset_all(self):
        for style in self.styles:
            style.clear()
        self.Refresh()
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
        if False:
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
        sizer.Add(listbox, 1, wx.EXPAND)
        sizer.AddSpacer(10)
        right = wx.BoxSizer(wx.VERTICAL)
        controls = StyleControls(self)
        controls.Bind(EVT_STYLE_CHANGED, self.on_style_changed)
        right.Add(controls, 0, wx.EXPAND)
        right.AddSpacer(8)
        right.Add(self.create_button_box(), 0, wx.EXPAND)
        sizer.Add(right, 0, wx.EXPAND)
        self.SetSizerAndFit(sizer)
        self.listbox = listbox
        self.controls = controls
        self.set_styles(styles)
    def set_styles(self, styles):
        self.listbox.set_styles(styles)
        self.controls.set_style(styles[0] if styles else None)
    def update_controls(self):
        self.controls.update_controls()
    def on_listbox(self, event):
        control = self.listbox
        index = control.GetSelection()
        style = control.styles[index] if index != wx.NOT_FOUND else None
        self.controls.set_style(style)
    def on_style_changed(self, event):
        self.listbox.Refresh()
    def on_reset(self, event):
        self.listbox.reset()
        self.controls.update_controls()
    def on_reset_all(self, event):
        self.listbox.reset_all()
        self.controls.update_controls()
    def create_button_box(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddStretchSpacer(1)
        reset = wx.Button(self, -1, 'Reset')
        reset.Bind(wx.EVT_BUTTON, self.on_reset)
        sizer.Add(reset)
        sizer.AddSpacer(8)
        reset_all = wx.Button(self, -1, 'Reset All')
        reset_all.Bind(wx.EVT_BUTTON, self.on_reset_all)
        sizer.Add(reset_all)
        return sizer
        
class LanguageStyles(wx.Panel):
    def __init__(self, parent, root):
        super(LanguageStyles, self).__init__(parent, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        top = wx.BoxSizer(wx.HORIZONTAL)
        top.Add(wx.StaticText(self, -1, 'Language:'), 0, wx.ALIGN_CENTRE_VERTICAL)
        top.AddSpacer(4)
        languages = wx.Choice(self, -1)
        languages.Bind(wx.EVT_CHOICE, self.on_choice)
        top.Add(languages)
        top.AddSpacer(4)
        line = wx.StaticLine(self, -1, size=(0,2), style=wx.LI_HORIZONTAL)
        top.Add(line, 1, wx.ALIGN_CENTRE_VERTICAL)
        sizer.Add(top, 0, wx.EXPAND)
        sizer.AddSpacer(8)
        panel = StylePanel(self)
        sizer.Add(panel, 1, wx.EXPAND)
        self.SetSizerAndFit(sizer)
        self.languages = languages
        self.panel = panel
        self.set_root(root)
    def set_root(self, root):
        self.root = root
        languages = list(root.children)
        languages.sort()
        control = self.languages
        control.Clear()
        for language in languages:
            control.Append(language.name, language)
        if languages:
            control.SetSelection(0)
        self.on_choice(None)
    def update_controls(self):
        self.panel.controls.update_controls()
    def on_choice(self, event):
        control = self.languages
        index = control.GetSelection()
        language = control.GetClientData(index) if index != wx.NOT_FOUND else None
        styles = list(language.children) if language else []
        styles.sort()
        if styles:
            styles = [language] + styles
        self.panel.set_styles(styles)
        
class StyleDialog(wx.Dialog):
    def __init__(self, parent):
        super(StyleDialog, self).__init__(parent, -1, 'Style Configuration')
        styles = StyleManager.instance.styles
        self.styles = copy.deepcopy(styles)
        sizer = wx.BoxSizer(wx.VERTICAL)
        notebook = wx.Notebook(self, -1)
        notebook.AddPage(self.create_global_page(notebook), 'Global Style')
        notebook.AddPage(self.create_app_page(notebook), 'Application Styles')
        notebook.AddPage(self.create_language_page(notebook), 'Language Styles')
        sizer.Add(notebook, 1, wx.EXPAND|wx.ALL, 8)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        buttons.AddStretchSpacer(1)
        ok = wx.Button(self, wx.ID_OK, 'OK')
        ok.Bind(wx.EVT_BUTTON, self.on_apply)
        cancel = wx.Button(self, wx.ID_CANCEL, 'Cancel')
        apply = wx.Button(self, wx.ID_APPLY, 'Apply')
        apply.Disable()
        apply.Bind(wx.EVT_BUTTON, self.on_apply)
        buttons.Add(ok, 0, wx.LEFT, 5)
        buttons.Add(cancel, 0, wx.LEFT, 5)
        buttons.Add(apply, 0, wx.LEFT, 5)
        sizer.Add(buttons, 0, wx.EXPAND|wx.ALL&~wx.TOP, 8)
        self.SetSizerAndFit(sizer)
        self.apply = apply
    def on_change(self, event):
        event.Skip()
        self.apply.Enable()
    def on_global_change(self, event):
        self.on_change(event)
        self.app_controls.update_controls()
        self.language_controls.update_controls()
    def on_app_change(self, event):
        self.on_change(event)
        self.global_controls.update_controls()
        self.language_controls.update_controls()
    def on_language_change(self, event):
        self.on_change(event)
        self.global_controls.update_controls()
        self.app_controls.update_controls()
    def on_apply(self, event):
        event.Skip()
        self.apply.Disable()
        StyleManager.instance.styles = copy.deepcopy(self.styles)
        StyleManager.instance.save_styles()
    def create_global_page(self, parent):
        page = wx.Panel(parent, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        controls = StyleControls(page, self.styles)
        controls.Bind(EVT_STYLE_CHANGED, self.on_global_change)
        sizer.Add(controls, 1, wx.EXPAND|wx.ALL, 10)
        page.SetSizer(sizer)
        self.global_controls = controls
        return page
    def create_app_page(self, parent):
        page = wx.Panel(parent, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        styles = list(self.styles.get_child(0).children)
        controls = StylePanel(page, styles)
        controls.controls.Bind(EVT_STYLE_CHANGED, self.on_app_change)
        sizer.Add(controls, 1, wx.EXPAND|wx.ALL, 10)
        page.SetSizer(sizer)
        self.app_controls = controls
        return page
    def create_language_page(self, parent):
        page = wx.Panel(parent, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        styles = self.styles
        controls = LanguageStyles(page, styles)
        controls.panel.controls.Bind(EVT_STYLE_CHANGED, self.on_language_change)
        sizer.Add(controls, 1, wx.EXPAND|wx.ALL, 10)
        page.SetSizer(sizer)
        self.language_controls = controls
        return page
        
        
        
if __name__ == '__main__':
    app = wx.PySimpleApp()
    StyleManager()
    dialog = StyleDialog(None)
    dialog.ShowModal()
    dialog.Destroy()
    app.MainLoop()
    