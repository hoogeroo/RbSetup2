import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure

from PyQt6.QtCore import QTimer

FLUORESCENCE_SAMPLES = 100

class PlotsGui:
    def __init__(self, window):
        self.window = window
        self.fluorescence_data = np.zeros(FLUORESCENCE_SAMPLES)

        # camera plot
        self.camera_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.camera_ax = self.camera_canvas.figure.subplots()
        self.window.camera_grid.addWidget(self.camera_canvas, 1, 4, 1, 1)

        # fluorescence plot
        self.fluorescence_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.fluorescence_ax = self.fluorescence_canvas.figure.subplots()
        self.fluorescence_ax.set_xlabel('Time (s)')
        self.fluorescence_ax.set_ylabel('Fluorescence (a.u.)')
        self.fluorescence_points, = self.fluorescence_ax.plot(self.fluorescence_data)
        self.window.fluorescence_grid.addWidget(self.fluorescence_canvas, 1, 4, 1, 1)

        # fluorescence timer
        self.fluorescence_timer = QTimer()
        self.fluorescence_timer.timeout.connect(self.update_fluorescence_plot)
        self.fluorescence_timer.start(100)

    def update_fluorescence_plot(self):
        # poll the pipe with no timeout (only read already queued values)
        if self.window.gui_pipe.poll():
            # get the fluorescence value
            fluorescence = self.window.gui_pipe.recv()

            # put the new value at the end of the buffer
            self.fluorescence_data = np.roll(self.fluorescence_data, -1)
            self.fluorescence_data[-1] = fluorescence

            # refresh the plot
            self.fluorescence_points.set_ydata(self.fluorescence_data)
            self.fluorescence_ax.relim()
            self.fluorescence_ax.autoscale_view()
            self.fluorescence_canvas.draw()
