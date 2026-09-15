"""
data_analysis.py: Data analysis tools and utilities for the experimental GUI such as retrieving physical parameters from images.
"""

import os
import numpy as np
from typing import Tuple, Optional, List
import matplotlib.pyplot as plt
from scipy import ndimage, optimize
from scipy.stats import norm
from scipy.optimize import curve_fit

from src.device import filtering
from src.gui.plots import CameraImages

background_save_path = 'runs/background_bank.npz'
empty_save_path = 'runs/empty_bank.npz'


class ImageAnalysis:
    """Class for analyzing experimental images and extracting physical parameters."""
    
    def __init__(self, device):
        self.device = device
        self.background_bank = []
        self.empty_bank = []
        self.number_of_backgrounds = 0
        self.number_of_empties = 0
        self.load_backgrounds()
        self.load_empties()

    def fit_2D_Gaussian(self, coords, sigma_x, sigma_y, A, x0, y0, offset):
        """2D Gaussian function for fitting."""
        x, y = coords
        gaussian = offset + A * np.exp(-(((x - x0) ** 2) / (2 * sigma_x ** 2) + ((y - y0) ** 2) / (2 * sigma_y ** 2)))
        return gaussian.ravel()


    def save_background(self, new_background: np.ndarray) -> bool:
        # Saves Bacground image to bank if unique
        # Uses circular buffer to keep the 100 most recent backgrounds.
        # Check if this background already exists
        for background in self.background_bank:
            if np.allclose(background, new_background, atol=0):
                return False

        # Add new background at current BGindex position
        self.background_bank.append(new_background)
        self.number_of_backgrounds += 1

        # Limit the bank size to 100
        if len(self.background_bank) > 100:
            self.background_bank.pop(0)
            self.number_of_backgrounds = 100

        # Save current background bank to npz file
        np.savez(background_save_path, backgrounds=np.array(self.background_bank))

        # Background was added
        return True
    
    def save_empty(self, new_empty: np.ndarray) -> bool:

        for empty in self.empty_bank:
            if np.allclose(empty, new_empty, atol=0):
                return False
            
        self.empty_bank.append(new_empty)
        self.number_of_empties += 1

        if len(self.empty_bank) > 100:
            self.empty_bank.pop(0)
            self.number_of_empties = 100

        np.savez(empty_save_path, empties=np.array(self.empty_bank))

        # Empty was added
        return True
    
    def load_backgrounds(self):
        if os.path.exists(background_save_path):
            data = np.load(background_save_path)
            self.background_bank = list(data['backgrounds'])
            self.number_of_backgrounds = len(self.background_bank)

    def load_empties(self):
        if os.path.exists(empty_save_path):
            data = np.load(empty_save_path)
            self.empty_bank = list(data['empties'])
            self.number_of_empties = len(self.empty_bank)

    def process_OD_image(self, fg: np.ndarray, bg: np.ndarray, empty: np.ndarray, save: bool=False) -> np.ndarray:
        fg = fg - empty
        bg = bg - empty
        od_image = -np.log(fg / bg)

        if save:
            self.save_background(bg)

        return od_image

    def get_n_atoms_from_bf(self, bf_od_image: np.ndarray, pixel_size=5.86e-6, crosssection=1.3e-13) -> float:
        area_px = (pixel_size) ** 2  # Area of one pixel in m^2 assuming 1:1 imaging
        n_atoms_bf_sum = float(round(area_px * np.sum(bf_od_image) / crosssection, 2))

        # Use Gaussian fitting to estimate the atom number
        try:
            amp = float(np.max(bf_od_image))  # Amplitude guess
            y0, x0 = np.unravel_index(np.argmax(bf_od_image), bf_od_image.shape)  # Center guess (rows, cols)
            sigma_x, sigma_y = self.guess_widths(bf_od_image)
            if not np.isfinite(sigma_x) or sigma_x <= 0:
                sigma_x = 1.0
            if not np.isfinite(sigma_y) or sigma_y <= 0:
                sigma_y = 1.0
            offset = float(np.mean(bf_od_image[0:10, 0:10]))
            initial_guess = (sigma_x, sigma_y, amp, x0, y0, offset)

            x, y = np.indices(bf_od_image.shape)
            popt, _ = curve_fit(self.fit_2D_Gaussian, (x, y), bf_od_image.ravel(), p0=initial_guess)
            sigma_x, sigma_y, amp, x0, y0, offset = popt
            n_atoms_bf = 2 * area_px * np.pi * abs(sigma_x) * abs(sigma_y) * amp / crosssection
        except Exception:
            n_atoms_bf = 0.0

        return n_atoms_bf, n_atoms_bf_sum

    def filter_images(self, images: CameraImages) -> CameraImages:
        # process images
        self.save_empty(images.empty)
        master_empty = np.median(self.empty_bank, axis=0)
        Current_offset = np.median(images.empty - master_empty)
        total_empty = master_empty + Current_offset # Accounts for any constant shifts of the empty image photon counts
        images.master_empty = total_empty

        od_image = self.process_OD_image(images.foreground, images.background, total_empty, save=True)
        if images.bf_foreground is not None:
            images.bf_image = self.process_OD_image(images.bf_foreground, images.bf_background, images.bf_empty)
            images.n_atoms_bf, images.n_atoms_bf_sum = self.get_n_atoms_from_bf(images.bf_image)

        # calculate physical parameters
        images.n_atoms_int, images.n_atoms_sum = self.get_atom_number(od_image)
        images.max_od = self.get_max_od(od_image)
        images.n_atoms_roi = self.get_atom_number_in_ROI(od_image, Rx=40, Ry=25)

        # apply filtering based on device settings
        if self.device.device_settings.fringe_removal  and self.number_of_backgrounds > 5:
            od_image, opref = filtering.fringe_removal(images.foreground - total_empty, self.background_bank)

        if self.device.device_settings.pca and self.number_of_backgrounds > 5:
            od_image, opref = filtering.pca(images.foreground - total_empty, self.background_bank)

        if self.device.device_settings.low_pass:
            od_image = filtering.low_pass(od_image)

        if self.device.device_settings.fft_filter:
            od_image = filtering.fft_filter(od_image)

        images.od = od_image
    
        return images

    def get_max_od(self, od_image: np.ndarray) -> float:
        """
        Calculate maximum optical density OD.
        
        Args:
            od_image: Optical density image
            
        Returns:
            Float
        """
        # handle non-finite values safely
        if not np.any(np.isfinite(od_image)):
            return 0.0
        od_max = round(float(np.nanmax(np.nan_to_num(od_image, nan=0.0, posinf=0.0, neginf=0.0))), 2)
        return od_max
    
    def get_atom_number_in_ROI(self, od_image: np.ndarray, Rx, Ry, pixel_size = 5.86e-6, crosssection = 1.3e-13) -> float:
        try:
            ### Gaussian Fitting Guesses ###
            amp = float(max(od_image))  # Amplitude guess
            y0, x0 = np.unravel_index(np.argmax(od_image), od_image.shape)  # Center guess (rows, cols)
            sigma_x, sigma_y = self.guess_widths(od_image)
            # guard against zero/NaN widths
            if not np.isfinite(sigma_x) or sigma_x <= 0:
                sigma_x = 1.0
            if not np.isfinite(sigma_y) or sigma_y <= 0:
                sigma_y = 1.0
            offset = float(np.mean(od_image[0:10, 0:10]))
            initial_guess = (sigma_x, sigma_y, amp, x0, y0, offset)

            x, y = np.indices(od_image.shape)
            popt, _ = curve_fit(self.fit_2D_Gaussian, (x, y), od_image.ravel(), p0=initial_guess)
            sigma_x, sigma_y, amp, x0, y0, offset = popt
        except:
            from scipy.ndimage import gaussian_filter
            od_smoothed = gaussian_filter(od_image, sigma=1.0)
            y0, x0 = np.unravel_index(np.argmax(od_smoothed), od_smoothed.shape)

        # Define the region of interest (ROI)
        x_min = max(int(x0 - Rx), 0)
        x_max = min(int(x0 + Rx), od_image.shape[1])
        y_min = max(int(y0 - Ry), 0)
        y_max = min(int(y0 + Ry), od_image.shape[0])

        # Create mask for the ROI
        mask = np.zeros_like(od_image, dtype=bool)
        mask[y_min:y_max, x_min:x_max] = True

        # Calculate atom number within the ROI
        masked_image = np.where(mask, od_image, 0)
        area_px = ((1 / 2.6) * pixel_size) ** 2  # Area of one pixel in m^2
        atom_number_roi = float(round(area_px * np.sum(masked_image) / crosssection, 2))

        return atom_number_roi

    def get_atom_number(self, od_image: np.ndarray, pixel_size = 16e-6, crosssection = 1.3e-13) -> float:
        """
        Calculate total atom number from an optical density image.
        
        Args:
            od_image: Optical density image
            pixel_size: Size of one pixel in meters
            cross_section: Absorption cross-section in square meters
            
        Returns:
            Total atom number
        """
        """
        area_px = ((1/2.6) * pixel_size ) **2  # Area of one pixel in m^2
        try:
            ### Gaussian Fitting Guesses ###
            amp = np.max(od_image)  # Amplitude guess
            x0, y0 = np.unravel_index(np.argmax(od_image), od_image.shape)  # Center guess
            sigma_x, sigma_y = self.guess_widths(od_image)
            offset = np.mean(od_image[0:10, 0:10])  # Offset guess from corner
            initial_guess = (sigma_x, sigma_y, amp, x0, y0, offset)

            x, y = np.indices(od_image.shape)
        
            Gaussian_2D = curve_fit(self.fit_2D_Gaussian, (x, y), od_image.ravel(), p0 = initial_guess)
            x, y = np.indices(od_image.shape)
        
            Gaussian_2D = curve_fit(self.fit_2D_Gaussian, (x, y), od_image.ravel(), p0 = initial_guess)
            sigma_x, sigma_y, amp, x0, y0, offset = Gaussian_2D[0]
            atom_number = 2 * area_px * np.pi * abs(sigma_x) * abs(sigma_y) * amp / crosssection # Gaussian integral result
            atom_number = 2 * area_px * np.pi * abs(sigma_x) * abs(sigma_y) * amp / crosssection # Gaussian integral result
        except RuntimeError:
            # Fallback to simple sum if fitting fails
            atom_number = float(round((area_px) * np.sum(od_image) / crosssection, 2))
            
        return atom_number
        """
        # area per pixel (m^2)
        area_px = ((1 / 2.6) * pixel_size) ** 2

        # sanitize image and short-circuit empty frames
        od_image = np.nan_to_num(od_image, nan=0.0, posinf=0.0, neginf=0.0)
        od_max = np.max(od_image)
        if not np.isfinite(od_max) or od_max <= 0:
            return 0.0

        try:
            ### Gaussian Fitting Guesses ###
            amp = float(od_max)  # Amplitude guess
            y0, x0 = np.unravel_index(np.argmax(od_image), od_image.shape)  # Center guess (rows, cols)
            sigma_x, sigma_y = self.guess_widths(od_image)
            # guard against zero/NaN widths
            if not np.isfinite(sigma_x) or sigma_x <= 0:
                sigma_x = 1.0
            if not np.isfinite(sigma_y) or sigma_y <= 0:
                sigma_y = 1.0
            offset = float(np.mean(od_image[0:10, 0:10]))
            initial_guess = (sigma_x, sigma_y, amp, x0, y0, offset)

            x, y = np.indices(od_image.shape)
            popt, _ = curve_fit(self.fit_2D_Gaussian, (x, y), od_image.ravel(), p0=initial_guess)
            sigma_x, sigma_y, amp, x0, y0, offset = popt
            atom_number = 2 * area_px * np.pi * abs(sigma_x) * abs(sigma_y) * amp / crosssection
            atom_number_sum = float(round(area_px * np.sum(od_image) / crosssection, 2))
        except Exception:
            # Fallback to simple sum if fitting fails
            atom_number = float('nan')
            atom_number_sum = float(round(area_px * np.sum(od_image) / crosssection, 2))

        return atom_number, atom_number_sum


    def guess_widths(self, data: np.ndarray):
        x, y = np.indices(data.shape)
        total = np.sum(data)

        X0 = np.sum(x * data) / total if total != 0 else 0
        Y0 = np.sum(y * data) / total if total != 0 else 0

        sx = np.sqrt(np.sum(data * (x - X0) ** 2) / total)
        sy = np.sqrt(np.sum(data * (y - Y0) ** 2) / total)

        return sx, sy
    
class FluorescenceAnalysis:
    @staticmethod
    def exponential_decay(x, A, x0, c):
        return c + A * np.exp(-x/x0)

    @staticmethod
    def extract_mot_lifetime(times: np.ndarray, fluorescence_data: np.ndarray):
        A_guess = max(fluorescence_data)
        offset_guess = 200
        x0_guess = 10
        k0_guess = 0
        B_guess = 0

        p0 = [A_guess, x0_guess, offset_guess]
        bounds = ([0, 1e-3, 0], [10000, 120, 500])

        popt, pcov = curve_fit(FluorescenceAnalysis.exponential_decay, times, fluorescence_data, p0=p0, bounds=bounds)
        A, tau, offset = popt
        tau_error = np.sqrt(pcov[1, 1])
        fitted_fluorescence = FluorescenceAnalysis.exponential_decay(times, *popt)

        return (A, tau, offset, tau_error, fitted_fluorescence)
