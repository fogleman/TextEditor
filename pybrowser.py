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
        
if __name__ == '__main__':
    parser = Parser()
    result = parser.parse_file('pybrowser.py')
    result.display()
    