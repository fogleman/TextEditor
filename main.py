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
        self.SetSize((1000, 1100))
        self.SetIcon(wx.IconFromBitmap(util.get_icon('page_edit.png')))
        self.notebook.load_state()
        self.load_state()
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
            self.SetSize(settings.MAIN_WINDOW_SIZE)
            self.SetPosition(settings.MAIN_WINDOW_POSITION)
            self.Maximize(settings.MAIN_WINDOW_MAXIMIZED)
    def create_notebook(self):
        tabs = notebook.Notebook(self)
        self.notebook = tabs
        tabs.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.on_tab_changed)
        #tabs.create_tab()
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
        toolbar = self.create_toolbar()
        self.manager.AddPane(toolbar, info)
    def create_menu(self):
        menubar = wx.MenuBar()
        file = wx.Menu()
        util.menu_item(self, file, '&New\tCtrl+N', self.on_new, 'page.png')
        util.menu_item(self, file, '&Open...\tCtrl+O', self.on_open, 'folder_page.png')
        util.menu_item(self, file, '&Save\tCtrl+S', self.on_save, 'disk.png')
        util.menu_item(self, file, '&Save As...\tCtrl+Shift+S', self.on_save_as, 'disk.png')
        util.menu_item(self, file, 'Save All', self.on_event, 'disk_multiple.png')
        file.AppendSeparator()
        util.menu_item(self, file, 'Close\tCtrl+F4', self.on_event, 'folder_delete.png')
        util.menu_item(self, file, 'Close All', self.on_event, 'folder_delete.png')
        file.AppendSeparator()
        util.menu_item(self, file, 'Reload', self.on_event, 'drive_go.png')
        util.menu_item(self, file, 'Rename...', self.on_event, 'page_go.png')
        util.menu_item(self, file, 'Delete From Disk', self.on_event, 'cross.png')
        file.AppendSeparator()
        util.menu_item(self, file, 'Print...\tCtrl+P', self.on_event, 'printer.png')
        file.AppendSeparator()
        util.menu_item(self, file, '&Exit\tAlt+F4', self.on_exit, 'door_out.png')
        menubar.Append(file, '&File')
        
        edit = wx.Menu()
        util.menu_item(self, edit, '&Undo\tCtrl+Z', self.on_undo, 'arrow_undo.png')
        util.menu_item(self, edit, '&Redo\tCtrl+Y', self.on_redo, 'arrow_redo.png')
        edit.AppendSeparator()
        util.menu_item(self, edit, 'Cut\tCtrl+X', self.on_cut, 'cut.png')
        util.menu_item(self, edit, 'Copy\tCtrl+C', self.on_copy, 'page_copy.png')
        util.menu_item(self, edit, 'Paste\tCtrl+V', self.on_paste, 'paste_plain.png')
        util.menu_item(self, edit, 'Delete\tDel', self.on_delete, 'delete.png')
        util.menu_item(self, edit, 'Select All\tCtrl+A', self.on_select_all, 'table_go.png')
        edit.AppendSeparator()
        util.menu_item(self, edit, 'Lowercase', self.on_event, 'text_lowercase.png')
        util.menu_item(self, edit, 'Uppercase', self.on_event, 'text_uppercase.png')
        menubar.Append(edit, '&Edit')
        
        search = wx.Menu()
        util.menu_item(self, search, 'Find...\tCtrl+F', self.on_event, 'find.png')
        util.menu_item(self, search, 'Find Next\tF3', self.on_event, 'page_white_put.png')
        util.menu_item(self, search, 'Find Previous\tCtrl+F3', self.on_event, 'page_white_get.png')
        util.menu_item(self, search, 'Find In Files...\tCtrl+Shift+F', self.on_event, 'magnifier.png')
        util.menu_item(self, search, 'Replace...\tCtrl+H', self.on_event, 'text_replace.png')
        util.menu_item(self, search, 'Goto Line...\tCtrl+G', self.on_event, 'text_linespacing.png')
        menubar.Append(search, '&Search')
        
        view = wx.Menu()
        menubar.Append(view, '&View')
        
        tools = wx.Menu()
        menubar.Append(tools, '&Tools')
        
        help = wx.Menu()
        menubar.Append(help, '&Help')
        
        self.SetMenuBar(menubar)
    def create_toolbar(self):
        toolbar = wx.ToolBar(self, -1, style=wx.TB_HORIZONTAL|wx.TB_FLAT|wx.TB_NODIVIDER)
        toolbar.SetToolBitmapSize((18,18))
        util.tool_item(self, toolbar, 'New Document', self.on_new, 'page.png')
        util.tool_item(self, toolbar, 'Open Document', self.on_open, 'folder_page.png')
        util.tool_item(self, toolbar, 'Save Document', self.on_save, 'disk.png')
        util.tool_item(self, toolbar, 'Save All Documents', self.on_event, 'disk_multiple.png')
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
        result = dialog.ShowModal()
        if result == wx.ID_OK:
            paths = dialog.GetPaths()
            for path in paths:
                self.notebook.create_tab(path)
    def on_save(self, event):
        tab = self.notebook.get_window()
        if tab and not tab.save_file():
            self.on_save_as(event)
    def on_save_as(self, event):
        tab = self.notebook.get_window()
        if not tab: return
        dialog = wx.FileDialog(self, 'Save As', style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        result = dialog.ShowModal()
        if result == wx.ID_OK:
            path = dialog.GetPath()
            tab.save_file(path)
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
    def on_exit(self, event):
        self.Close()
    def on_close(self, event):
        event.Skip()
        self.save_state()
        self.notebook.save_state()
    def on_tab_changed(self, event):
        event.Skip()
        title = self.notebook.get_title()
        title = '%s - %s' % (title, APP_NAME) if title else APP_NAME
        self.SetTitle(title)
    def on_tab_edited(self, event):
        event.Skip()
        notebook = self.notebook
        widget = event.GetEventObject()
        index = notebook.GetPageIndex(widget)
        if index == wx.NOT_FOUND: return
        notebook.SetPageBitmap(index, util.get_icon('page_red.png'))
    def on_event(self, event):
        print 'Unhandled event!'
        
def run():
    #import psyco
    #psyco.full()
    app = wx.PySimpleApp()
    frame = Frame()
    frame.Show()
    app.MainLoop()
    
if __name__ == '__main__':
    run()
    