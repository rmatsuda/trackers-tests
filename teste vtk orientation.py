import wx
from vtk.wx.wxVTKRenderWindowInteractor import wxVTKRenderWindowInteractor
import vtk
import os
#requires the following import to works sendmessage args
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub as Publisher
import numpy as np
from math import radians, sin, cos
import create as c
import random
from numpy.core.umath_tests import inner1d

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
        self.coil = imp0.Append(wx.ID_ANY, 'Coil')
        self.brain = imp0.Append(wx.ID_ANY, 'Brain')
        self.obj = menuF.AppendMenu(wx.ID_ANY, 'Create an OBJ', imp0)

        self.delOBJ = menuF.Append(wx.ID_ANY, 'Delete OBJ')

        menuT = wx.Menu()
        menuBar.Append(menuT, "Trackers")
        imp = wx.Menu()
        self.mtc = imp.Append(wx.ID_ANY, 'Claron')
        self.plh = imp.Append(wx.ID_ANY, 'Polhemus')
        self.debug = imp.Append(wx.ID_ANY, 'Debug')
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
        #self.widget.RemoveObservers('LeftButtonPressEvent')

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
        self.Bind(wx.EVT_MENU, self.oncoil, self.coil)
        self.Bind(wx.EVT_MENU, self.onbrain, self.brain)
        self.Bind(wx.EVT_MENU, self.ondelOBJ, self.delOBJ)
        self.Bind(wx.EVT_MENU, self.onplh, self.plh)
        self.Bind(wx.EVT_MENU, self.onmtc, self.mtc)
        self.Bind(wx.EVT_MENU, self.ondebug, self.debug)
        self.Bind(wx.EVT_MENU, self.onStop, self.stop)

        #create axes
        # axes = vtk.vtkAxesActor()
        # self.marker = vtk.vtkOrientationMarkerWidget()
        # self.marker.SetInteractor(self.widget._Iren)
        # self.marker.SetOrientationMarker(axes)
        # self.marker.SetViewport(0.75, 0, 1, 0.25)
        # self.marker.SetEnabled(1)

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

    def oncoil(self, evt):
        # Create a line
        filename = "bobina1.stl"

        reader = vtk.vtkSTLReader()
        reader.SetFileName(filename)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())
        self.coilactor = vtk.vtkActor()
        self.coilactor.SetMapper(mapper)
        self.coilactor.RotateX(-60)
        self.coilactor.RotateZ(180)
        #self.coilactor.GetProperty().SetOpacity(0.7)

        self.coilactor2 = vtk.vtkActor()
        self.coilactor2.SetMapper(mapper)
        self.coilactor2.SetPosition(0, -150, 00)
        self.coilactor2.RotateZ(180)
        #self.coilactor2.GetProperty().SetOpacity(0.7)

        self.coilactor3 = vtk.vtkActor()
        self.coilactor3.SetMapper(mapper)
        self.coilactor3.SetPosition(0, -300, 0)
        self.coilactor3.RotateY(90)
        self.coilactor3.RotateZ(180)
        #self.coilactor3.GetProperty().SetOpacity(0.7)

        self.arrowactorZ1 = c.arrow([-50,-35,12], [-50,-35,50])
        self.arrowactorZ1.GetProperty().SetColor(0, 0, 1)
        self.arrowactorZ1.RotateX(-60)
        self.arrowactorZ1.RotateZ(180)
        self.arrowactorZ2 = c.arrow([50,-35,0], [50,-35,-50])
        self.arrowactorZ2.GetProperty().SetColor(0, 0, 1)
        self.arrowactorZ2.RotateX(-60)
        self.arrowactorZ2.RotateZ(180)

        self.arrowactorY1 = c.arrow([-50,-35,0], [-50,5,0])
        self.arrowactorY1.GetProperty().SetColor(0, 1, 0)
        self.arrowactorY1.SetPosition(0, -150, 0)
        self.arrowactorY1.RotateZ(180)
        self.arrowactorY2 = c.arrow([50,-35,0], [50,-75,0])
        self.arrowactorY2.GetProperty().SetColor(0, 1, 0)
        self.arrowactorY2.SetPosition(0, -150, 0)
        self.arrowactorY2.RotateZ(180)

        self.arrowactorX1 = c.arrow([0, 65, 38], [0, 65, 68])
        self.arrowactorX1.GetProperty().SetColor(1, 0, 0)
        self.arrowactorX1.SetPosition(0, -300, 0)
        self.arrowactorX1.RotateY(90)
        self.arrowactorX1.RotateZ(180)
        self.arrowactorX2 = c.arrow([0, -55, 5], [0, -55, -30])
        self.arrowactorX2.GetProperty().SetColor(1, 0, 0)
        self.arrowactorX2.SetPosition(0, -300, 0)
        self.arrowactorX2.RotateY(90)
        self.arrowactorX2.RotateZ(180)

        self.ren.AddActor(self.coilactor)
        self.ren2.AddActor(self.coilactor)
        self.ren.AddActor(self.arrowactorZ1)
        self.ren.AddActor(self.arrowactorZ2)
        self.ren.AddActor(self.coilactor2)
        self.ren.AddActor(self.arrowactorY1)
        self.ren.AddActor(self.arrowactorY2)
        self.ren.AddActor(self.coilactor3)
        self.ren.AddActor(self.arrowactorX1)
        self.ren.AddActor(self.arrowactorX2)
        #create axes
        # self.assembly = vtk.vtkAssembly()
        # self.assembly.AddPart(self.coilactor)
        # self.assembly.AddPart(self.coilactor)
        # self.assembly.AddPart(self.arrowactorZ1)
        # self.assembly.AddPart(self.arrowactorZ2)
        # self.assembly.AddPart(self.coilactor2)
        # self.assembly.AddPart(self.arrowactorY1)
        # self.assembly.AddPart(self.arrowactorY2)
        # self.assembly.AddPart(self.coilactor3)
        # self.assembly.AddPart(self.arrowactorX1)
        # self.assembly.AddPart(self.arrowactorX2)


        # self.coil_box = vtk.vtkOrientationMarkerWidget()
        # self.coil_box.SetInteractor(self.widget._Iren)
        # self.coil_box.SetOrientationMarker(self.assembly)
        # self.coil_box.SetViewport(0.75, 0, 1, 0.25)
        # self.coil_box.SetEnabled(1)

        self.ren.ResetCamera()
        self.ren2.ResetCamera()
        #self.ren.Camera(0)

        # Render the scene
        self.widget.Render()

        self.menuTrackers.Enable(True)
        self.obj.Enable(False)
        self.delOBJ.Enable(True)

        self.OBJ_ID = 2

    def onbrain(self, evt):
        self.ren.SetViewport(0, 0, 0.75, 1)

        self.ren2 = vtk.vtkRenderer()

        self.widget.GetRenderWindow().AddRenderer(self.ren2)
        self.ren2.SetViewport(0.75, 0, 1,1)
        filename = "c101_MRI_clean_2.obj"

        reader = vtk.vtkOBJReader()
        reader.SetFileName(filename)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())
        self.brainactor = vtk.vtkActor()
        self.brainactor.SetMapper(mapper)
        self.ren.AddActor(self.brainactor)
        target = [151.4, -113, 176.8]
        sphere = c.sphere(target, 5, [1, 0, 0])
        self.ren.AddActor(sphere)

        # ------------------------------- Create plane

        # calculating a plane
        scale = vtk.vtkTransform()
        scale.Scale(1, 1, 1)
        filter = vtk.vtkTransformPolyDataFilter()
        filter.SetInputConnection(reader.GetOutputPort())
        filter.SetTransform(scale)
        filter.Update()

        surface = filter.GetOutput()

        pTarget = self.CenterOfMass(surface)
        v3, M_plane_inv = self.Plane(target, pTarget)

        mat4x4 = vtk.vtkMatrix4x4()
        for i in range(4):
            mat4x4.SetElement(i, 0, M_plane_inv[i][0])
            mat4x4.SetElement(i, 1, M_plane_inv[i][1])
            mat4x4.SetElement(i, 2, M_plane_inv[i][2])
            mat4x4.SetElement(i, 3, M_plane_inv[i][3])

        # plane for visualization.
        plane = vtk.vtkPlaneSource()
        plane.SetCenter(target)
        plane.SetNormal(v3)
        plane.Update()

        filename = "bobina1_dummy2.stl"

        reader = vtk.vtkSTLReader()
        reader.SetFileName(filename)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        #Plane
        # # Create four points (must be in counter clockwise order)
        # p0 = [-1.0, -1.0, 0.0]
        # p1 = [-1.0, 1.0, 0.0]
        # p2 = [1.0, 1.0, 0.0]
        # p3 = [1.0, -1.0, 0.0]
        # # Add the points to a vtkPoints object
        # points = vtk.vtkPoints()
        # points.InsertNextPoint(p0)
        # points.InsertNextPoint(p1)
        # points.InsertNextPoint(p2)
        # points.InsertNextPoint(p3)
        # # Create a quad on the four points
        # quad = vtk.vtkQuad()
        # quad.GetPointIds().SetId(0, 0)
        # quad.GetPointIds().SetId(1, 1)
        # quad.GetPointIds().SetId(2, 2)
        # quad.GetPointIds().SetId(3, 3)
        # # Create a cell array to store the quad in
        # quads = vtk.vtkCellArray()
        # quads.InsertNextCell(quad)
        # # Create a polydata to store everything in
        # polydata = vtk.vtkPolyData()
        # # Add the points and quads to the dataset
        # polydata.SetPoints(points)
        # polydata.SetPolys(quads)
        # # Setup actor and mapper
        # mapper = vtk.vtkPolyDataMapper()
        # mapper.SetInputData(polydata)

        # Transform the polydata
        transform = vtk.vtkTransform()
        transform.SetMatrix(mat4x4)
        transform.Scale(1, 1, 1)
        #transform.RotateWXYZ(180, 0, 1, 0)
        transformPD = vtk.vtkTransformPolyDataFilter()
        transformPD.SetTransform(transform)
        transformPD.SetInputConnection(reader.GetOutputPort())
        transformPD.Update()
        # mapper transform
        mapper.SetInputConnection(transformPD.GetOutputPort())

        coil_dummy = vtk.vtkActor()
        coil_dummy.SetMapper(mapper)
        coil_dummy.GetProperty().SetColor(1,1,1)
        coil_dummy.GetProperty().SetOpacity(0.4)
        self.ren.AddActor(coil_dummy)

        filename = "aim.stl"

        reader = vtk.vtkSTLReader()
        reader.SetFileName(filename)
        # Apply the transforms arrow 1
        transform_1 = vtk.vtkTransform()
        transform_1.SetMatrix(mat4x4)

        # Create a mapper and actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        # Transform the polydata
        transformPD = vtk.vtkTransformPolyDataFilter()
        transformPD.SetTransform(transform_1)
        transformPD.SetInputConnection(reader.GetOutputPort())
        transformPD.Update()
        # mapper transform
        mapper.SetInputConnection(transformPD.GetOutputPort())

        self.aimactor = vtk.vtkActor()
        self.aimactor.SetMapper(mapper)
        self.aimactor.GetProperty().SetColor(0, 0, 1)
        self.ren.AddActor(self.aimactor)

        #set camera
        self.ren.ResetCamera()
        cam_focus = target
        cam = self.ren.GetActiveCamera()
        initial_focus = np.array(cam.GetFocalPoint())
        cam_pos0 = np.array(cam.GetPosition())
        cam_focus0 = np.array(cam.GetFocalPoint())
        v0 = cam_pos0 - cam_focus0
        v0n = np.sqrt(inner1d(v0, v0))

        v1 = (cam_focus - initial_focus)
        v1n = np.sqrt(inner1d(v1, v1))
        if not v1n:
            v1n = 1.0
        cam_pos = (v1 / v1n) * v0n + cam_focus
        cam.SetFocalPoint(cam_focus)
        cam.SetPosition(cam_pos)

        filename = "bobina1.stl"

        reader = vtk.vtkSTLReader()
        reader.SetFileName(filename)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())
        self.coilactor = vtk.vtkActor()
        self.coilactor.SetMapper(mapper)
        self.coilactor.RotateX(-60)
        self.coilactor.RotateZ(180)
        #self.coilactor.GetProperty().SetOpacity(0.7)

        self.coilactor2 = vtk.vtkActor()
        self.coilactor2.SetMapper(mapper)
        self.coilactor2.SetPosition(0, -150, 0)
        self.coilactor2.RotateZ(180)
        #self.coilactor2.GetProperty().SetOpacity(0.7)

        self.coilactor3 = vtk.vtkActor()
        self.coilactor3.SetMapper(mapper)
        self.coilactor3.SetPosition(0, -300, 0)
        self.coilactor3.RotateY(90)
        self.coilactor3.RotateZ(180)
        #self.coilactor3.GetProperty().SetOpacity(0.7)

        self.arrowactorZ1 = c.arrow([-50,-35,12], [-50,-35,50])
        self.arrowactorZ1.GetProperty().SetColor(0, 0, 1)
        self.arrowactorZ1.RotateX(-60)
        self.arrowactorZ1.RotateZ(180)
        self.arrowactorZ2 = c.arrow([50,-35,0], [50,-35,-50])
        self.arrowactorZ2.GetProperty().SetColor(0, 0, 1)
        self.arrowactorZ2.RotateX(-60)
        self.arrowactorZ2.RotateZ(180)

        self.arrowactorY1 = c.arrow([-50,-35,0], [-50,5,0])
        self.arrowactorY1.GetProperty().SetColor(0, 1, 0)
        self.arrowactorY1.SetPosition(0, -150, 0)
        self.arrowactorY1.RotateZ(180)
        self.arrowactorY2 = c.arrow([50,-35,0], [50,-75,0])
        self.arrowactorY2.GetProperty().SetColor(0, 1, 0)
        self.arrowactorY2.SetPosition(0, -150, 0)
        self.arrowactorY2.RotateZ(180)

        self.arrowactorX1 = c.arrow([0, 65, 38], [0, 65, 68])
        self.arrowactorX1.GetProperty().SetColor(1, 0, 0)
        self.arrowactorX1.SetPosition(0, -300, 0)
        self.arrowactorX1.RotateY(90)
        self.arrowactorX1.RotateZ(180)
        self.arrowactorX2 = c.arrow([0, -55, 5], [0, -55, -30])
        self.arrowactorX2.GetProperty().SetColor(1, 0, 0)
        self.arrowactorX2.SetPosition(0, -300, 0)
        self.arrowactorX2.RotateY(90)
        self.arrowactorX2.RotateZ(180)

        self.ren2.AddActor(self.coilactor)
        self.ren2.AddActor(self.arrowactorZ1)
        self.ren2.AddActor(self.arrowactorZ2)
        self.ren2.AddActor(self.coilactor2)
        self.ren2.AddActor(self.arrowactorY1)
        self.ren2.AddActor(self.arrowactorY2)
        self.ren2.AddActor(self.coilactor3)
        self.ren2.AddActor(self.arrowactorX1)
        self.ren2.AddActor(self.arrowactorX2)


        self.ren2.ResetCamera()

        # Render the scene
        self.widget.Render()

        self.menuTrackers.Enable(True)
        self.obj.Enable(False)
        self.delOBJ.Enable(True)

        self.OBJ_ID = 3

    def CenterOfMass(self, surface):
        barycenter = [0.0,0.0,0.0]
        n = surface.GetNumberOfPoints()
        for i in range(n):
            point = surface.GetPoint(i)
            barycenter[0] += point[0]
            barycenter[1] += point[1]
            barycenter[2] += point[2]
        barycenter[0] /= n
        barycenter[1] /= n
        barycenter[2] /= n

        return barycenter

    def Plane(self, x0, pTarget):
        v3 = np.array(pTarget) - x0  # normal to the plane
        v3 = v3 / np.linalg.norm(v3)  # unit vector

        d = np.dot(v3, x0)
        # prevents division by zero.
        if v3[0] == 0.0:
            v3[0] = 1e-09

        x1 = np.array([(d - v3[1] - v3[2]) / v3[0], 1, 1])
        v2 = x1 - x0
        v2 = v2 / np.linalg.norm(v2)  # unit vector
        v1 = np.cross(v3, v2)
        v1 = v1 / np.linalg.norm(v1)  # unit vector
        x2 = x0 + v1
        # calculates the matrix for the change of coordinate systems (from canonical to the plane's).
        # remember that, in np.dot(M,p), even though p is a line vector (e.g.,np.array([1,2,3])), it is treated as a column for the dot multiplication.
        M_plane_inv = np.array([[v1[0], v2[0], v3[0], x0[0]],
                                [v1[1], v2[1], v3[1], x0[1]],
                                [v1[2], v2[2], v3[2], x0[2]],
                                [0, 0, 0, 1]])

        return v3, M_plane_inv

    def ondelOBJ(self, evt):
        if self.OBJ_ID == 0:
            self.ren.RemoveActor(self.ball_actorP)
            self.ren.RemoveActor(self.arrow)
        elif self.OBJ_ID == 1:
            self.ren.RemoveActor(self.lineActor)
        elif self.OBJ_ID == 2:
            self.ren.RemoveActor(self.coilactor)
            self.ren.RemoveActor(self.coilactor2)
            self.ren.RemoveActor(self.coilactor3)
            self.ren.RemoveActor(self.arrowactorX1)
            self.ren.RemoveActor(self.arrowactorX2)
            self.ren.RemoveActor(self.arrowactorY1)
            self.ren.RemoveActor(self.arrowactorY2)
            self.ren.RemoveActor(self.arrowactorZ1)
            self.ren.RemoveActor(self.arrowactorZ2)
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

    def ondebug(self, evt):
        self.tracker_init = 'debug'
        self.stop_flag = 1
        tck = 'debug'
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
        if self.OBJ_ID == 2:
            self.ren.RemoveActor(self.arrowactorZ1)
            self.assembly.RemovePart(self.arrowactorZ1)
            self.ren.RemoveActor(self.arrowactorZ2)
            self.assembly.RemovePart(self.arrowactorZ2)
            offset = 5
            self.arrowactorZ1 = c.arrow([-55, -35, offset], [-55, -35, offset + coord])
            self.arrowactorZ1.RotateX(-60)
            self.arrowactorZ1.RotateZ(180)
            self.arrowactorZ2 = c.arrow([55, -35, offset], [55, -35, offset - coord])
            if coord == 0:
                self.coilactor.GetProperty().SetColor(0, 1, 0)
            else:
                self.coilactor.GetProperty().SetColor(1, 1, 1)
            self.arrowactorZ2.RotateX(-60)
            self.arrowactorZ2.RotateZ(180)
            self.ren.AddActor(self.arrowactorZ1)
            self.assembly.AddPart(self.arrowactorZ1)
            self.ren.AddActor(self.arrowactorZ2)
            self.assembly.AddPart(self.arrowactorZ2)

            self.ren.RemoveActor(self.arrowactorY1)
            self.assembly.RemovePart(self.arrowactorY1)
            self.ren.RemoveActor(self.arrowactorY2)
            self.assembly.RemovePart(self.arrowactorY2)
            offset = -35
            self.arrowactorY1 = c.arrow([-55, offset, 0], [-55, offset + coord, 0])
            self.arrowactorY2 = c.arrow([55, offset, 0], [55, offset - coord, 0])
            self.arrowactorY1.SetPosition(0, -150, 0)
            self.arrowactorY1.RotateZ(180)
            self.arrowactorY1.GetProperty().SetColor(0, 1, 0)
            self.arrowactorY2.SetPosition(0, -150, 0)
            self.arrowactorY2.RotateZ(180)
            self.arrowactorY2.GetProperty().SetColor(0, 1, 0)
            self.ren.AddActor(self.arrowactorY1)
            self.assembly.AddPart(self.arrowactorY1)
            self.ren.AddActor(self.arrowactorY2)
            self.assembly.AddPart(self.arrowactorY2)

            self.ren.RemoveActor(self.arrowactorX1)
            self.assembly.RemovePart(self.arrowactorX1)
            self.ren.RemoveActor(self.arrowactorX2)
            self.assembly.RemovePart(self.arrowactorX2)
            offset = 38
            self.arrowactorX1 = c.arrow([0, 65, offset], [0, 65, offset + coord])
            offset = 5
            self.arrowactorX2 = c.arrow([0, -55, offset], [0, -55, offset - coord])
            self.arrowactorX1.SetPosition(0, -300, 0)
            self.arrowactorX1.RotateY(90)
            self.arrowactorX1.RotateZ(180)
            self.arrowactorX1.GetProperty().SetColor(1, 0, 0)
            self.arrowactorX2.SetPosition(0, -300, 0)
            self.arrowactorX2.RotateY(90)
            self.arrowactorX2.RotateZ(180)
            self.arrowactorX2.GetProperty().SetColor(1, 0, 0)
            self.ren.AddActor(self.arrowactorX1)
            self.assembly.AddPart(self.arrowactorX1)
            self.ren.AddActor(self.arrowactorX2)
            self.assembly.AddPart(self.arrowactorX2)
        self.widget.Render()
        #self.ren.ResetCamera()

# ----------------------------------------------------------------------------------------------


if __name__ == "__main__":
    app = wx.App(0)

    frame = MyFrame(None)

    frame.Show()

    app.MainLoop()