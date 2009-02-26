import wx
import wx.aui as aui
import wx.stc as stc
import os
import control
import util
from settings import settings

class NotebookEvent(wx.PyEvent):
    def __init__(self, type, object=None):
        super(NotebookEvent, self).__init__()
        self.SetEventType(type.typeId)
        self.SetEventObject(object)
        
EVT_NOTEBOOK_TAB_CLOSED = wx.PyEventBinder(wx.NewEventType())

class DropTarget(wx.FileDropTarget):
    def __init__(self, notebook):
        super(DropTarget, self).__init__()
        self.notebook = notebook
    def OnDropFiles(self, x, y, paths):
        for path in paths:
            self.notebook.create_tab(path)
        return True
        
class Notebook(aui.AuiNotebook):
    def __init__(self, parent):
        style = wx.BORDER_NONE
        style |= aui.AUI_NB_TAB_MOVE
        style |= aui.AUI_NB_TAB_SPLIT
        style |= settings.AUI_NB_CLOSE
        style |= settings.AUI_NB_POSITION
        if settings.AUI_NB_TAB_FIXED_WIDTH:
            style |= aui.AUI_NB_TAB_FIXED_WIDTH
        if settings.AUI_NB_SCROLL_BUTTONS:
            style |= aui.AUI_NB_SCROLL_BUTTONS
        if settings.AUI_NB_WINDOWLIST_BUTTON:
            style |= aui.AUI_NB_WINDOWLIST_BUTTON
            
        super(Notebook, self).__init__(parent, -1, style=style)
        self._tab_controls = {}
        self._tab_order = []
        self._right_up_position = (0, 0)
        self.SetDropTarget(DropTarget(self))
        self.SetUniformBitmapSize((21, 21))
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.on_page_close)
        self.Bind(aui.EVT_AUINOTEBOOK_DRAG_DONE, self.on_drag_done)
        self.Bind(aui.EVT_AUINOTEBOOK_END_DRAG, self.on_end_drag)
    def on_end_drag(self, event):
        event.Skip()
        self.bind_tab_control()
        wx.CallAfter(self.check_tabs)
    def check_tabs(self):
        result = []
        for control in self._tab_controls.keys():
            if not control:
                del self._tab_controls[control]
                continue
            tab_order = []
            count = control.GetPageCount()
            for i in range(count):
                window = control.GetPage(i).window
                index = self.GetPageIndex(window)
                tab_order.append(index)
            self._tab_controls[control] = tab_order
            result.extend(tab_order)
        self._tab_order = result
    def on_drag_done(self, event):
        event.Skip()
        self.bind_tab_control()
    def on_page_close(self, event):
        event.Veto()
        index = event.GetSelection()
        self.close_tab(index)
    def is_tab(self, event):
        x, y = event.GetPosition()
        control = event.GetEventObject()
        return control.TabHitTest(x, y, None)
    def on_right_up(self, event):
        event.Skip()
        self._right_up_position = event.GetPosition()
    def on_tab_right_up(self, event):
        order = self._tab_controls[event.GetEventObject()]
        index = order[event.GetSelection()]
        if index == self.GetSelection():
            frame = self.GetParent()
            menu = frame.create_tab_menu()
            event.GetEventObject().PopupMenu(menu, self._right_up_position)
    def on_tab_right_down(self, event):
        order = self._tab_controls[event.GetEventObject()]
        index = order[event.GetSelection()]
        self.SetSelection(index)
    def on_left_dclick(self, event):
        if self.is_tab(event):
            if settings.CLOSE_TAB_ON_DOUBLE_CLICK:
                self.close_tab()
        else:
            if settings.CREATE_TAB_ON_DOUBLE_CLICK:
                self.create_tab()
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
        for child in self.GetChildren():
            if child in self._tab_controls:
                continue
            if isinstance(child, aui.AuiTabCtrl):
                child.Bind(wx.EVT_LEFT_DCLICK, self.on_left_dclick)
                child.Bind(wx.EVT_RIGHT_UP, self.on_right_up)
                child.Bind(aui.EVT_AUINOTEBOOK_TAB_RIGHT_UP, self.on_tab_right_up)
                child.Bind(aui.EVT_AUINOTEBOOK_TAB_RIGHT_DOWN, self.on_tab_right_down)
                self._tab_controls[child] = []
    def get_open_files(self):
        files = [window.file_path for window in self.get_ordered_windows()]
        files = [file for file in files if file]
        return files
    def save_state(self):
        files = self.get_open_files()
        settings.OPEN_FILES = files if settings.REMEMBER_OPEN_FILES else []
        settings.ACTIVE_TAB = self.GetSelection() #TODO: use tab order
    def load_state(self):
        if settings.OPEN_FILES:
            for file in settings.OPEN_FILES:
                self.create_tab(file)
            for index in (settings.ACTIVE_TAB, 0):
                if index >= 0 and index < self.GetPageCount():
                    self.SetSelection(index)
                    self.get_window(index).SetFocus()
                    break
        else:
            self.create_tab()
    def recent_path(self, path):
        if path:
            settings.RECENT_FILES = util.add_history(path, settings.RECENT_FILES, settings.RECENT_FILES_SIZE)
    def close_untitled_tab(self):
        windows = self.get_windows()
        if len(windows) == 1:
            window = windows[0]
            if not window.file_path and not window.edited and not window.GetText():
                self.close_tab(create_untitled=False)
    def create_tab(self, path=None):
        if path:
            path = os.path.abspath(path)
            for window in self.get_windows():
                if not window.file_path:
                    continue
                p1 = os.path.normcase(path)
                p2 = os.path.normcase(window.file_path)
                if p1 == p2:
                    window.SetFocus()
                    return
        self.Freeze()
        if path:
            self.close_untitled_tab()
        widget = control.EditorControl(self, -1, style=wx.BORDER_NONE)
        widget.SetDropTarget(DropTarget(self))
        if path:
            widget.open_file(path)
        widget.Bind(control.EVT_EDITOR_STATUS_CHANGED, self.on_status_changed)
        self.AddPage(widget, widget.get_name(), True, util.get_icon('page.png'))
        widget.SetFocus()
        self.bind_tab_control()
        self.recent_path(path)
        self.check_tabs()
        self.Thaw()
    def close_tab(self, index=None, create_untitled=True):
        self.Freeze()
        if index is None: index = self.GetSelection()
        if index >= 0:
            window = self.get_window(index)
            if window.confirm_close(True):
                self.recent_path(window.file_path)
                self.DeletePage(index)
                wx.PostEvent(self, NotebookEvent(EVT_NOTEBOOK_TAB_CLOSED, self))
        if self.GetPageCount() == 0 and create_untitled:
            self.create_tab()
        self.check_tabs()
        self.Thaw()
    def close_tabs(self):
        n = self.GetPageCount()
        for i in range(n):
            self.close_tab(0)
    def close_other_tabs(self):
        n = self.GetPageCount()
        index = self.GetSelection()
        before = index
        after = n - index - 1
        for i in range(before):
            self.close_tab(0)
        for i in range(after):
            self.close_tab(1)
    def next_tab(self):
        index = self.GetSelection()
        order = self._tab_order
        if index in order:
            i = order.index(index)
            n = len(order)
            self.SetSelection(order[(i+1)%n])
    def previous_tab(self):
        index = self.GetSelection()
        order = self._tab_order
        if index in order:
            i = order.index(index)
            n = len(order)
            self.SetSelection(order[(i+n-1)%n])
    def get_window(self, index=None):
        if index is None: index = self.GetSelection()
        return self.GetPage(index) if index >= 0 else None
    def get_windows(self):
        n = self.GetPageCount()
        return [self.get_window(i) for i in range(n)]
    def get_ordered_windows(self):
        windows = self.get_windows()
        order = self._tab_order
        return [windows[i] for i in order]
    def get_tab_name(self, index=None):
        if index is None: index = self.GetSelection()
        return self.GetPageText(index) if index >= 0 else None
    def update_tab_name(self, tab):
        index = self.GetPageIndex(tab)
        if index >= 0:
            self.SetPageText(index, tab.get_name())
    def get_title(self):
        title = None
        if settings.FULL_PATH_IN_TITLE:
            window = self.get_window()
            if window:
                title = window.file_path
        title = title or self.get_tab_name()
        return title
        