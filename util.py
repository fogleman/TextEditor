import wx

class BaseException(Exception):
    def __init__(self, message):
        if isinstance(message, list):
            self.messages = [msg for msg in message]
        else:
            self.messages = [message]
    def __str__(self):
        return '\n'.join(self.messages)
        
class FontEnumerator(wx.FontEnumerator):
    def __init__(self):
        super(FontEnumerator, self).__init__()
        self.fonts = []
        self.EnumerateFacenames(fixedWidthOnly=True)
    def OnFacename(self, name):
        self.fonts.append(name)
        return True
        
def get_font():
    preferred_fonts = [
        'Bitstream Vera Sans Mono',
        'Courier New',
        'Courier',
    ]
    enum = FontEnumerator()
    for font in preferred_fonts:
        if font in enum.fonts:
            return font
    return enum.fonts[0] if enum.fonts else None
    
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
    
def add_history(new_item, item_list, max_size):
    result = list(item_list)
    if new_item in result:
        result.remove(new_item)
    result.insert(0, new_item)
    if len(result) > max_size:
        result = result[:max_size]
    return result
    