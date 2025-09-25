"""
data_analysis.py: Data analysis tools and utilities for the experimental GUI such as retrieving physical parameters from images.
"""

import numpy as np
from typing import Tuple, Optional, List
import matplotlib.pyplot as plt
from scipy import ndimage, optimize
from scipy.stats import norm

from src.device import filtering


class ImageAnalysis:
    """Class for analyzing experimental images and extracting physical parameters."""
    
    def __init__(self, device):
        self.device = device
        self.background_bank = []

    def save_background(self, new_background: np.ndarray):
        # Saves Bacground image to bank if unique
        # Uses circular buffer to keep the 100 most recent backgrounds.
        # Check if this background already exists
        for background in self.background_bank:
            if np.allclose(background, new_background, atol=0):
                return False

        # Add new background at current BGindex position
        self.background_bank.append(new_background)

        # Limit the bank size to 100
        if len(self.background_bank) > 100:
            self.background_bank.pop(0)

        # Background was added
        return True

    def filter_images(self, images: np.ndarray) -> tuple[float, float, np.ndarray]:
        n_atoms = float('nan')
        max_od = float('nan')

        if images.shape[0] == 3:
            # process images
            foreground = np.maximum(images[0,:,:] - images[2,:,:], 1)
            background = np.maximum(images[1,:,:] - images[2,:,:], 1)
            self.save_background(background)
            od_image = -np.log(foreground / background)

            # calculate physical parameters
            n_atoms = self.get_atom_number(od_image)
            max_od = self.get_max_od(od_image)

            # apply filtering based on device settings
            if self.device.device_settings.fringe_removal  and self.device.number_of_backgrounds > 5:
                od_image, opref = filtering.fringe_removal(foreground, self.background_bank)

            if self.device.device_settings.pca and self.number_of_backgrounds > 5:
                od_image, opref = filtering.pca(foreground, self.background_bank)

            if self.device.device_settings.low_pass:
                od_image = filtering.low_pass(images)

            if self.device.device_settings.fft_filter:
                od_image = filtering.fft_filter(od_image)

            # ensure od_image maintains proper 3D shape (add dimension if needed)
            if od_image.ndim == 2:
                od_image = od_image[np.newaxis, :, :]

            # append the processed image to the original images
            images = np.append(images, od_image, axis=0)

        return (n_atoms, max_od, images)

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
        # integrate optical density over the image and convert to atom number
        area_px = (2/3) * pixel_size**2  # Area of one pixel in m^2
        atom_number = float(round((area_px) * np.sum(od_image) / crosssection, 2))
        return atom_number
