"""
Copyright © 2023 Howard Hughes Medical Institute, Authored by Carsen Stringer and Marius Pachitariu.
Modified for Windows 11 styling enhancements.
"""
import numpy as np
import pyqtgraph as pg
from qtpy import QtCore
from pyqtgraph import Point
from pyqtgraph import functions as fn
from pyqtgraph.graphicsItems.ViewBox.ViewBoxMenu import ViewBoxMenu

from . import masks

# Define a global border color that matches your Windows 11 style palette
BORDER_COLOR = "#555555"  # Adjust this to match your chosen Windows 11 style

class TraceBox(pg.PlotItem):
    def __init__(self, parent=None, border=None, lockAspect=False, enableMouse=True,
                 invertY=False, enableMenu=True, name=None, invertX=False):
        super(TraceBox, self).__init__()
        self.parent = parent

    def mouseDoubleClickEvent(self, ev):
        self.zoom_plot()

    def zoom_plot(self):
        self.setXRange(0, self.parent.Fcell.shape[1])
        self.setYRange(self.parent.fmin, self.parent.fmax)
        self.parent.show()

class ViewBox(pg.ViewBox):
    def __init__(self, parent=None, border=None, lockAspect=False, enableMouse=True,
                 invertY=False, enableMenu=True, name=None, invertX=False):
        super(ViewBox, self).__init__()
        # Use the provided border or fallback to our global BORDER_COLOR
        if border is None:
            border = BORDER_COLOR
        self.border = fn.mkPen(border, width=1)
        if enableMenu:
            self.menu = ViewBoxMenu(self)
        self.name = name
        self.parent = parent
        if self.name == "plot2":
            self.setXLink(parent.p1)
            self.setYLink(parent.p1)

        # Set internal state flags
        self.state["enableMenu"] = enableMenu
        self.state["yInverted"] = invertY

    def mouseDoubleClickEvent(self, ev):
        if self.parent.loaded:
            self.zoom_plot()

    def mouseClickEvent(self, ev):
        if self.parent.loaded:
            pos = self.mapSceneToView(ev.scenePos())
            posy = int(pos.x())
            posx = int(pos.y())
            iplot = 0 if self.name == "plot1" else 1
            if posy >= 0 and posx >= 0 and posy <= self.parent.Lx and posx <= self.parent.Ly:
                ichosen = int(self.parent.rois["iROI"][iplot, 0, posx, posy])
                if ichosen < 0:
                    if ev.button() == QtCore.Qt.RightButton and self.menuEnabled():
                        self.raiseContextMenu(ev)
                    return
                else:
                    if ev.button() == QtCore.Qt.RightButton:
                        if ichosen not in self.parent.imerge:
                            self.parent.imerge = [ichosen]
                            self.parent.ichosen = ichosen
                        masks.flip_plot(self.parent)
                    else:
                        merged = False
                        if ev.modifiers() == QtCore.Qt.ShiftModifier or ev.modifiers() == QtCore.Qt.ControlModifier:
                            if self.parent.iscell[self.parent.imerge[0]] == self.parent.iscell[ichosen]:
                                if ichosen not in self.parent.imerge:
                                    self.parent.imerge.append(ichosen)
                                    self.parent.ichosen = ichosen
                                    merged = True
                                elif ichosen in self.parent.imerge and len(self.parent.imerge) > 1:
                                    self.parent.imerge.remove(ichosen)
                                    self.parent.ichosen = self.parent.imerge[0]
                                    merged = True
                        if not merged:
                            self.parent.imerge = [ichosen]
                            self.parent.ichosen = ichosen

                    if self.parent.isROI:
                        self.parent.ROI_remove()
                    if not self.parent.sizebtns.button(1).isChecked():
                        for btn in self.parent.topbtns.buttons():
                            if btn.isChecked():
                                btn.setStyleSheet(self.parent.styleUnpressed)
                    self.parent.update_plot()

    def zoom_plot(self):
        self.setXRange(0, self.parent.ops["Lx"])
        self.setYRange(0, self.parent.ops["Ly"])
        self.parent.p2.setXLink(self.parent.p1)
        self.parent.p2.setYLink(self.parent.p1)
        self.parent.show()

def init_range(parent):
    parent.p1.setXRange(0, parent.ops["Lx"])
    parent.p1.setYRange(0, parent.ops["Ly"])
    parent.p2.setXRange(0, parent.ops["Lx"])
    parent.p2.setYRange(0, parent.ops["Ly"])
    parent.p3.setLimits(xMin=0, xMax=parent.Fcell.shape[1])
    parent.trange = np.arange(0, parent.Fcell.shape[1])

def ROI_index(ops, stat):
    """Generate a matrix (Ly x Lx) where each pixel contains the ROI index (-1 if no ROI is present)."""
    ncells = len(stat) - 1
    Ly = ops["Ly"]
    Lx = ops["Lx"]
    iROI = -1 * np.ones((Ly, Lx), dtype=np.int32)
    for n in range(ncells):
        ypix = stat[n]["ypix"][~stat[n]["overlap"]]
        if ypix is not None:
            xpix = stat[n]["xpix"][~stat[n]["overlap"]]
            iROI[ypix, xpix] = n
    return iROI
