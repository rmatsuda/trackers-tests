import time
import threading
import wx
#requires the following import to works sendmessage args
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub as Publisher
class nav(threading.Thread):
    # Thread created to update the object coordinates
    # Sleep function in run method is used for better real-time navigation

    def __init__(self,nav, tracker_init, tck):
        threading.Thread.__init__(self)
        self.nav = nav
        self.tck = tck
        self.tracker_init = tracker_init
        self._pause_ = False
        self.start()

    def stop(self):
        self._pause_ = True
        self.tracker_init.Close()

    def run(self):
        inch2mm = 25.4
        x = 10.0
        y = 10.0
        z = -10.0
        i=0
        d=1
        while self.nav:
            if self.tck == "plh":
                plh = self.tracker_init
                plh.Run()
                coord = (plh.PositionTooltipX1, plh.PositionTooltipY1, plh.PositionTooltipZ1,
                         plh.AngleX1, plh.AngleY1, plh.AngleZ1)

                coord = (float(coord[0]) * inch2mm, float(coord[1]) * inch2mm,
                         float(coord[2]) * (-inch2mm), float(coord[3]),
                         float(coord[4]), float(coord[5]))
                wx.CallAfter(Publisher.sendMessage, 'Update Orientation', coord)
            elif self.tck == "mtc":
                mtc = self.tracker_init
                mtc.Run()
                coord = (mtc.PositionTooltipX1, mtc.PositionTooltipY1, mtc.PositionTooltipZ1,
                                  mtc.AngleX1, mtc.AngleY1, mtc.AngleZ1,
                         mtc.ProjectionCenterX / 10, mtc.ProjectionCenterY / 10, mtc.ProjectionCenterZ / 10,
                         mtc.ProjectionCableX / 10, mtc.ProjectionCableY / 10, mtc.ProjectionCableZ / 10)
                print mtc.PositionTooltipX1
                coord = (float(coord[0])*x, float(coord[1])*y,
                         float(coord[2])*z, float(coord[3]),
                         float(coord[4]), float(coord[5]),
                         float(coord[6])*x, float(coord[7])*y, float(coord[8])*z,
                     float(coord[9])*x, float(coord[10])*y, float(coord[11])*z)

                print coord
                wx.CallAfter(Publisher.sendMessage, 'Update Orientation', coord)
            elif self.tck == "debug":
                wx.CallAfter(Publisher.sendMessage, 'Update Orientation', i)
                if i<=50 and d==1:
                    i+=1
                    d=1
                elif i >= -50 and d == 0:
                    i -= 1
                    d = 0
                elif i>50:
                    d=0
                else:
                    d=1
                print d, i


            time.sleep(0.175)

            if self._pause_:
                return