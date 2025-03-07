"""
Copyright © 2023 Howard Hughes Medical Institute, Authored by Carsen Stringer and Marius Pachitariu.
Cleaned-up version that relies on a global style sheet for Windows 11–inspired styling.
"""
import numpy as np
from qtpy import QtGui, QtCore
from qtpy.QtWidgets import QPushButton, QButtonGroup, QLabel, QLineEdit

def make_selection(parent):
    """Creates buttons for drawing a square on view."""
    parent.topbtns = QButtonGroup()
    ql = QLabel("select cells")
    ql.setFont(QtGui.QFont("Arial", 8, QtGui.QFont.Bold))
    parent.l0.addWidget(ql, 0, 2, 1, 2)
    pos = [2, 3, 4]
    for b in range(3):
        btn = TopButton(b, parent)
        btn.setFont(QtGui.QFont("Arial", 8))
        parent.topbtns.addButton(btn, b)
        parent.l0.addWidget(btn, 0, pos[b] * 2, 1, 2)
        btn.setEnabled(False)
    parent.topbtns.setExclusive(True)
    parent.isROI = False
    parent.ROIplot = 0

    ql = QLabel("n=")
    ql.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    ql.setFont(QtGui.QFont("Arial", 8, QtGui.QFont.Bold))
    parent.l0.addWidget(ql, 0, 10, 1, 1)

    parent.topedit = QLineEdit(parent)
    parent.topedit.setValidator(QtGui.QIntValidator(0, 500))
    parent.topedit.setText("40")
    parent.ntop = 40
    parent.topedit.setFixedWidth(35)
    parent.topedit.setAlignment(QtCore.Qt.AlignRight)
    parent.topedit.returnPressed.connect(parent.top_number_chosen)
    parent.l0.addWidget(parent.topedit, 0, 11, 1, 1)

def make_cellnotcell(parent):
    """Creates buttons for cell / not cell views at the top."""
    parent.lcell0 = QLabel("")
    parent.lcell0.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    parent.l0.addWidget(parent.lcell0, 0, 12, 1, 2)
    parent.lcell1 = QLabel("")
    parent.l0.addWidget(parent.lcell1, 0, 20, 1, 2)

    parent.sizebtns = QButtonGroup(parent)
    labels = [" cells", " both", " not cells"]
    for b, l in enumerate(labels):
        btn = SizeButton(b, l, parent)
        parent.sizebtns.addButton(btn, b)
        parent.l0.addWidget(btn, 0, 14 + 2 * b, 1, 2)
        btn.setEnabled(False)
        if b == 1:
            btn.setEnabled(True)
    parent.sizebtns.setExclusive(True)

def make_quadrants(parent):
    """Creates quadrant buttons."""
    parent.quadbtns = QButtonGroup(parent)
    for b in range(9):
        btn = QuadButton(b, " " + str(b + 1), parent)
        parent.quadbtns.addButton(btn, b)
        parent.l0.addWidget(btn, parent.quadbtns.button(b).ypos,
                            29 + parent.quadbtns.button(b).xpos, 1, 1)
        btn.setEnabled(False)
    parent.quadbtns.setExclusive(True)

class QuadButton(QPushButton):
    """Custom QPushButton for quadrant plotting."""
    def __init__(self, bid, Text, parent=None):
        super(QuadButton, self).__init__(parent)
        self.setText(Text)
        self.setCheckable(True)
        self.setFont(QtGui.QFont("Arial", 8, QtGui.QFont.Bold))
        self.resize(self.minimumSizeHint())
        self.setMaximumWidth(22)
        self.xpos = bid % 3
        self.ypos = int(np.floor(bid / 3))
        self.clicked.connect(lambda: self.press(parent, bid))
        self.show()

    def press(self, parent, bid):
        # Clear all buttons before setting this one checked.
        for b in range(9):
            if parent.quadbtns.button(b).isEnabled():
                parent.quadbtns.button(b).setChecked(False)
        self.setChecked(True)
        self.xrange = np.array([self.xpos - 0.15, self.xpos + 1.15]) * parent.ops["Lx"] / 3
        self.yrange = np.array([self.ypos - 0.15, self.ypos + 1.15]) * parent.ops["Ly"] / 3
        parent.p1.setXRange(self.xrange[0], self.xrange[1])
        parent.p1.setYRange(self.yrange[0], self.yrange[1])
        parent.p2.setXRange(self.xrange[0], self.xrange[1])
        parent.p2.setYRange(self.yrange[0], self.yrange[1])
        parent.p2.setXLink("plot1")
        parent.p2.setYLink("plot1")
        parent.show()

