import wx
import wx.aui as aui
import wx.stc as stc
import os
import control
import notebook
import util
import find
import about
import styles
import style_dialog
from settings import settings

class Frame(wx.Frame):
    def __init__(self, parent=None, title=settings.APP_NAME):
        super(Frame, self).__init__(parent, -1, title)
        self.style_manager = styles.StyleManager()
        manager = aui.AuiManager(self)
        self.manager = manager
        self.create_menu()
        self.create_statusbar()
        self.create_notebook()
        self.create_toolbars()
        manager.Update()
        self.load_state()
        self.notebook.load_state()
        self.rebuild_file_menu()
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_ACTIVATE, self.on_activate)
        self.SetIcon(wx.Icon('icons/page_edit.ico', wx.BITMAP_TYPE_ICO))
    def parse_args(self, args):
        self.Raise()
        files = args.split(';')
        files = [file.strip() for file in files]
        files = filter(bool, files)
        for file in files:
            path = os.path.abspath(file)
            if os.path.exists(path):
                self.open(path)
    def set_default_size(self):
        w = wx.SystemSettings_GetMetric(wx.SYS_SCREEN_X)
        h = wx.SystemSettings_GetMetric(wx.SYS_SCREEN_Y)
        wr, hr = 1, 1
        pad = min(w/8, h/8)
        n = min((w-pad)/wr, (h-pad)/hr)
        size = (n*wr, n*hr)
        self.SetSize(size)
    def save_state(self):
        if settings.MAIN_WINDOW_PERSISTED and not self.IsIconized():
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
    def create_context_menu(self, control):
        selection = bool(control.GetSelectedText())
        menu = wx.Menu()
        util.menu_item(self, menu, 'Cut', self.on_cut, 'cut.png').Enable(selection)
        util.menu_item(self, menu, 'Copy', self.on_copy, 'page_copy.png').Enable(selection)
        util.menu_item(self, menu, 'Paste', self.on_paste, 'paste_plain.png').Enable(control.CanPaste())
        util.menu_item(self, menu, 'Delete', self.on_delete, 'delete.png').Enable(selection)
        menu.AppendSeparator()
        util.menu_item(self, menu, 'Select All', self.on_select_all, 'table_go.png')
        menu.AppendSeparator()
        util.menu_item(self, menu, 'Mark Selection', self.on_mark_text, 'pencil_add.png').Enable(selection)
        util.menu_item(self, menu, 'Unmark Selection', self.on_unmark_text, 'blank.png').Enable(selection)
        util.menu_item(self, menu, 'Unmark All', self.on_unmark_all, 'pencil_delete.png').Enable(bool(control._markers))
        return menu
    def create_tab_menu(self):
        menu = wx.Menu()
        util.menu_item(self, menu, 'Close', self.on_close_tab, 'page_delete.png')
        util.menu_item(self, menu, 'Close Others', self.on_close_other_tabs, 'blank.png')
        util.menu_item(self, menu, 'Close All', self.on_close_tabs, 'blank.png')
        menu.AppendSeparator()
        util.menu_item(self, menu, 'Save', self.on_save, 'disk.png')
        util.menu_item(self, menu, 'Save As...', self.on_save_as, 'blank.png')
        menu.AppendSeparator()
        util.menu_item(self, menu, 'Open Containing Folder', self.on_containing_folder, 'folder.png')
        return menu
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
        util.menu_item(self, file, 'Reload', self.on_reload, 'arrow_refresh_small.png')
        #util.menu_item(self, file, 'Rename...', self.on_event, 'drive_edit.png')
        util.menu_item(self, file, 'Delete From Disk', self.on_delete_file, 'cross.png')
        file.AppendSeparator()
        util.menu_item(self, file, 'Print...\tCtrl+P', self.on_event, 'printer.png').Enable(False)
        file.AppendSeparator()
        recent_files = self.get_recent_files()
        if recent_files and settings.SHOW_RECENT_FILES:
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
        util.menu_item(self, edit, 'Indent\tTab', self.on_indent, 'text_indent.png')
        util.menu_item(self, edit, 'Unindent\tShift+Tab', self.on_unindent, 'text_indent_remove.png')
        util.menu_item(self, edit, 'Toggle Comment\tCtrl+/', self.on_comment, 'text_padding_left.png')
        edit.AppendSeparator()
        util.menu_item(self, edit, 'Sort', self.on_sort, 'arrow_down.png')
        util.menu_item(self, edit, 'Lowercase', self.on_lowercase, 'text_lowercase.png')
        util.menu_item(self, edit, 'Uppercase', self.on_uppercase, 'text_uppercase.png')
        menubar.Append(edit, '&Edit')
        
        search = wx.Menu()
        util.menu_item(self, search, 'Find...\tCtrl+F', self.on_find, 'find.png')
        util.menu_item(self, search, 'Find Next\tF3', self.on_find_next, 'page_white_put.png')
        util.menu_item(self, search, 'Find Previous\tCtrl+F3', self.on_find_previous, 'page_white_get.png')
        util.menu_item(self, search, 'Find In Files...\tCtrl+Shift+F', self.on_event, 'magnifier.png').Enable(False)
        util.menu_item(self, search, 'Replace...\tCtrl+R', self.on_replace, 'text_replace.png')
        util.menu_item(self, search, 'Goto Line...\tCtrl+G', self.on_goto_line, 'text_linespacing.png')
        search.AppendSeparator()
        util.menu_item(self, search, 'Mark Selection', self.on_mark_text, 'pencil_add.png')
        util.menu_item(self, search, 'Unmark Selection', self.on_unmark_text, 'blank.png')
        util.menu_item(self, search, 'Unmark All', self.on_unmark_all, 'pencil_delete.png')
        menubar.Append(search, '&Search')
        
        view = wx.Menu()
        util.menu_item(self, view, 'Next Tab\tCtrl+Tab', self.on_next_tab, 'arrow_right.png')
        util.menu_item(self, view, 'Previous Tab\tCtrl+Shift+Tab', self.on_previous_tab, 'arrow_left.png')
        view.AppendSeparator()
        util.menu_item(self, view, 'Toggle Word Wrap', self.on_word_wrap, 'text_padding_bottom.png')
        menubar.Append(view, '&View')
        
        tools = wx.Menu()
        util.menu_item(self, tools, 'Options...', self.on_event, 'cog.png').Enable(False)
        util.menu_item(self, tools, 'Fonts && Colors...', self.on_styles, 'palette.png')
        tools.AppendSeparator()
        util.menu_item(self, tools, 'Record Macro\tCtrl+Shift+R', self.on_record_macro, 'bullet_red.png')
        util.menu_item(self, tools, 'Play Macro\tCtrl+Shift+P', self.on_play_macro, 'control_play.png')
        util.menu_item(self, tools, 'Play Macro to End of File', self.on_play_macro_to_end, 'control_end.png')
        menubar.Append(tools, '&Tools')
        
        help = wx.Menu()
        util.menu_item(self, help, 'About %s...' % settings.APP_NAME, self.on_about, 'information.png')
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
        util.tool_item(self, toolbar, 'Find', self.on_find, 'find.png')
        util.tool_item(self, toolbar, 'Find Next', self.on_find_next, 'page_white_put.png')
        util.tool_item(self, toolbar, 'Find Previous', self.on_find_previous, 'page_white_get.png')
        util.tool_item(self, toolbar, 'Find In Files', self.on_event, 'magnifier.png')
        util.tool_item(self, toolbar, 'Replace', self.on_replace, 'text_replace.png')
        util.tool_item(self, toolbar, 'Goto Line', self.on_goto_line, 'text_linespacing.png')
        toolbar.AddSeparator()
        util.tool_item(self, toolbar, 'Mark Selection', self.on_mark_text, 'pencil_add.png')
        util.tool_item(self, toolbar, 'Unmark All', self.on_unmark_all, 'pencil_delete.png')
        toolbar.AddSeparator()
        util.tool_item(self, toolbar, 'Toggle Word Wrap', self.on_word_wrap, 'text_padding_bottom.png')
        toolbar.Realize()
        toolbar.Fit()
        return toolbar
    def create_statusbar(self):
        statusbar = self.CreateStatusBar()
        self.statusbar = statusbar
    def get_control(self):
        return self.notebook.get_window()
    def get_floating_position(self, pane):
        anchor = self.get_control()
        x, y = anchor.GetScreenPosition()
        w1, h1 = anchor.GetSize()
        w2, h2 = pane.GetSize()
        px, py = 32, 8
        return (x+w1-w2-px, y+py)
    def float(self, window):
        window.SetPosition(self.get_floating_position(window))
    def on_goto_line(self, event):
        dialog = find.GotoLine(self)
        dialog.Centre()
        dialog.ShowModal()
    def on_new(self, event):
        self.notebook.create_tab()
    def on_open(self, event):
        dialog = wx.FileDialog(self, 'Open', style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST|wx.FD_MULTIPLE)
        tab = self.get_control()
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
        tab = self.get_control()
        if tab: self.save(tab)
    def save(self, tab):
        if not tab.save_file():
            self.save_as(tab)
    def on_save_as(self, event):
        tab = self.get_control()
        if tab: self.save_as(tab)
    def save_as(self, tab):
        dialog = wx.FileDialog(self, 'Save As', style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        result = dialog.ShowModal()
        if result == wx.ID_OK:
            path = dialog.GetPath()
            tab.save_file(path, force=True)
            self.notebook.update_tab_name(tab)
            self.update_title()
    def on_save_all(self, event):
        for tab in self.notebook.get_windows():
            self.save(tab)
    def on_find(self, event, replace=False):
        window = find.Find(self, replace)
        self.float(window)
        window.Show()
    def on_replace(self, event):
        self.on_find(event, replace=True)
    def on_cut(self, event):
        self.get_control().Cut()
    def on_copy(self, event):
        self.get_control().Copy()
    def on_paste(self, event):
        self.get_control().Paste()
    def on_select_all(self, event):
        self.get_control().SelectAll()
    def on_delete(self, event):
        self.get_control().Clear()
    def on_undo(self, event):
        self.get_control().Undo()
    def on_redo(self, event):
        self.get_control().Redo()
    def on_sort(self, event):
        self.get_control().sort()
    def on_lowercase(self, event):
        self.get_control().lower()
    def on_uppercase(self, event):
        self.get_control().upper()
    def on_indent(self, event):
        self.get_control().indent()
    def on_unindent(self, event):
        self.get_control().unindent()
    def on_comment(self, event):
        self.get_control().toggle_comment()
    def on_reload(self, event):
        self.get_control().reload_file()
    def on_delete_file(self, event):
        self.notebook.delete_file()
    def on_close_tab(self, event):
        self.notebook.close_tab()
    def on_close_tabs(self, event):
        self.notebook.close_tabs()
    def on_close_other_tabs(self, event):
        self.notebook.close_other_tabs()
    def on_next_tab(self, event):
        self.notebook.next_tab()
    def on_previous_tab(self, event):
        self.notebook.previous_tab()
    def on_containing_folder(self, event):
        path = self.get_control().file_path
        if path:
            proc = 'explorer.exe /select,"%s"' % path
            wx.Execute(proc)
    def on_styles(self, event):
        dialog = style_dialog.StyleDialog(self, self.style_manager)
        dialog.Bind(style_dialog.EVT_STYLE_CHANGED, self.on_style_changed)
        dialog.Centre()
        dialog.ShowModal()
    def on_style_changed(self, event):
        for tab in self.notebook.get_windows():
            tab.detect_language()
    def on_record_macro(self, event):
        self.get_control().toggle_macro()
    def on_play_macro(self, event):
        self.get_control().play_macro()
    def on_play_macro_to_end(self, event):
        self.get_control().play_macro_to_end()
    def on_word_wrap(self, event):
        self.get_control().word_wrap()
    def on_find_next(self, event):
        self.get_control().find(settings.FIND_TEXT)
    def on_find_previous(self, event):
        self.get_control().find(settings.FIND_TEXT, previous=True)
    def on_mark_text(self, event):
        self.get_control().mark_text()
    def on_unmark_text(self, event):
        self.get_control().unmark_text()
    def on_unmark_all(self, event):
        self.get_control().unmark_all()
    def on_about(self, event):
        dialog = about.About(self)
        dialog.ShowModal()
    def on_exit(self, event):
        self.Close()
    def on_close(self, event):
        can_veto = event.CanVeto()
        veto = not self.confirm_close(can_veto)
        if veto and can_veto:
            event.Veto()
            return
        event.Skip()
        self.save_state()
        self.notebook.save_state()
    def confirm_close(self, can_veto):
        for tab in self.notebook.get_windows():
            if not tab.confirm_close(can_veto):
                return False
        return True
    def on_activate(self, event):
        event.Skip()
        if event.GetActive():
            self.check_file_modifications()
    def on_tab_closed(self, event):
        event.Skip()
        self.rebuild_file_menu()
        self.check_file_modifications()
    def on_tab_changed(self, event):
        event.Skip()
        self.update_title()
        self.check_file_modifications()
    def check_file_modifications(self):
        for tab in self.notebook.get_windows():
            if not tab.check_stat():
                tab.mark_stat()
                name = tab.file_path or tab.get_name()
                style = wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION
                dialog = wx.MessageDialog(self, 'Reload changed file "%s"?' % name, 'File Changed', style)
                result = dialog.ShowModal()
                if result == wx.ID_YES:
                    tab.reload_file()
                else:
                    tab.edited = True
    def update_title(self):
        title = self.notebook.get_title()
        title = '%s - %s' % (title, settings.APP_NAME) if title else settings.APP_NAME
        self.SetTitle(title)
    def on_event(self, event):
        dialog = wx.MessageDialog(self, 'This feature does not exist yet.', 'Lazy Programmer Error', wx.OK|wx.ICON_INFORMATION)
        dialog.ShowModal()
        
