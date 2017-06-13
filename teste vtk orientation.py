import wx
from vtk.wx.wxVTKRenderWindowInteractor import wxVTKRenderWindowInteractor
import vtk
import os
#requires the following import to works sendmessage args
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub as Publisher
import numpy as np
from math import radians, sin, cos

import trackers
import coord

class MyFrame(wx.Frame):
    def __init__(self, id):
        wx.Frame.__init__(self, id, title='Trackers control',size=(1300, 800), style=wx.DEFAULT_FRAME_STYLE)
        self.__bind_events()
        #TODO: Fix vtkwarning when its using tube obj
        fow = vtk.vtkFileOutputWindow()
        ow = vtk.vtkOutputWindow()
        ow.SetInstance(fow)

        ## Add a menubar
        self.stop_flag = 1

        menuBar = wx.MenuBar()
        menuF = wx.Menu()
        menuBar.Append(menuF, "OBJs")

        imp0 = wx.Menu()
        self.arrowOBJ = imp0.Append(wx.ID_ANY, 'Arrow')
        self.tube = imp0.Append(wx.ID_ANY, 'Tube')
        self.obj = menuF.AppendMenu(wx.ID_ANY, 'Create an OBJ', imp0)

        self.delOBJ = menuF.Append(wx.ID_ANY, 'Delete OBJ')

        menuT = wx.Menu()
        menuBar.Append(menuT, "Trackers")
        imp = wx.Menu()
        self.mtc = imp.Append(wx.ID_ANY, 'Claron')
        self.plh = imp.Append(wx.ID_ANY, 'Polhemus')
        self.menuTrackers = menuT.AppendMenu(wx.ID_ANY, 'Start Tracker', imp)

        self.stop = menuT.Append(wx.ID_ANY, 'Stop Tracker')

        self.SetMenuBar(menuBar)

        self.sb = self.CreateStatusBar()

        self.sb.SetFieldsCount(2)
        self.stop.Enable(False)
        self.menuTrackers.Enable(False)
        self.delOBJ.Enable(False)
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
        self.Bind(wx.EVT_MENU, self.onarrow, self.arrowOBJ)
        self.Bind(wx.EVT_MENU, self.ontube, self.tube)
        self.Bind(wx.EVT_MENU, self.ondelOBJ, self.delOBJ)
        self.Bind(wx.EVT_MENU, self.onplh, self.plh)
        self.Bind(wx.EVT_MENU, self.onmtc, self.mtc)
        self.Bind(wx.EVT_MENU, self.onStop, self.stop)

        #create axes
        axes = vtk.vtkAxesActor()
        self.marker = vtk.vtkOrientationMarkerWidget()
        self.marker.SetInteractor(self.widget._Iren)
        self.marker.SetOrientationMarker(axes)
        self.marker.SetViewport(0.75, 0, 1, 0.25)
        self.marker.SetEnabled(1)

    def onarrow(self, evt):
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

        self.arrow = vtk.vtkAssembly()
        self.arrow.AddPart(actor)
        self.arrow.AddPart(actor2)
        self.arrow.AddPart(actor3)
        self.arrow.SetScale(10.0, 10.0, 10.0)
        self.ball_reference = self.arrow
        self.ren.AddActor(self.arrow)

        self.ball_referenceP = vtk.vtkSphereSource()
        self.ball_referenceP.SetRadius(3)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(self.ball_referenceP.GetOutputPort())
        p = vtk.vtkProperty()
        p.SetColor(0, 1, 0)
        self.ball_actorP = vtk.vtkActor()
        self.ball_actorP.SetMapper(mapper)
        self.ball_actorP.SetProperty(p)
        self.ren.AddActor(self.ball_actorP)

        # filename = "C://Users//renan//Google Drive//Lab//Material suporte//Imagens Teste//0051//CT 0051 - InVesalius Sample.stl"
        # reader = vtk.vtkSTLReader()
        # reader.SetFileName(filename)
        # mapper = vtk.vtkPolyDataMapper()
        # mapper.SetInputConnection(reader.GetOutputPort())
        # actor = vtk.vtkActor()
        # actor.SetMapper(mapper)
        # self.ren.AddActor(actor)

        self.ren.ResetCamera()

        # Render the scene
        self.widget.Render()
        self.menuTrackers.Enable(True)
        self.obj.Enable(False)
        self.delOBJ.Enable(True)

        self.OBJ_ID = 0

    def ontube(self, evt):
        # Create a line
        self.lineSource = vtk.vtkLineSource()
        self.lineSource.SetPoint1(1, 0, 0)
        self.lineSource.SetPoint2(0, 1, 0)

        # Create a mapper and actor
        lineMapper = vtk.vtkPolyDataMapper()
        lineMapper.SetInputConnection(self.lineSource.GetOutputPort())
        self.lineActor = vtk.vtkActor()
        self.lineActor.GetProperty().SetColor(1, 1, 1)
        self.lineActor.GetProperty().SetLineWidth(5)
        self.lineActor.SetMapper(lineMapper)
        #self.lineActor.SetScale(10.0, 10.0, 10.0)

        # create cube
        cube = vtk.vtkCubeSource()
        cube.SetXLength(1.0)
        cube.SetYLength(8.0)
        cube.SetZLength(1.0)

        # mapper
        cubeMapper = vtk.vtkPolyDataMapper()
        cubeMapper.SetInputConnection(cube.GetOutputPort())
        self.cube = vtk.vtkActor()
        self.cube.SetMapper(cubeMapper)

        self.ren.AddActor(self.lineActor)
        self.ren.AddActor(self.cube)

        self.ren.ResetCamera()

        # Render the scene
        self.widget.Render()

        self.menuTrackers.Enable(True)
        self.obj.Enable(False)
        self.delOBJ.Enable(True)

        self.OBJ_ID = 1

    def ondelOBJ(self, evt):
        if self.OBJ_ID == 0:
            self.ren.RemoveActor(self.ball_actorP)
            self.ren.RemoveActor(self.arrow)
        elif self.OBJ_ID == 1:
            self.ren.RemoveActor(self.lineActor)
        self.widget.Render()
        self.obj.Enable(True)
        self.menuTrackers.Enable(False)
        self.delOBJ.Enable(False)


    def onStop(self, evt):
        self.stop_flag = None
        self.menuTrackers.Enable(True)
        self.stop.Enable(False)
        self.delOBJ.Enable(True)
        self.thr.stop()

    def onplh(self, evt):
        self.tracker_init = trackers.polhemus()
        self.stop_flag = 1
        tck = 'plh'
        self.menuTrackers.Enable(False)
        self.stop.Enable(True)
        self.delOBJ.Enable(False)
        self.thr = coord.nav(self.stop_flag,self.tracker_init, tck)

    def onmtc(self, evt):
        self.tracker_init = trackers.claron()
        self.stop_flag = 1
        tck = 'mtc'
        self.menuTrackers.Enable(False)
        self.stop.Enable(True)
        self.delOBJ.Enable(False)
        self.thr = coord.nav(self.stop_flag,self.tracker_init, tck)

    def __bind_events(self):
        Publisher.subscribe(self.__update_orientation, 'Update Orientation')

    def __update_orientation(self, pubsub_evt):
        coord = pubsub_evt.data
        if self.OBJ_ID == 0:
            self.ball_reference.SetPosition(float(coord[0]), float(coord[1]), float(coord[2]))
            self.ball_reference.SetOrientation(float(coord[3]), float(coord[4]), float(coord[5]))
            self.ball_referenceP.SetCenter(float(coord[0]), float(coord[1]), float(coord[2]))
        elif self.OBJ_ID == 1:
            self.lineSource.SetPoint1(float(coord[9]), float(coord[10]), float(coord[11]))
            self.lineSource.SetPoint2(float(coord[6]), float(coord[7]), float(coord[8]))
            self.cube.SetPosition(((float(coord[6]))+float(coord[9]))/2,((float(coord[7]))+float(coord[10]))/2,((float(coord[8]))+float(coord[11]))/2)
            print ((((float(coord[6]))+float(coord[9]))/2),(((float(coord[7]))+float(coord[10]))/2),(((float(coord[11]))+float(coord[8]))/2))
        self.widget.Render()
        self.ren.ResetCamera()

# ----------------------------------------------------------------------------------------------


if __name__ == "__main__":
    app = wx.App(0)

    frame = MyFrame(None)

    frame.Show()

    app.MainLoop()