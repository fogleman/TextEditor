import wx
import wx.stc as stc
import util

class Node(object):
    ROOT = 0
    CLASS = 1
    DEF = 2
    def __init__(self, parent, line, indent, type, text):
        self.parent = parent
        self.line = line
        self.indent = indent
        self.type = type
        self.text = text
        self.children = []
        if parent:
            parent.children.append(self)
    def _get_depth(self):
        if self.parent is None:
            return 0
        return self.parent._get_depth() + 1
    depth = property(_get_depth)
    def display(self):
        if self.parent:
            print '    '*(self.depth-1) + self.text, self.line
        for child in self.children:
            child.display()
            
class Parser(object):
    def __init__(self):
        pass
    def parse_file(self, path):
        file = open(path, 'r')
        text = file.read()
        file.close()
        return self.parse_string(text)
    def parse_string(self, text):
        count = 0
        root = Node(None, -1, -1, Node.ROOT, '')
        stack = [root]
        for line in text.split('\n'):
            count += 1
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith('#'):
                continue
            stripped = line.lstrip()
            indent = len(line) - len(stripped)
            stripped = stripped.strip().rstrip(':')
            while indent <= stack[-1].indent:
                stack.pop()
            node = None
            if stripped.startswith('class '):
                txt = stripped[6:].strip()
                node = Node(stack[-1], count, indent, Node.CLASS, txt)
            if stripped.startswith('def '):
                txt = stripped[4:].strip()
                node = Node(stack[-1], count, indent, Node.DEF, txt)
            if node and node.indent > stack[-1].indent:
                stack.append(node)
        return root
        
class Control(wx.TreeCtrl):
    def __init__(self, parent):
        super(Control, self).__init__(parent, -1, style=wx.TR_HIDE_ROOT|wx.TR_FULL_ROW_HIGHLIGHT|wx.TR_NO_LINES|wx.BORDER_STATIC)
        self.control = None
        self.cache = None
        font = self.GetFont()
        font.SetPointSize(10)
        self.SetFont(font)
        images = wx.ImageList(16, 16)
        images.Add(util.get_icon('bullet_go.png'))
        images.Add(util.get_icon('bullet_orange.png'))
        self.SetImageList(images)
        self.images = images
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_sel_changed)
    def set_control(self, control):
        if self.control:
            self.control.Unbind(stc.EVT_STC_CHANGE)#, self.on_change)
        self.control = control
        if control:
            self.control.Bind(stc.EVT_STC_CHANGE, self.on_change)
        wx.CallAfter(self.update)
    def on_change(self, event):
        event.Skip()
        control = self.control
        cache = (control, control.GetLineCount() if control else 0)
        if cache != self.cache:
            self.cache = cache
            wx.CallAfter(self.update)
    def update(self):
        control = self.control
        if control:
            text = control.GetText()
            parser = Parser()
            result = parser.parse_string(text)
            self.set_root(result)
        else:
            self.set_root(None)
    def on_sel_changed(self, event):
        item = self.GetSelection()
        control = self.control
        if item.IsOk() and control:
            data = self.GetPyData(item)
            p1 = control.PositionFromLine(data.line-1)
            p2 = control.PositionFromLine(data.line)-1
            control.SetSelection(p1, p2)
            control.ScrollToLine(data.line-control.LinesOnScreen()/2)
    def set_root(self, node):
        self.Freeze()
        self.UnselectAll()
        self.DeleteAllItems()
        if node:
            root = self.AddRoot('')
            for i, child in enumerate(node.children):
                item = self.add_node(root, child)
                self.Expand(item)
        self.Thaw()
    def add_node(self, parent, node):
        item = self.AppendItem(parent, node.text)
        self.SetPyData(item, node)
        if node.type == Node.CLASS:
            self.SetItemImage(item, 0)
            self.SetItemBold(item)
        elif node.type == Node.DEF:
            self.SetItemImage(item, 1)
        for child in node.children:
            self.add_node(item, child)
        return item
        
if __name__ == '__main__':
    parser = Parser()
    result = parser.parse_file('pybrowser.py')
    app = wx.PySimpleApp()
    frame = wx.Frame(None, -1, 'Python Class Browser')
    control = Control(frame, result)
    frame.Show()
    app.MainLoop()
    