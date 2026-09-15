'''
plots.py: handles the plotting part of the gui and related events
'''

import numpy as np

from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure

from PyQt6.QtWidgets import QTabWidget, QDialog, QVBoxLayout

FLUORESCENCE_SAMPLES = 100

class CameraImages:
    def __init__(self, foreground: np.ndarray, background: np.ndarray, empty: np.ndarray, od: np.ndarray=None, bf_foreground: np.ndarray=None, 
                 bf_background: np.ndarray=None, bf_empty: np.ndarray=None, bf_image: np.ndarray=None, bf_images: np.ndarray=None, master_empty: np.ndarray=None,
                  n_atoms_int: float = float('nan'), n_atoms_sum: float = float('nan'), max_od: float = float('nan'), n_atoms_roi: float = float('nan'), fluoimage: np.ndarray=None, 
                  n_atoms_bf: float = float('nan'), n_atoms_bf_sum: float = float('nan')):
        self.foreground = foreground
        self.background = background
        self.empty = empty
        self.od = od
        self.bf_image = bf_image
        self.bf_images = bf_images
        self.bf_foreground = bf_foreground
        self.bf_background = bf_background
        self.bf_empty = bf_empty
        self.master_empty = master_empty
        self.n_atoms_int = n_atoms_int
        self.n_atoms_sum = n_atoms_sum
        self.n_atoms_bf = n_atoms_bf
        self.n_atoms_bf_sum = n_atoms_bf_sum
        self.max_od = max_od
        self.n_atoms_roi = n_atoms_roi
        self.fluoimage = fluoimage

class FluorescenceSample:
    def __init__(self, sample: float = 0.0, sample_bf: float = 0.0):
        self.sample = sample
        self.sample_bf = sample_bf

