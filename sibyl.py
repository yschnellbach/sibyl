#!/usr/bin/env python3
import sys
import signal
import json
import numpy as np
import matplotlib.cm as cm
import argparse
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import rat
import ROOT
import ctypes as ct
from PyQt5 import QtGui, QtCore
import _thread
from sibyl_python import *

## Some matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

''' -- Sibyl Event Viewer
|------------------------------------------|
|Main|Crate|...|                           |
|------------------------------------------|
|         --         |                     |
|        -  -        |                     |
|         --         |                     |
| ------------------ |                     |
| |                | |----------|----------|
| |________________| |          |          |          |
|         --         |          |
|        -  -        |          |          |
|         --         |          |          |
|------------------------------------------|
'''

class MainWindow(QtGui.QWidget):
    '''
    Order of operations:
    1. Create the main window
    2. Create grid layout
    3. Open the ratroot file to get information and store event info
    '''
    App = None
    plot = None
    colorMask = 'Charge'
    isLog = False

    ''' Set by rat '''
    entries = 999

    def __init__(self, fname, app=None):
        self.fname = fname
        if self.App is None:
            if app is not None:
                self.App = app
            else:
                self.App = QtGui.QApplication([])
        super(MainWindow,self).__init__()
        self.beginRat()
        self.buildLayout()

    def buildLayout(self):
        formGroupBox = QtGui.QGroupBox()
        formLayout = QtGui.QFormLayout()
        # Main layout = QtGui.QGridLayout()
        self.layout = QtGui.QGridLayout()
        # Events
        self.total_events_line = QtGui.QLineEdit("0")
        self.total_events_line.setReadOnly(True)
        self.total_events_line.setText(str(self.entries))
        formLayout.addRow(QtGui.QLabel("Total Events"), self.total_events_line)
        ## Event switcher buttons
        left_button = QtGui.QPushButton("<")
        left_button.clicked.connect(self.leftEvent)
        right_button = QtGui.QPushButton(">")
        right_button.clicked.connect(self.rightEvent)
        self.event = QtGui.QLineEdit("0")
        self.event.textChanged.connect(self.newEvent)
        self.hboxchooser = QtGui.QHBoxLayout()
        self.hboxchooser.addWidget(left_button)
        self.hboxchooser.addWidget(right_button)
        self.hboxchooser.addWidget(self.event)
        formLayout.addRow(self.hboxchooser)

        ## Choose charge mode
        chargeTime_button = QtGui.QPushButton("Q/T Toggle")
        chargeTime_button.clicked.connect(self.toggleColorMode)
        self.hboxchooser.addWidget(chargeTime_button)

        ## Put form together
        formGroupBox.setLayout(formLayout)
        ## Top bar:
        self.layout.addWidget(formGroupBox,0,0,1,16)
        ## EV Info panel
        self.pFig = Figure()
        self.figCanvas = FigureCanvas(self.pFig)
        #evinfoGroupBox = QtGui.QGroupBox()
        self.layout.addWidget(self.figCanvas,6,12,3,4)
        #self.layout.addWidget(evinfoGroupBox,6,12,3,4)

        ## Histogram
        #histGroupBox = QtGui.QGroupBox()
        self.plotHistogram = pg.PlotWidget(name='Histogram')
        self.plotHistogram.setLimits(xMin=0, yMin=0)
        self.layout.addWidget(self.plotHistogram,6,8,3,4)

        # Flat-map goes here
        self.flatMapWindow = gl.GLViewWidget()
        self.flatMapWindow.opts['elevation'] = 90 
        self.flatMapWindow.opts['distance'] = 35000
        self.flatMapWindow.opts['azimuth'] = -90 
        print(self.flatMapWindow.opts)

        ## Now the 3D graph
        self.plot3DView = gl.GLScatterPlotItem(pxMode=False)
        self.plotTracks = gl.GLLinePlotItem(mode='lines', color=(1,0,0,0.1))
        self.plotFlatMap = gl.GLScatterPlotItem(pxMode=False, size=300)
        self.newEvent()
        self.glWin = Sibyl3DViewer(self.plot3DView, self.plotTracks, self.App)
        #self.layout.addWidget(self.glWin,1,0,4,1)
        self.flatMapWindow.addItem(self.plotFlatMap)
        self.layout.addWidget(self.flatMapWindow,1,0,8,8)
        self.layout.addWidget(self.glWin,1,8,5,8)

        # Fake 3d-2d
        #evinfoGroupBox = QtGui.QGroupBox()



        # Fix the column and row stretch
        for r in range(9):
            self.layout.setRowStretch(r, 1)
        for c in range(16):
            self.layout.setColumnStretch(c, 1)
        self.setLayout(self.layout)
        self.show()

    def toggleColorMode(self):
        if self.colorMask == 'charge':
            self.colorMask = 'time'
        else:
            self.colorMask = 'charge'
        self.drawEvent()

    def leftEvent(self):
        min_event = 0
        cur_event = int(self.event.text())
        if cur_event > (min_event):
            cur_event -= 1
        self.event.setText(str(cur_event))

    def rightEvent(self):
        max_event = int(self.total_events_line.text())
        cur_event = int(self.event.text())
        if cur_event < (max_event-1):
            cur_event += 1
        self.event.setText(str(cur_event))

    def updateEvent(self):
        self.readRat()
        self.readRatTracking()
        self.drawEvent()

    def newEvent(self):
        min_event, max_event = 0, int(self.total_events_line.text())
        try:
            cur_event = int(self.event.text())
        except ValueError:
            self.event.setText("0")
            cur_event = int(self.event.text())
        if (cur_event >= min_event) and (cur_event < max_event):
            self.updateEvent()
        else:
            self.event.setText("0")

    ## Rat, moveme to rat class
    def beginRat(self):
        self.ds = rat.RAT.DSReader(self.fname)
        f = ROOT.TFile(self.fname)
        t = f.Get('runT')
        self.run = rat.RAT.DS.Run()
        t.SetBranchAddress('run', ROOT.AddressOf(self.run))
        t.GetEntry(0)
        self.pmt_info = self.run.GetPMTInfo()
        self.entries = self.ds.GetTotal()
        dprint('Total entries:', self.entries)

    def readRat(self):
        event =int(self.event.text())
        thisEvent = self.ds.GetEvent(event)
        allpmt = self.pmt_info.GetPMTCount()
        self.posArray = np.zeros((allpmt, 3))
        self.pmtidArray = np.zeros((allpmt))
        self.CHARGE = np.zeros((allpmt))-100
        self.TIME = np.zeros((allpmt))-100
        self.plWeights = np.zeros((allpmt)) + 100#3 is minimum point size?
        for pmt_id in range(allpmt):
            pmtx = self.pmt_info.GetPosition(pmt_id).X()
            pmty = self.pmt_info.GetPosition(pmt_id).Y()
            pmtz = self.pmt_info.GetPosition(pmt_id).Z()
            self.pmtidArray[pmt_id] = pmt_id
            self.posArray[pmt_id] = np.array([pmtx, pmty, pmtz])
        if thisEvent.GetEVCount() <= 0:
            return
        self.ev = thisEvent.GetEV(0)
        npmt = self.ev.GetPMTCount()

        for pmt in range(npmt):
            thispmt = self.ev.GetPMT(pmt)
            pid = thispmt.GetID()
            self.CHARGE[pid] = thispmt.GetCharge()
            self.TIME[pid] = thispmt.GetTime()
            # if hit increase weight
            self.plWeights[pid] = 300

    def readRatTracking(self):
        # Clear last event
        event = int(self.event.text())
        mc = self.ds.GetEvent(event).GetMC()
        nTracks = mc.GetMCTrackCount()
        # Colors based on: ID and Process if optical
        # Yellow: electron
        clr_electron = (1, 1, 0, 1.0)
        # Green: Gamma
        clr_gamma = (0, 1, 0, 1.0)
        # Cherenkov: Blue
        clr_cerenkov = (0, 0.5, 1.0, 0.1)
        # Scintillation: Pink
        clr_scint = (1, 0, 0.5, 0.1)
        clr_reim = (0, 0, 1, 0.1)
        clr_dict = {'e-':clr_electron,
                    'gamma':clr_gamma,
                    'Cerenkov':clr_cerenkov,
                    'Scintillation':clr_scint,
                    'Reemission':clr_scint}
        clr_other = (0.7, 0.7, 0.8, 0.1)
        clr_list = []
        nlist = []
        for trk in range(nTracks):
            track = mc.GetMCTrack(trk)
            name = track.GetParticleName()
            if name == 'opticalphoton':
                name = track.GetMCTrackStep(0).GetProcess()
            nSteps = track.GetMCTrackStepCount()
            # A path consists of steps-1 segments:
            path = []
            for stp in range(nSteps):
                step = track.GetMCTrackStep(stp)
                tv = step.GetEndpoint()
                x, y, z = tv.X(), tv.Y(), tv.Z()
                path.append( (x, y, z) )
            x, y, z = np.array(path).T
            xx = np.roll(np.repeat(x, 2), -1)[:-2]
            yy = np.roll(np.repeat(y, 2), -1)[:-2]
            zz = np.roll(np.repeat(z, 2), -1)[:-2]
            jj = np.array([xx, yy, zz]).T
            if name in clr_dict:
                color_choice = clr_dict[name]
            else:
                color_choice = clr_other
            clr_list.append( np.array([color_choice for i in range(len(jj))]) )
            nlist.append(jj)
        if len(nlist) > 0:
            tarray = np.concatenate(nlist)
            carray = np.concatenate(clr_list)
            self.plotTracks.pos = tarray
            self.plotTracks.color = carray

    def addPMT(self, pmtpos):
        self.posArray = np.append(self.posArray, np.array([pmtpos]), axis=0)

    def drawEvent(self):
        self.colorize()
        ## 3D Viewport
        if self.plot3DView is None:
            self.plot3DView = gl.GLScatterPlotItem(pos=self.posArray,
                    color=self.colorArray, size=self.plWeights, pxMode=False)
        else:
            self.plot3DView.pos = self.posArray
            self.plot3DView.color = self.colorArray
            self.plot3DView.size = self.plWeights
            self.plot3DView.update()

        ## Histogram
        self.plotHistogram.clear()
        hy,hx = np.histogram(self.CHARGE[self.CHARGE>0], bins=100)
        #for x,y in zip(hx[:-1], hy):
        #    self.plotHistogram.plot([x,x+w], [y, y] )
        
        self.plotHistogram.plot(hx, hy, stepMode=True, fillLevel=0,
                brush=(0,0,255,150))
        ## Version-2
        ax = self.pFig.add_subplot(111)
        ax.plot(hx[1:], hy)

        ## Flat test
        posR = np.sum(self.posArray**2, axis=1)**0.5
        posX = (self.posArray.T)[0]
        posY = (self.posArray.T)[1]
        posZ = (self.posArray.T)[2]
        posRho = (posX**2 + posY**2)**0.5
        theta = np.arctan2(posX, posY) * posRho
        ## Move this to a detector class, but for now, arbitrarily define
        ## various regions.
        ## displace top and bottom
        zCut = 6300
        rCut = 6400
        vetoH = 6500
        flatSelect = (posZ<zCut)&(posZ>-zCut)&(posRho<rCut)
        flatPOS = np.array([theta[flatSelect], posZ[flatSelect], np.zeros(len(theta[flatSelect]))]).T
        flatCLR = self.colorArray[flatSelect]
        #brushes = self.colorArray[flatSelect].tolist()
        #brushes = [tuple(br) for br in brushes]
        #print(brushes[0])
        # Flat region
        #self.plotFlatMap.plot(theta[flatSelect], posZ[flatSelect], pen=None, 
        #        symbol='o')
                #symbolBrushes=[pg.mkBrush(br) for br in brushes] )
        # Top Circle
        topSelect = (posZ>=zCut)&(posZ<vetoH)
        topShift = zCut*2.1 #1.5
        topX, topY = posX[topSelect], -posY[topSelect] + topShift
        topPOS = np.array([topX, topY, np.zeros(len(topX))]).T
        topCLR = self.colorArray[topSelect]
        #self.plotFlatMap.setData(x=topX, y=topY, z=self.CHARGE[topSelect])
        #self.plotFlatMap.update()
        #self.plotFlatMap.plot(topX, topY, pen=None, symbol='o')
        # Bot Circle
        botSelect = (posZ<=-zCut)&(posZ>-vetoH)
        botShift = -zCut*2.1 #1.5
        botX, botY = posX[botSelect], posY[botSelect] + botShift
        botPOS = np.array([botX, botY, np.zeros(len(botX))]).T
        botCLR = self.colorArray[botSelect]
        #self.plotFlatMap.plot(botX, botY, pen=None, symbol='o')

        totalPOS = np.concatenate([topPOS, botPOS, flatPOS])
        totalCLR = np.concatenate([topCLR, botCLR, flatCLR])

        self.plotFlatMap.pos = totalPOS
        self.plotFlatMap.color = totalCLR
        self.plotFlatMap.update()

    def colorize(self):
        # choose color mask, charge for now
        if self.colorMask == 'charge':
            variable = self.CHARGE
        else:
            variable = self.TIME
        #variable = self.TIME
        true_min = 0.0
        min_var = max(true_min, min(variable))
        max_var = max(variable)
        var_range = max_var - min_var
        colorList = []
        cmap = cm.jet
        for val in variable:
            if val < true_min:
                colorList.append(cm.Greys(100))
            else:
                try:
                #colorList.append(cm.jet(int((val-min_var)*(256/var_range))))
                    colorList.append(cmap(int((val-min_var)*(256/var_range))))
                except ValueError:
                    print('color problem')
        self.colorArray = np.array(colorList)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('ratfile', type=str, help=('rat root file'))
    parser.add_argument('--debug', action='store_true')
    return parser.parse_args()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, lambda *args: QtGui.QApplication.quit())
    args = get_args()
    def dprint(*argmnt):
        if args.debug:
            print(*argmnt)
    app = QtGui.QApplication([])
    timer = QtCore.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)
    guit = MainWindow(args.ratfile)

    sys.exit(app.exec_())
