def polhemus():
    """
    Connect with Polhemus
    """
    import polhemus
    trck_init = polhemus.polhemus()
    initplh = trck_init.Initialize()
    trck_init.Run()

    return trck_init

def claron():
    """
    Connect with Claron
    """
    import pyclaron
    mtc = pyclaron.pyclaron()
    mtc.CalibrationDir = "C:\Program Files\Claron Technology\MicronTracker\CalibrationFiles"
    mtc.MarkerDir = "C:\Program Files\Claron Technology\MicronTracker\Markers"
    mtc.NumberFramesProcessed = 10
    mtc.Initialize()

    return mtc