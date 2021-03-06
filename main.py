def set_path():
    import os
    import dummy
    file = dummy.__file__
    file = os.path.abspath(file)
    while file and not os.path.isdir(file):
        file, ext = os.path.split(file)
    os.chdir(file)
    
def activate_psyco():
    try:
        import psyco
        psyco.full()
    except:
        pass
        
def run():
    import wx
    import frame
    try:
        import ipc_win32 as ipc
    except:
        import ipc_none as ipc
    app = wx.PySimpleApp()
    container, message = ipc.init()
    if container:
        window = frame.Frame()
        container.callback = window.parse_args
        container(message)
        window.Show()
        app.MainLoop()
        
if __name__ == '__main__':
    set_path()
    from settings import settings
    if settings.USE_PSYCO:
        activate_psyco()
    run()
    