import wx
import wx.aui as aui
import wx.stc as stc
import os
import control
import util
from settings import settings

class Notebook(aui.AuiNotebook):
    def __init__(self, parent):
        style = wx.BORDER_NONE | aui.AUI_NB_CLOSE_BUTTON | aui.AUI_NB_TAB_MOVE | aui.AUI_NB_SCROLL_BUTTONS | aui.AUI_NB_WINDOWLIST_BUTTON
        super(Notebook, self).__init__(parent, -1, style=style)
        self.SetUniformBitmapSize((21, 21))
    def on_left_dclick(self, event):
        x, y = event.GetPosition()
        control = event.GetEventObject()
        if control.TabHitTest(x, y, None):
            if settings.CLOSE_TAB_ON_DOUBLE_CLICK:
                self.close_tab()
    def on_status_changed(self, event):
        tab = event.GetEventObject()
        if tab.edited:
            icon = 'page_red.png'
        else:
            icon = 'page.png'
        index = self.GetPageIndex(tab)
        if index >= 0:
            self.SetPageBitmap(index, util.get_icon(icon))
    def bind_tab_control(self):
        if hasattr(self, '_bound'): return
        for child in self.GetChildren():
            if isinstance(child, aui.AuiTabCtrl):
                child.Bind(wx.EVT_LEFT_DCLICK, self.on_left_dclick)
                self._bound = True
    def save_state(self):
        files = [window.file_path for window in self.get_windows()]
        files = [file for file in files if file]
        settings.OPEN_FILES = files if settings.REMEMBER_OPEN_FILES else []
    def load_state(self):
        if settings.OPEN_FILES:
            for file in settings.OPEN_FILES:
                self.create_tab(file)
        else:
            self.create_tab()
    def create_tab(self, path=None):
        if path:
            for window in self.get_windows():
                if window.file_path == path:
                    window.SetFocus()
                    return
        widget = control.EditorControl(self, -1, style=wx.BORDER_NONE)
        name = '(Untitled)'
        if path:
            widget.open_file(path)
            pre, name = os.path.split(path)
        widget.Bind(control.EVT_EDITOR_STATUS_CHANGED, self.on_status_changed)
        self.AddPage(widget, name, True, util.get_icon('page.png'))
        widget.SetFocus()
        self.bind_tab_control()
    def close_tab(self, index=None):
        if index is None: index = self.GetSelection()
        if index >= 0:
            window = self.get_window(index)
            self.RemovePage(index)
            window.Destroy()
        if self.GetPageCount() == 0:
            self.create_tab()
    def close_tabs(self):
        n = self.GetPageCount()
        for i in range(n):
            self.close_tab(0)
    def get_window(self, index=None):
        if index is None: index = self.GetSelection()
        return self.GetPage(index) if index >= 0 else None
    def get_windows(self):
        n = self.GetPageCount()
        return [self.get_window(i) for i in range(n)]
    def get_tab_name(self, index=None):
        if index is None: index = self.GetSelection()
        return self.GetPageText(index) if index >= 0 else None
    def get_title(self):
        title = None
        if settings.FULL_PATH_IN_TITLE:
            window = self.get_window()
            if window:
                title = window.file_path
        title = title or self.get_tab_name()
        return title
        