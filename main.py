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
    app = wx.PySimpleApp()
    window = frame.Frame()
    window.Show()
    app.MainLoop()
    
if __name__ == '__main__':
    if settings.USE_PSYCO:
        activate_psyco()
    run()
    