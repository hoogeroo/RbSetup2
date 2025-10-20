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
        od_max = round(np.max(od_image), 2)
        
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
        
        area_px = ((2/3) * pixel_size ) **2  # Area of one pixel in m^2

        ### Gaussian Fitting Guesses ###
        amp = np.max(od_image)  # Amplitude guess
        x0, y0 = np.unravel_index(np.argmax(od_image), od_image.shape)  # Center guess
        sigma_x, sigma_y = self.guess_widths(od_image)
        offset = np.mean(od_image[0:10, 0:10])  # Offset guess from corner
        initial_guess = (sigma_x, sigma_y, amp, x0, y0, offset)

        x, y = np.indices(od_image.shape)

        Gaussian_2D = curve_fit(self.fit_2D_Gaussian, (x, y), od_image.ravel(), p0 = initial_guess)
        try:
            sigma_x, sigma_y, amp, x0, y0, offset = Gaussian_2D[0]
            atom_number = 2 * area_px * np.pi * sigma_x * sigma_y * amp / crosssection # Gaussian integral result
        except RuntimeError:
            # Fallback to simple sum if fitting fails
            atom_number = float(round((area_px) * np.sum(od_image) / crosssection, 2))
            
        return atom_number
       

    def guess_widths(self, data: np.ndarray):
        total_x = data.sum(axis=0)
        total_y = data.sum(axis=1)
        x_coords = np.arange(data.shape[1])
        y_coords = np.arange(data.shape[0])

        sx = np.sqrt(np.sum(total_x * (x_coords - (total_x * x_coords).sum() / total_x.sum())**2) / total_x.sum())
        sy = np.sqrt(np.sum(total_y * (y_coords - (total_y * y_coords).sum() / total_y.sum())**2) / total_y.sum())
        return sx, sy