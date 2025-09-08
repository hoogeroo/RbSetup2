"""
data_analysis.py: Data analysis tools and utilities for the experimental GUI such as retrieving physical parameters from images.
"""

import numpy as np
from typing import Tuple, Optional, List
import matplotlib.pyplot as plt
from scipy import ndimage, optimize
from scipy.stats import norm


class ImageAnalysis:
    """Class for analyzing experimental images and extracting physical parameters."""
    
    def __init__(self):
        pass
    
    def get_max_OD(self, ODimage: np.ndarray) -> float:
        """
        Calculate maximum optical density OD.
        
        Args:
            ODimage: Optical density image
            
        Returns:
            Float
        """
        od_max = round(np.max(ODimage), 2)
        
        return od_max
    
    def get_atom_number(self, odimage: np.ndarray, pixel_size = 16e-6, crosssection = 1.3e-13) -> float:
        """
        Calculate total atom number from an optical density image.
        
        Args:
            od_image: Optical density image
            pixel_size: Size of one pixel in meters
            cross_section: Absorption cross-section in square meters
            
        Returns:
            Total atom number
        """
        # Integrate OD over the image and convert to atom number
        atom_number = float(round((pixel_size**2) * np.sum(odimage) / crosssection, 2))
        keys = ['K', 'M', 'B', 'T']
        count = 0
        for div in range(0, len(keys)):
          atom_number = atom_number/1000
          count += 1
          if atom_number < 1000:
            break
        atom_number_rounded = str(round(atom_number, 2)) + keys[count - 1]
        
        return atom_number_rounded, atom_number
