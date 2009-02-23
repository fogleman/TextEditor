import wx

class BaseException(Exception):
    def __init__(self, message):
        if isinstance(message, list):
            self.messages = [msg for msg in message]
        else:
            self.messages = [message]
    def __str__(self):
        return '\n'.join(self.messages)
        
def get_icon(file):
    file = 'icons/%s' % file
    return wx.Bitmap(file)
    
def button(parent, label, func=None, id=-1):
    button = wx.Button(parent, id, label)
    if func:
        button.Bind(wx.EVT_BUTTON, func)
    return button
    
def menu_item(window, menu, label, func, icon=None, kind=wx.ITEM_NORMAL, toolbar=None):
    item = wx.MenuItem(menu, -1, label, kind=kind)
    if func:
        window.Bind(wx.EVT_MENU, func, id=item.GetId())
    if icon:
        item.SetBitmap(get_icon(icon))
    menu.AppendItem(item)
    if toolbar and icon:
        tool_item = toolbar.AddSimpleTool(-1, get_icon(icon), label)
        if func:
            window.Bind(wx.EVT_TOOL, func, id=tool_item.GetId())
    return item
    
def tool_item(window, toolbar, label, func, icon):
    item = toolbar.AddSimpleTool(-1, get_icon(icon), label)
    if func:
        window.Bind(wx.EVT_TOOL, func, id=item.GetId())
    return item
    
def abbreviate(text, length):
    n = len(text)
    if n <= length:
        return text
    half = (length - 3) / 2
    pre = text[:half]
    post = text[-half:]
    return '%s...%s' % (pre, post)
    