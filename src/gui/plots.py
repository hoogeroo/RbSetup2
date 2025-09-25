'''
plots.py: handles the plotting part of the gui and related events
'''

import numpy as np

from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure

from PyQt6.QtWidgets import QTabWidget

FLUORESCENCE_SAMPLES = 100

class CameraImages:
    def __init__(self, images: np.ndarray = None, n_atoms: float = float('nan'), max_od: float = float('nan')):
        self.images = images
        self.n_atoms = n_atoms
        self.max_od = max_od

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
    def update_fluorescence(self, sample: FluorescenceSample):
        sample = sample.sample

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
    def update_images(self, camera_images: CameraImages):
        # store unfiltered images for saving later
        self.images = camera_images.images

        # clear existing tabs
        self.camera_tabs.clear()

        # plot the images
        image_names = ["Foreground", "Background", "Empty Image", "OD Image"]
        for i in range(camera_images.images.shape[0]):
            canvas = FigureCanvas(Figure(figsize=(5, 3)))
            fig = canvas.figure

            # plot the new image
            ax = fig.subplots()
            ax.imshow(camera_images.images[i, :, :], aspect='equal', cmap='inferno')
            fig.colorbar(ax.images[0], ax=ax)

            # add a tab for the images
            self.camera_tabs.addTab(canvas, f"{image_names[i]}")

        # format the atom number nicely
        atom_number = camera_images.n_atoms
        keys = ['K', 'M', 'B', 'T']
        count = 0
        for div in range(0, len(keys)):
          atom_number = atom_number/1000
          count += 1
          if atom_number < 1000:
            break
        atom_number_rounded = str(round(atom_number, 2)) + keys[count - 1]

        # print to the log
        text = self.window.log.document().toPlainText()
        text += f"Num Atoms: {atom_number_rounded}\nMax OD: {camera_images.max_od:.2f}\n\n"
        self.window.log.setPlainText(text)
        self.window.log.verticalScrollBar().setValue(self.window.log.verticalScrollBar().maximum())
