from settings import settings

def activate_psyco():
    try:
        import psyco
        psyco.full()
    except:
        pass
        
def run():
    import wx
    import frame
    import ipc_win32 as ipc
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
    