class SizeButton(QPushButton):
    """Button for adjusting the trace box size."""
    def __init__(self, bid, Text, parent=None):
        super(SizeButton, self).__init__(parent)
        self.setText(Text)
        self.setCheckable(True)
        self.setFont(QtGui.QFont("Arial", 8, QtGui.QFont.Bold))
        self.resize(self.minimumSizeHint())
        self.clicked.connect(lambda: self.press(parent))
        self.bid = bid
        self.show()

    def press(self, parent):
        # Uncheck all size buttons and check this one.
        for btn in parent.sizebtns.buttons():
            btn.setChecked(False)
        self.setChecked(True)
        ts = 100
        if self.bid == 0:
            parent.p2.linkView(parent.p2.XAxis, view=None)
            parent.p2.linkView(parent.p2.YAxis, view=None)
            parent.win.ci.layout.setColumnStretchFactor(0, ts)
            parent.win.ci.layout.setColumnStretchFactor(1, 0)
        elif self.bid == 1:
            parent.win.ci.layout.setColumnStretchFactor(0, ts)
            parent.win.ci.layout.setColumnStretchFactor(1, ts)
            parent.p2.setXLink("plot1")
            parent.p2.setYLink("plot1")
        elif self.bid == 2:
            parent.p2.linkView(parent.p2.XAxis, view=None)
            parent.p2.linkView(parent.p2.YAxis, view=None)
            parent.win.ci.layout.setColumnStretchFactor(0, 0)
            parent.win.ci.layout.setColumnStretchFactor(1, ts)
        if self.bid != 1:
            if parent.ops_plot["color"] != 0:
                for btn in parent.topbtns.buttons():
                    btn.setEnabled(True)
            else:
                parent.topbtns.button(0).setEnabled(True)
        else:
            parent.ROI_remove()
            for btn in parent.topbtns.buttons():
                btn.setEnabled(False)
        parent.win.show()
        parent.show()

class TopButton(QPushButton):
    """Button for selecting top neurons."""
    def __init__(self, bid, parent=None):
        super(TopButton, self).__init__(parent)
        texts = [" draw selection", " select top n", " select bottom n"]
        self.bid = bid
        self.setText(texts[bid])
        self.setCheckable(True)
        self.setFont(QtGui.QFont("Arial", 8, QtGui.QFont.Bold))
        self.resize(self.minimumSizeHint())
        self.clicked.connect(lambda: self.press(parent))
        self.show()

    def press(self, parent):
        if not parent.sizebtns.button(1).isChecked():
            if parent.ops_plot["color"] == 0:
                for b in [1, 2]:
                    parent.topbtns.button(b).setEnabled(False)
            else:
                for b in [1, 2]:
                    parent.topbtns.button(b).setEnabled(True)
        else:
            for b in range(3):
                parent.topbtns.button(b).setEnabled(False)
        self.setChecked(True)
        if self.bid == 0:
            parent.ROI_selection()
        else:
            self.top_selection(parent)

    def top_selection(self, parent):
        parent.ROI_remove()
        ncells = len(parent.stat)
        icells = np.minimum(ncells, parent.ntop)
        top = (self.bid == 1)
        draw = False
        if parent.sizebtns.button(0).isChecked():
            wplot = 0
            draw = True
        elif parent.sizebtns.button(2).isChecked():
            wplot = 1
            draw = True
        if draw:
            if parent.ops_plot["color"] != 0:
                c = parent.ops_plot["color"]
                istat = parent.colors["istat"][c]
                if wplot == 0:
                    icell = np.array(parent.iscell.nonzero()).flatten()
                    istat = istat[parent.iscell]
                else:
                    icell = np.array((~parent.iscell).nonzero()).flatten()
                    istat = istat[~parent.iscell]
                inds = istat.argsort()
                if top:
                    inds = inds[-icells:]
                    parent.ichosen = icell[inds[-1]]
                else:
                    inds = inds[:icells]
                    parent.ichosen = icell[inds[0]]
                parent.imerge = list(icell[inds])
                parent.update_plot()
                parent.show()
