import wx
import wx.aui as aui
import wx.stc as stc
import os
import control
import notebook
import util
from settings import settings

APP_NAME = 'Text Editor'

class Frame(wx.Frame):
    def __init__(self, parent=None, title=APP_NAME):
        super(Frame, self).__init__(parent, -1, title)
        manager = aui.AuiManager(self)
        self.manager = manager
        self.create_menu()
        self.create_statusbar()
        self.create_notebook()
        self.create_toolbars()
        manager.Update()
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.SetIcon(wx.IconFromBitmap(util.get_icon('page_edit.png')))
        self.load_state()
        self.notebook.load_state()
        self.rebuild_file_menu()
    def set_default_size(self):
        w = wx.SystemSettings_GetMetric(wx.SYS_SCREEN_X)
        h = wx.SystemSettings_GetMetric(wx.SYS_SCREEN_Y)
        wr, hr = 1, 1
        pad = min(w/8, h/8)
        n = min((w-pad)/wr, (h-pad)/hr)
        size = (n*wr, n*hr)
        self.SetSize(size)
    def save_state(self):
        if settings.MAIN_WINDOW_PERSISTED:
            if self.IsMaximized():
                settings.MAIN_WINDOW_MAXIMIZED = True
            else:
                settings.MAIN_WINDOW_MAXIMIZED = False
                settings.MAIN_WINDOW_SIZE = self.GetSize()
                settings.MAIN_WINDOW_POSITION = self.GetPosition()
    def load_state(self):
        if settings.MAIN_WINDOW_PERSISTED:
            self.set_default_size()
            self.Centre()
            self.SetSize(settings.MAIN_WINDOW_SIZE)
            self.SetPosition(settings.MAIN_WINDOW_POSITION)
            self.Maximize(settings.MAIN_WINDOW_MAXIMIZED)
    def create_notebook(self):
        tabs = notebook.Notebook(self)
        self.notebook = tabs
        tabs.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.on_tab_changed)
        tabs.Bind(notebook.EVT_NOTEBOOK_TAB_CLOSED, self.on_tab_closed)
        info = aui.AuiPaneInfo()
        info.CentrePane()
        info.PaneBorder(False)
        self.manager.AddPane(tabs, info)
    def create_toolbars(self):
        info = aui.AuiPaneInfo()
        info.ToolbarPane()
        info.LeftDockable(False)
        info.RightDockable(False)
        info.PaneBorder(False)
        info.Top()
        toolbar = self.create_main_toolbar()
        self.manager.AddPane(toolbar, info)
    def rebuild_file_menu(self):
        self.GetMenuBar().Replace(0, self.create_file_menu(), '&File')
    def create_file_menu(self):
        file = wx.Menu()
        util.menu_item(self, file, '&New\tCtrl+N', self.on_new, 'page.png')
        util.menu_item(self, file, '&Open...\tCtrl+O', self.on_open, 'folder_page.png')
        util.menu_item(self, file, '&Save\tCtrl+S', self.on_save, 'disk.png')
        util.menu_item(self, file, '&Save As...\tCtrl+Shift+S', self.on_save_as, 'blank.png')
        util.menu_item(self, file, 'Save All', self.on_save_all, 'disk_multiple.png')
        file.AppendSeparator()
        util.menu_item(self, file, 'Close\tCtrl+F4', self.on_close_tab, 'page_delete.png')
        util.menu_item(self, file, 'Close All\tCtrl+Shift+F4', self.on_close_tabs, 'blank.png')
        file.AppendSeparator()
        #util.menu_item(self, file, 'Reload', self.on_event, 'arrow_refresh_small.png')
        #util.menu_item(self, file, 'Rename...', self.on_event, 'drive_edit.png')
        #util.menu_item(self, file, 'Delete From Disk', self.on_event, 'cross.png')
        #file.AppendSeparator()
        util.menu_item(self, file, 'Print...\tCtrl+P', self.on_event, 'printer.png')
        file.AppendSeparator()
        recent_files = self.get_recent_files()
        if recent_files:
            for path in recent_files:
                text = util.abbreviate(path, 60)
                item = util.menu_item(self, file, text, self.on_open_recent, 'blank.png')
                item.SetHelp(path)
            file.AppendSeparator()
            util.menu_item(self, file, 'Open All Recent Documents', self.on_open_all_recent, 'folder_star.png')
            util.menu_item(self, file, 'Clear Recent Documents', self.on_clear_recent, 'blank.png')
            file.AppendSeparator()
        util.menu_item(self, file, '&Exit\tAlt+F4', self.on_exit, 'door_out.png')
        return file
    def get_recent_files(self):
        result = []
        if hasattr(self, 'notebook'):
            open_files = set(self.notebook.get_open_files())
            recent_files = set(settings.RECENT_FILES)
            displayed_files = recent_files - open_files
            if displayed_files:
                count = 0
                for path in settings.RECENT_FILES:
                    if path not in displayed_files:
                        continue
                    result.append(path)
                    count += 1
                    if count >= settings.RECENT_FILES_DISPLAY:
                        break
        return result
    def create_menu(self):
        menubar = wx.MenuBar()
        
        file = self.create_file_menu()
        menubar.Append(file, '&File')
        
        edit = wx.Menu()
        util.menu_item(self, edit, '&Undo\tCtrl+Z', self.on_undo, 'arrow_undo.png')
        util.menu_item(self, edit, '&Redo\tCtrl+Y', self.on_redo, 'arrow_redo.png')
        edit.AppendSeparator()
        util.menu_item(self, edit, 'Cut\tCtrl+X', self.on_cut, 'cut.png')
        util.menu_item(self, edit, 'Copy\tCtrl+C', self.on_copy, 'page_copy.png')
        util.menu_item(self, edit, 'Paste\tCtrl+V', self.on_paste, 'paste_plain.png')
        util.menu_item(self, edit, 'Delete\tDel', self.on_delete, 'delete.png')
        edit.AppendSeparator()
        util.menu_item(self, edit, 'Select All\tCtrl+A', self.on_select_all, 'table_go.png')
        edit.AppendSeparator()
        util.menu_item(self, edit, 'Sort', self.on_sort, 'arrow_down.png')
        util.menu_item(self, edit, 'Lowercase', self.on_lowercase, 'text_lowercase.png')
        util.menu_item(self, edit, 'Uppercase', self.on_uppercase, 'text_uppercase.png')
        menubar.Append(edit, '&Edit')
        
        search = wx.Menu()
        util.menu_item(self, search, 'Find...\tCtrl+F', self.on_event, 'find.png')
        util.menu_item(self, search, 'Find Next\tF3', self.on_find_next, 'page_white_put.png')
        util.menu_item(self, search, 'Find Previous\tCtrl+F3', self.on_event, 'page_white_get.png')
        util.menu_item(self, search, 'Find In Files...\tCtrl+Shift+F', self.on_event, 'magnifier.png')
        util.menu_item(self, search, 'Replace...\tCtrl+H', self.on_event, 'text_replace.png')
        util.menu_item(self, search, 'Goto Line...\tCtrl+G', self.on_event, 'text_linespacing.png')
        menubar.Append(search, '&Search')
        
        view = wx.Menu()
        util.menu_item(self, view, 'Next Tab\tCtrl+Tab', self.on_next_tab, 'arrow_right.png')
        util.menu_item(self, view, 'Previous Tab\tCtrl+Shift+Tab', self.on_previous_tab, 'arrow_left.png')
        menubar.Append(view, '&View')
        
        tools = wx.Menu()
        menubar.Append(tools, '&Tools')
        
        help = wx.Menu()
        menubar.Append(help, '&Help')
        
        self.SetMenuBar(menubar)
    def create_main_toolbar(self):
        toolbar = wx.ToolBar(self, -1, style=wx.TB_HORIZONTAL|wx.TB_FLAT|wx.TB_NODIVIDER)
        toolbar.SetToolBitmapSize((18,18))
        util.tool_item(self, toolbar, 'New Document', self.on_new, 'page.png')
        util.tool_item(self, toolbar, 'Open Document', self.on_open, 'folder_page.png')
        util.tool_item(self, toolbar, 'Save Document', self.on_save, 'disk.png')
        util.tool_item(self, toolbar, 'Save All Documents', self.on_save_all, 'disk_multiple.png')
        util.tool_item(self, toolbar, 'Close Document', self.on_close_tab, 'page_delete.png')
        toolbar.AddSeparator()
        util.tool_item(self, toolbar, 'Undo', self.on_undo, 'arrow_undo.png')
        util.tool_item(self, toolbar, 'Redo', self.on_redo, 'arrow_redo.png')
        toolbar.AddSeparator()
        util.tool_item(self, toolbar, 'Cut', self.on_cut, 'cut.png')
        util.tool_item(self, toolbar, 'Copy', self.on_copy, 'page_copy.png')
        util.tool_item(self, toolbar, 'Paste', self.on_paste, 'paste_plain.png')
        toolbar.AddSeparator()
        util.tool_item(self, toolbar, 'Find...', self.on_event, 'find.png')
        #util.tool_item(self, toolbar, 'Find Next', self.on_event, 'page_white_put.png')
        #util.tool_item(self, toolbar, 'Find Previous', self.on_event, 'page_white_get.png')
        util.tool_item(self, toolbar, 'Find In Files', self.on_event, 'magnifier.png')
        util.tool_item(self, toolbar, 'Replace', self.on_event, 'text_replace.png')
        util.tool_item(self, toolbar, 'Goto Line', self.on_event, 'text_linespacing.png')
        
        toolbar.Realize()
        toolbar.Fit()
        return toolbar
    def create_statusbar(self):
        statusbar = self.CreateStatusBar()
        self.statusbar = statusbar
    def on_new(self, event):
        self.notebook.create_tab()
    def on_open(self, event):
        dialog = wx.FileDialog(self, 'Open', style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST|wx.FD_MULTIPLE)
        tab = self.notebook.get_window()
        if tab and tab.file_path and settings.SET_DIRECTORY_FOR_OPEN:
            directory, file = os.path.split(tab.file_path)
            dialog.SetDirectory(directory)
        result = dialog.ShowModal()
        if result == wx.ID_OK:
            paths = dialog.GetPaths()
            for path in paths:
                self.open(path)
    def open(self, path):
        self.notebook.create_tab(path)
        self.rebuild_file_menu()
    def on_open_all_recent(self, event):
        paths = self.get_recent_files()
        for path in paths:
            self.open(path)
    def on_clear_recent(self, event):
        settings.RECENT_FILES = []
        self.rebuild_file_menu()
    def on_open_recent(self, event):
        item = self.GetMenuBar().FindItemById(event.GetId())
        path = item.GetHelp()
        self.open(path)
    def on_save(self, event):
        tab = self.notebook.get_window()
        if tab: self.save(tab)
    def save(self, tab):
        if not tab.save_file():
            self.save_as(tab)
    def on_save_as(self, event):
        tab = self.notebook.get_window()
        if tab: self.save_as(tab)
    def save_as(self, tab):
        dialog = wx.FileDialog(self, 'Save As', style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        result = dialog.ShowModal()
        if result == wx.ID_OK:
            path = dialog.GetPath()
            tab.save_file(path)
    def on_save_all(self, event):
        for tab in self.notebook.get_windows():
            self.save(tab)
    def on_cut(self, event):
        tab = self.notebook.get_window()
        if tab: tab.Cut()
    def on_copy(self, event):
        tab = self.notebook.get_window()
        if tab: tab.Copy()
    def on_paste(self, event):
        tab = self.notebook.get_window()
        if tab: tab.Paste()
    def on_select_all(self, event):
        tab = self.notebook.get_window()
        if tab: tab.SelectAll()
    def on_delete(self, event):
        tab = self.notebook.get_window()
        if tab: tab.Clear()
    def on_undo(self, event):
        tab = self.notebook.get_window()
        if tab: tab.Undo()
    def on_redo(self, event):
        tab = self.notebook.get_window()
        if tab: tab.Redo()
    def on_sort(self, event):
        tab = self.notebook.get_window()
        if tab: tab.sort()
    def on_lowercase(self, event):
        tab = self.notebook.get_window()
        if tab: tab.lower()
    def on_uppercase(self, event):
        tab = self.notebook.get_window()
        if tab: tab.upper()
    def on_close_tab(self, event):
        self.notebook.close_tab()
    def on_close_tabs(self, event):
        self.notebook.close_tabs()
    def on_next_tab(self, event):
        self.notebook.next_tab()
    def on_previous_tab(self, event):
        self.notebook.previous_tab()
    def on_find_next(self, event):
        tab = self.notebook.get_window()
        if tab: tab.find_next() # TODO: pass search token
    def on_exit(self, event):
        self.Close()
    def on_close(self, event):
        event.Skip()
        self.save_state()
        self.notebook.save_state()
    def on_tab_closed(self, event):
        event.Skip()
        self.rebuild_file_menu()
    def on_tab_changed(self, event):
        event.Skip()
        title = self.notebook.get_title()
        title = '%s - %s' % (title, APP_NAME) if title else APP_NAME
        self.SetTitle(title)
    def on_event(self, event):
        print 'Unhandled event!'
        
def run():
    app = wx.PySimpleApp()
    frame = Frame()
    frame.Show()
    app.MainLoop()
    
if __name__ == '__main__':
    run()
    