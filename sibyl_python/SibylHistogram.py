from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as Navbar
from matplotlib.figure import Figure
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np

class SibylHistogram(FigureCanvas):
    '''
    Generic histogram object (widget). Designed primarily
    to draw charge/time histograms for an event with a colored
    axis.
    '''

    press = False
    bins  = 20

    def __init__(self, parent=None):
        self._parent = parent
        self._setup_painter()
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_move)

    def _setup_painter(self):
        self.fig = Figure()
        self.fig.patch.set_facecolor('black')
        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor('black')
        axcolor = 'red'
        self.axes.set_xlim(left=0)
        self.axes.set_ylim(bottom=0)
        self.axes.spines['bottom'].set_color(axcolor)
        self.axes.spines['left'].set_color(axcolor)
        self.axes.tick_params(axis='x', color=axcolor, which='both')
        self.axes.tick_params(axis='y', color=axcolor, which='both')
        self.axes.xaxis.label.set_color(axcolor)
        #self.cbar = self.fig.add_axes([0.85, 0.1, 0.05, 0.8])
        FigureCanvas.__init__(self, self.fig)

    def on_press(self, event):
        #print('you pressed', event.button, event.xdata, event.ydata)
        if event.dblclick:
            y, x = np.histogram(self.data, self.bins)
            self.axes.set_ylim(top=1.1*y.max())
            self.axes.set_xlim(right=x.max())
            self.redraw()
            return
        if event.button == 3: #right click
            if self.axes.get_yscale() == 'linear': 
                self.axes.set_ylim(bottom=1e-1)
                self.axes.set_yscale('log')
                self.draw()
            else:
                self.axes.set_yscale('linear')
                self.axes.set_ylim(bottom=0)
                self.draw()
        if event.button == 1:
            self._prev_pos = event.xdata, event.ydata
            self._prev_xmax = self.axes.get_xlim()[1]
            self._prev_ymax = self.axes.get_ylim()[1]
            self.press=False

    def on_release(self, event):
        #print('you pressed', event.button, event.xdata, event.ydata)
        if event.button == 1:
            self.press=False
            dx = self._prev_pos[0] - event.xdata
            dy = self._prev_pos[1] - event.ydata
            #print(dx, dy)


    def on_move(self, event):
        if event.button == 1:
            dx = event.xdata - self._prev_pos[0]
            dy = event.ydata - self._prev_pos[1]
            self.axes.set_xlim(right=self._prev_xmax-dx)
            self.axes.set_ylim(top=self._prev_ymax-dy)
            self.redraw()
        #print('you pressed', event.button, event.xdata, event.ydata)

    def setData(self, dataset):
        self.data = dataset[dataset>0]
        self.redraw()

    def redraw(self):
        if hasattr(self, 'patches'):
            t = [b.remove() for b in self.patches]
        newxlim = self.axes.get_xlim()[1]
        self._parent.parameters['histXMax'] = newxlim
        bins = np.linspace(0, newxlim, self.bins)
        y, x, self.patches = self.axes.hist(
                np.clip(self.data, bins[0], bins[-1]), 
                bins=bins)
        colors = cm.jet(np.linspace(0,1, self.bins))
        for ptc, clr in zip(self.patches, colors):
            ptc.set_facecolor(clr)
        self.draw()
        if self._parent is not None:
            self._parent.drawColors()

    def colorline(self, x, y, z=None, cmap=cm.jet,
            norm=plt.Normalize(0, 1), linewidth=3, alpha=1.0):
        if z is None:
            z = np.linspace(0, 1.0, (len(x)-1)*4)
        if not hasattr(z, "__iter__"):
            z = np.array([z])
        z = np.asarray(z)
        segments = self.make_segments(x, y)
        lc = mcoll.LineCollection(segments, array=z, cmap=cmap,
                norm=norm, linewidth=linewidth, alpha=alpha)
        return lc

    def make_segments(self,x, y):
        rx = np.repeat(x, 4)[2:-2]
        ry = np.roll(np.vstack((np.zeros(y.shape),y)).ravel('F').repeat(2), -1)[4:]
        points = np.array([rx, ry]).T.reshape(-1, 1, 2)
        return np.concatenate([points[:-1], points[1:]], axis=1)

def histogram(events, **kwargs):
    y, x = np.histogram(events, **kwargs)
    kx = ((x+np.roll(x, -1))/2.)[:-1]
    return kx, y
