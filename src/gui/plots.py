'''
plots.py: handles the plotting part of the gui and related events
'''

import numpy as np

from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure

from PyQt6.QtWidgets import QTabWidget

from src.gui.filtering import low_pass

FLUORESCENCE_SAMPLES = 100

class CameraImages:
    def __init__(self, images: np.ndarray):
        self.images = images

class FluorescenceSample:
    def __init__(self, sample: float):
        self.sample = sample

class PlotsGui:
    def __init__(self, window):
        self.window = window
        self.fluorescence_data = np.zeros(FLUORESCENCE_SAMPLES)
        self.images = None

        # camera plots
        self.camera_tabs = QTabWidget()
        self.window.camera_grid.addWidget(self.camera_tabs)

        # fluorescence plot
        self.fluorescence_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.fluorescence_ax = self.fluorescence_canvas.figure.subplots()
        self.fluorescence_ax.set_xlabel('Time (s)')
        self.fluorescence_ax.set_ylabel('Fluorescence (a.u.)')
        self.fluorescence_points, = self.fluorescence_ax.plot(self.fluorescence_data)
        self.window.fluorescence_grid.addWidget(self.fluorescence_canvas)

    # update the fluorescence plot with a new sample
    def update_fluorescence(self, sample: float):
        # put the fluorescence value in the readout
        self.window.fluorescence.display(sample)

        # put the new value at the end of the buffer
        self.fluorescence_data = np.roll(self.fluorescence_data, -1)
        self.fluorescence_data[-1] = sample

        # refresh the plot
        self.fluorescence_points.set_ydata(self.fluorescence_data)
        self.fluorescence_ax.relim()
        self.fluorescence_ax.autoscale_view()
        self.fluorescence_canvas.draw()

    # update the camera images
    def update_images(self, images: np.ndarray):
        # store unfiltered images for saving later
        self.images = images

        # apply filtering
        if self.window.action_fringe_removal.isChecked():
            pass # todo
        if self.window.action_pca.isChecked():
            pass # todo
        if self.window.action_low_pass.isChecked():
            images = low_pass(images)
        if self.window.action_fft_filter.isChecked():
            pass # todo

        # load
        self.camera_tabs.clear()
        for i in range(images.shape[0]):
            canvas = FigureCanvas(Figure(figsize=(5, 3)))
            fig = canvas.figure

            # plot the new image
            ax = fig.subplots()
            ax.imshow(images[i, :, :], aspect='equal')
            fig.colorbar(ax.images[0], ax=ax)

            # add a tab
            self.camera_tabs.addTab(canvas, f"Picture {i}")