class PlotsGui:
    def __init__(self, window):
        self.window = window
        self.fluorescence_data = np.zeros(FLUORESCENCE_SAMPLES)
        self.fluorescence_data_bf = np.zeros(FLUORESCENCE_SAMPLES)
        self.images = None

        # camera plots
        self.camera_tabs = QTabWidget()
        self.window.camera_grid.addWidget(self.camera_tabs)

        # fluorescence plot
        self.fluorescence_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.fluorescence_ax = self.fluorescence_canvas.figure.subplots()
        self.fluorescence_ax_bf = self.fluorescence_ax.twinx()
        self.fluorescence_ax.set_xlabel('Time (s)')
        self.fluorescence_ax.set_ylabel('Fluorescence (a.u.)')
        self.fluorescence_points, = self.fluorescence_ax.plot(self.fluorescence_data, color = 'b', label = 'PD')
        self.fluorescence_points_bf, = self.fluorescence_ax_bf.plot(self.fluorescence_data_bf, color = 'g', label = 'BF')
        lines = [self.fluorescence_points, self.fluorescence_points_bf]
        labels = [line.get_label() for line in lines]
        self.fluorescence_ax.legend(lines, labels)

        self.window.fluorescence_grid.addWidget(self.fluorescence_canvas)
        self.multigo_y=[]
        self.multigo_x=[]

    # update the fluorescence plot with a new sample
    def update_fluorescence(self, sample: FluorescenceSample):
        sample_bf = sample.sample_bf
        sample = sample.sample

        # put the fluorescence value in the readout
        self.window.fluorescence.display(sample_bf)

        # put the new value at the end of the buffer
        self.fluorescence_data = np.roll(self.fluorescence_data, -1)
        self.fluorescence_data[-1] = sample
        self.fluorescence_data_bf = np.roll(self.fluorescence_data_bf, -1)
        self.fluorescence_data_bf[-1] = sample_bf

        # refresh the plot
        self.fluorescence_points.set_ydata(self.fluorescence_data)
        self.fluorescence_points_bf.set_ydata(self.fluorescence_data_bf)
        self.fluorescence_ax.relim()
        self.fluorescence_ax.autoscale_view()
        self.fluorescence_ax_bf.relim()
        self.fluorescence_ax_bf.autoscale_view()
        self.fluorescence_canvas.draw()

    def round_number(self, number):
        keys = ['K', 'M', 'B', 'T']
        count = 0
        for div in range(0, len(keys)):
            number = number / 1000
            count += 1
            if number < 1000:
                break
        rounded_number = str(round(number, 2)) + keys[count - 1]
        return rounded_number

    # update the camera images
    def update_images(self, camera_images: CameraImages):
        # store unfiltered images for saving later
        self.images = camera_images
        
        # format the atom number nicely
        atom_number = self.images.n_atoms_int
        atom_number_sum = self.images.n_atoms_sum
        n_atoms_roi = self.images.n_atoms_roi

        atom_number_bf = self.images.n_atoms_bf
        atom_number_bf_sum = self.images.n_atoms_bf_sum

        atom_number_rounded = self.round_number(atom_number)
        atom_number_sum_rounded = self.round_number(atom_number_sum)
        atom_number_bf_rounded = self.round_number(atom_number_bf)
        atom_number_bf_sum_rounded = self.round_number(atom_number_bf_sum)
        
        n_atoms_roi_rounded = self.round_number(n_atoms_roi)
        # clear existing tabs
        self.camera_tabs.clear()

        # plot the images
        image_names = [("OD Image", "od"), ("Foreground", "foreground"), ("Background", "background"), ("Empty Image", "empty"), ("Fluo Image", "fluoimage"), ("Master Empty", "master_empty"), 
                       ("Multigo", "multigo"), ("BF Image", "bf_image"), ("BF Foreground", "bf_foreground"), ("BF Background", "bf_background"), ("BF Empty", "bf_empty")]
        for (tab_name, image_name) in image_names:
            canvas = FigureCanvas(Figure(figsize=(5, 3)))
            fig = canvas.figure

            # plot the new image
            ax = fig.subplots()
            if image_name != "multigo":
                image = getattr(camera_images, image_name, None)
                if image is not None:
                    ax.imshow(image, aspect='equal', cmap='inferno')
                    ax.set_title(f"{tab_name} - {atom_number_rounded} atoms int, {atom_number_sum_rounded} atoms sum, Max OD: {camera_images.max_od:.2f}, N_atoms ROI: {n_atoms_roi_rounded}")
                    fig.colorbar(ax.images[0], ax=ax)
            else:
                self.multigo_y.append(camera_images.n_atoms_int)
                self.multigo_x.append(len(self.multigo_y))
                ax.plot(self.multigo_x, self.multigo_y, marker='o')
                ax.set_title(f"{tab_name} - {atom_number_rounded} atoms")
                ax.set_xlabel("Multigo Iteration")
                ax.set_ylabel("Number of Atoms")
            # add a tab for the images
            self.camera_tabs.addTab(canvas, tab_name)

        # print to the log
        text = self.window.log.document().toPlainText()
        text += f"Num Atoms Guassian integral: {atom_number_rounded}\nNum Atoms Sum {atom_number_sum_rounded}\nMax OD: {camera_images.max_od:.2f}\nN_atoms ROI: {n_atoms_roi_rounded}\nN_atoms BF: {atom_number_bf_rounded}\nN_atoms BF sum: {atom_number_bf_sum_rounded}\n"
        self.window.log.setPlainText(text)
        self.window.log.verticalScrollBar().setValue(self.window.log.verticalScrollBar().maximum())

    # update the temperature displays
    def update_temperatures(self, temperatures: dict):
        # update upper coil temperature
        if 'upper_coil' in temperatures and temperatures['upper_coil'] is not None:
            self.window.lblcoilup.setText(f"{temperatures['upper_coil']:.1f} °C")
        
        # update lower coil temperature
        if 'lower_coil' in temperatures and temperatures['lower_coil'] is not None:
            self.window.lblcoillow.setText(f"{temperatures['lower_coil']:.1f} °C")
        
        # update ambient temperature
        if 'ambient_temp' in temperatures and temperatures['ambient_temp'] is not None:
            self.window.lblambient.setText(f"{temperatures['ambient_temp']:.1f} °C")

    def update_mot_lifetime(self, result):
        import matplotlib.pyplot as plt
        text = self.window.log.document().toPlainText()
        text += f'Mot Lifetime: {result.tau: .2f} +- {result.tau_error: .2f}\n' f'Baseline: {result.offset: .2f}\n'
        self.window.log.setPlainText(text)
        self.window.log.verticalScrollBar().setValue(self.window.log.verticalScrollBar().maximum())
        
        plt.figure("MOT Lifetime")
        plt.clf()

        plt.plot(result.times, result.fluorescence, "o", label = "Measured Fluorescene")

        plt.plot(result.times, result.fitted_fluorescence, "--", label = "Exponential Fit")
        plt.xlabel("Time (s)")
        plt.ylabel("Fluorescence")
        plt.title(f"MOT Lifetime = {result.tau: .2f} +- {result.tau_error:.2f} s")
        plt.legend(loc = 'best')
        plt.tight_layout()

        plt.show(block=False)