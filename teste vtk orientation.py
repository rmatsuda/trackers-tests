import wx
from vtk.wx.wxVTKRenderWindowInteractor import wxVTKRenderWindowInteractor
import vtk
import time
import threading
from wx.lib.pubsub import pub as Publisher
# ----------------------------------------------------------------------------------------------
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
# ----------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, id):
        wx.Frame.__init__(self, id, title='trackers control', style=wx.DEFAULT_FRAME_STYLE)
        self.__bind_events()
        ## Add a menubar
        self.stop_flag = 1

        menuBar = wx.MenuBar()

        menuF = wx.Menu()

        menuBar.Append(menuF, "Menu")

        #self.draw = menuF.Append(wx.ID_OPEN, 'Start Tracker')

        imp = wx.Menu()
        self.plh = imp.Append(wx.ID_ANY, 'Polhemus')
        self.mtc = imp.Append(wx.ID_ANY, 'Claron')
        self.menuTrackers = menuF.AppendMenu(wx.ID_ANY, 'Start Tracker', imp)
        self.stop = menuF.Append(wx.ID_ANY, 'Stop Tracker')

        self.SetMenuBar(menuBar)

        self.sb = self.CreateStatusBar()

        self.sb.SetFieldsCount(2)

        # Add the vtk window widget

        self.widget = wxVTKRenderWindowInteractor(self, -1)

        self.widget.Enable(1)

        # Layout

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(self.widget, 1, wx.EXPAND)

        self.SetSizer(sizer)

        self.Layout()

        # Ad a renderer

        self.ren = vtk.vtkRenderer()

        self.widget.GetRenderWindow().AddRenderer(self.ren)

        # Bind the menu

        self.Bind(wx.EVT_MENU, self.onplh, self.plh)
        self.Bind(wx.EVT_MENU, self.onmtc, self.mtc)
        self.Bind(wx.EVT_MENU, self.onStop, self.stop)

        arrowSource1 = vtk.vtkArrowSource()
        arrowSource1.SetTipResolution(50)

        # Create a mapper and actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(arrowSource1.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0, 0, 1)
        actor.RotateZ(180)
        actor.SetScale(1.0, 2.0, 2.0)

        arrowSource2 = vtk.vtkArrowSource()
        arrowSource2.SetTipLength(.175)
        arrowSource2.SetTipResolution(50)
        mapper2 = vtk.vtkPolyDataMapper()
        mapper2.SetInputConnection(arrowSource2.GetOutputPort())
        actor2 = vtk.vtkActor()
        actor2.SetMapper(mapper2)
        actor2.GetProperty().SetColor(1, 0, 0)
        actor2.SetScale(1.25, 2.0, 2.0)

        # create cube
        cube = vtk.vtkCubeSource()
        cube.SetXLength(0.1)
        cube.SetYLength(0.8)
        cube.SetZLength(0.1)

        # mapper
        cubeMapper = vtk.vtkPolyDataMapper()
        cubeMapper.SetInputConnection(cube.GetOutputPort())
        actor3 = vtk.vtkActor()
        actor3.SetMapper(cubeMapper)

        self.ball_actor = vtk.vtkAssembly()
        self.ball_actor.AddPart(actor)
        self.ball_actor.AddPart(actor2)
        self.ball_actor.AddPart(actor3)
        self.ball_actor.SetScale(10.0, 10.0, 10.0)
        self.ball_reference = self.ball_actor
        self.ren.AddActor(self.ball_actor)

        self.ren.ResetCamera()

        # Render the scene
        self.widget.Render()

    def onStop(self, evt):
        self.stop_flag = None
        self.menuTrackers.Enable(True)
        self.thr.stop()

    def onplh(self, evt):
        self.tracker_init = polhemus()
        self.stop_flag = 1
        tck = 'plh'
        self.menuTrackers.Enable(False)
        self.thr = nav(self.stop_flag,self.tracker_init, self.ball_reference,tck)

    def onmtc(self, evt):
        self.tracker_init = claron()
        self.stop_flag = 1
        tck = 'mtc'
        self.menuTrackers.Enable(False)
        self.thr = nav(self.stop_flag,self.tracker_init, self.ball_reference,tck)

    def __bind_events(self):
        Publisher.subscribe(self.__update_orientation, 'Update Orientation')

    def __update_orientation(self):
        self.widget.Render()

# ----------------------------------------------------------------------------------------------
class nav(threading.Thread):
    # Thread created to update the coordinates with the fiducial points
    # corregistration method while the Navigation Button is pressed.
    # Sleep function in run method is used for better real-time navigation

    def __init__(self,nav, tracker_init,ball,tck):
        threading.Thread.__init__(self)
        self.nav = nav
        self.tracker_init = tracker_init
        self.ball_reference =ball
        self.tck = tck
        self._pause_ = False
        self.start()

    def stop(self):
        self._pause_ = True
        self.tracker_init.Close()

    def run(self):
        inch2mm = 25.4
        while self.nav:
            if self.tck == "plh":
                plh = self.tracker_init
                plh.Run()
                coord = (plh.PositionTooltipX1, plh.PositionTooltipY1, plh.PositionTooltipZ1,
                         plh.AngleX1, plh.AngleY1, plh.AngleZ1)

                coord = [float(coord[0]) * inch2mm, float(coord[1]) * inch2mm,
                         float(coord[2]) * (-inch2mm), float(coord[3]),
                         float(coord[4]), float(coord[5])]
                print coord
                self.ball_reference.SetOrientation(float(coord[3]), float(coord[4]), float(coord[5]))
                wx.CallAfter(Publisher.sendMessage, 'Update Orientation')
            elif self.tck == "mtc":
                mtc = self.tracker_init
                mtc.Run()
                coord = (mtc.PositionTooltipX1, mtc.PositionTooltipY1, mtc.PositionTooltipZ1,
                                  mtc.AngleX1, mtc.AngleY1, mtc.AngleZ1)
                coord = [float(coord[0]), float(coord[1]),
                         float(coord[2]), float(coord[3]),
                         float(coord[4]), float(coord[5])]
                print coord
                self.ball_reference.SetOrientation(float(coord[3]), float(coord[4]), float(coord[5]))
                wx.CallAfter(Publisher.sendMessage, 'Update Orientation')

            time.sleep(0.175)

            if self._pause_:
                return

if __name__ == "__main__":
    app = wx.App(0)

    frame = MyFrame(None)

    frame.Show()

    app.MainLoop()