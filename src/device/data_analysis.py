"""
data_analysis.py: Data analysis tools and utilities for the experimental GUI such as retrieving physical parameters from images.
"""

import numpy as np
from typing import Tuple, Optional, List
import matplotlib.pyplot as plt
from scipy import ndimage, optimize
from scipy.stats import norm
from scipy.optimize import curve_fit

from src.device import filtering
from src.gui.plots import CameraImages


class ImageAnalysis:
    """Class for analyzing experimental images and extracting physical parameters."""
    
    def __init__(self, device):
        self.device = device
        self.background_bank = []
        self.number_of_backgrounds = 0

    def fit_2D_Gaussian(self, coords, sigma_x, sigma_y, A, x0, y0, offset):
        """2D Gaussian function for fitting."""
        x, y = coords
        gaussian = offset + A * np.exp(-(((x - x0) ** 2) / (2 * sigma_x ** 2) + ((y - y0) ** 2) / (2 * sigma_y ** 2)))
        return gaussian.ravel()


    def save_background(self, new_background: np.ndarray):
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

        # Background was added
        return True

    def filter_images(self, images: CameraImages) -> CameraImages:
        # process images
        foreground = np.maximum(images.foreground - images.empty, 1)
        background = np.maximum(images.background - images.empty, 1)
        self.save_background(background)
        od_image = -np.log(foreground / background)

        # calculate physical parameters
        images.n_atoms = self.get_atom_number(od_image)
        images.max_od = self.get_max_od(od_image)

        # apply filtering based on device settings
        if self.device.device_settings.fringe_removal  and self.device.number_of_backgrounds > 5:
            od_image, opref = filtering.fringe_removal(foreground, self.background_bank)

        if self.device.device_settings.pca and self.number_of_backgrounds > 5:
            od_image, opref = filtering.pca(foreground, self.background_bank)

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
        #od_max = round(np.max(od_image), 2)
        
        #return od_max
        # handle non-finite values safely
        if not np.any(np.isfinite(od_image)):
            return 0.0
        od_max = round(float(np.nanmax(np.nan_to_num(od_image, nan=0.0, posinf=0.0, neginf=0.0))), 2)
        return od_max

    
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
        area_px = ((2/3) * pixel_size ) **2  # Area of one pixel in m^2
        try:
            ### Gaussian Fitting Guesses ###
            amp = np.max(od_image)  # Amplitude guess
            x0, y0 = np.unravel_index(np.argmax(od_image), od_image.shape)  # Center guess
            sigma_x, sigma_y = self.guess_widths(od_image)
            offset = np.mean(od_image[0:10, 0:10])  # Offset guess from corner
            initial_guess = (sigma_x, sigma_y, amp, x0, y0, offset)

            x, y = np.indices(od_image.shape)
        
            Gaussian_2D = curve_fit(self.fit_2D_Gaussian, (x, y), od_image.ravel(), p0 = initial_guess)
            sigma_x, sigma_y, amp, x0, y0, offset = Gaussian_2D[0]
            atom_number = 2 * area_px * np.pi * abs(sigma_x) * abs(sigma_y) * amp / crosssection # Gaussian integral result
        except RuntimeError:
            # Fallback to simple sum if fitting fails
            atom_number = float(round((area_px) * np.sum(od_image) / crosssection, 2))
            
        return atom_number
        """
        # area per pixel (m^2)
        area_px = (pixel_size) ** 2

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
            popt, _ = curve_fit(self.fit_2D_Gaussian, (x, y), od_image.ravel(), p0=initial_guess, maxfev=5000)
            sigma_x, sigma_y, amp, x0, y0, offset = popt
            atom_number = 2 * area_px * np.pi * abs(sigma_x) * abs(sigma_y) * amp / crosssection
        except Exception:
            # Fallback to simple sum if fitting fails
            atom_number = float(round(area_px * np.sum(np.nan_to_num(od_image)) / crosssection, 2))

        return atom_number


    def guess_widths(self, data: np.ndarray):
        x, y = np.indices(data.shape)
        total = np.sum(data)

        X0 = np.sum(x * data) / total if total != 0 else 0
        Y0 = np.sum(y * data) / total if total != 0 else 0

        sx = np.sqrt(np.sum(data * (x - X0) ** 2) / total)
        sy = np.sqrt(np.sum(data * (y - Y0) ** 2) / total)

        return sx, sy