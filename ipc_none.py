import wx
import sys

class CallbackContainer(object):
    def __init__(self):
        self.callback = None
    def __call__(self, message):
        if self.callback:
            wx.CallAfter(self.callback, message)
            
def init():
    container = CallbackContainer()
    message = ';'.join(sys.argv[1:])
    return container, message
    