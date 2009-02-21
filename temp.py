import wx
import wx.aui as aui
import wx.stc as stc

class Frame(wx.Frame):
    def __init__(self):
        super(Frame, self).__init__(None, -1, 'Test')
        style = wx.BORDER_NONE
        style |= aui.AUI_NB_CLOSE_BUTTON
        style |= aui.AUI_NB_TAB_MOVE
        tabs = aui.AuiNotebook(self, -1, style=style)
        #tabs = wx.Notebook(self, -1)
        bmp = wx.Bitmap('icons/page.png')
        for i in range(1, 6):
            control = stc.StyledTextCtrl(tabs, -1)
            tabs.AddPage(control, 'Page %d' % i)
            tabs.SetPageBitmap(i-1, bmp)
        for child in tabs.GetChildren():
            if isinstance(child, aui.AuiTabCtrl):
                child.Bind(wx.EVT_LEFT_DCLICK, self.on_event)
        self.tabs = tabs
    def on_event(self, event):
        x, y = event.GetPosition()
        control = event.GetEventObject()
        if control.TabHitTest(x, y, None):
            tab = self.tabs.GetSelection()
            self.tabs.RemovePage(tab)
            
if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = Frame()
    frame.Show()
    app.MainLoop()
    