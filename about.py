import wx
from settings import settings

class About(wx.Dialog):
    def __init__(self, parent):
        super(About, self).__init__(parent, -1, 'About %s' % settings.APP_NAME)
        sizer = wx.BoxSizer(wx.VERTICAL)
        bitmap = wx.Bitmap('images/about.png')
        bitmap = wx.StaticBitmap(self, -1, bitmap, style=wx.BORDER_STATIC)
        sizer.Add(bitmap, 0, wx.ALL, 5)
        self.SetSizerAndFit(sizer)
        