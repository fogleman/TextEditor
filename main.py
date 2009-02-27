from settings import settings

def activate_psyco():
    try:
        import psyco
        psyco.full()
    except:
        pass
        
def set_path(module):
    import os
    file = module.__file__
    file = os.path.abspath(file)
    while file and not os.path.isdir(file):
        file, dummy = os.path.split(file)
    os.chdir(file)
    
def run():
    import wx
    import frame
    import ipc_win32 as ipc
    set_path(frame)
    app = wx.PySimpleApp()
    container, message = ipc.init()
    if container:
        window = frame.Frame()
        container.callback = window.parse_args
        container(message)
        window.Show()
        app.MainLoop()
        
if __name__ == '__main__':
    if settings.USE_PSYCO:
        activate_psyco()
    run()
    