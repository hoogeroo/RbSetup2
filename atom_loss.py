from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import os
import math
import re

# -------- Control Parameters --------
magnification = 2.6
px_size = 16e-6  # Pixel size in meters
Rb_cross_section = 1.3e-13  # Cross-section of Rb in m^2
area_px = (px_size / magnification)**2  # Area per pixel in m^2

t_array = np.linspace(1, 10, 10)  # time held in s

fits_folder = "runs/multigo_2026-04-15_15-18-43"

# -------- Main calculations --------

def fit_2D_Gaussian(xy, sigma_x, sigma_y, amp, x0, y0, offset):
    x, y = xy
    return (offset + amp * np.exp(-((x - x0) ** 2 / (2 * sigma_x**2) + (y - y0) ** 2 / (2 * sigma_y**2)))).ravel()


def calculate_atom_number(image, sigma_x, sigma_y, amp):
    atom_number_2D = 2 * area_px * np.pi * abs(sigma_x) * abs(sigma_y) * amp / Rb_cross_section
    return atom_number_2D

# -------- Functions for fit guesses --------

def guess_widths(od_image):
    x_profile = np.sum(od_image, axis=0)
    y_profile = np.sum(od_image, axis=1)

    def estimate_width_from_profile(profile):
        max_val = np.max(profile)
        half_max = max_val / 2
        indices = np.where(profile >= half_max)[0]
        if len(indices) > 0:
            return (indices[-1] - indices[0]) / 2.355
        return 20.0

    sigma_x = estimate_width_from_profile(x_profile)
    sigma_y = estimate_width_from_profile(y_profile)
    return sigma_x, sigma_y


def guess_amplitude(od_image):
    return float(np.max(od_image))


def guess_center(od_image):
    x_profile = np.sum(od_image, axis=0)
    y_profile = np.sum(od_image, axis=1)
    x0 = int(np.argmax(x_profile))
    y0 = int(np.argmax(y_profile))
    return x0, y0


def guess_offset(od_image):
    return float(np.mean(od_image[0:10, 0:10]))

def linear(x, m, c):
    return m * x + c


# Load the image

def load_image(filepath):
    with fits.open(filepath) as hdul:
        image_data = hdul[1].data
    od_image = image_data[3, :, :]  # Extract the 2D image from the data cube
    return od_image

# ------- Main execution --------
numbers = re.compile(r'(\d+)')


def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts


def main():
    cwd = os.path.dirname(os.path.abspath(__file__))
    cwd = os.path.join(cwd, fits_folder)

    fits_files = [file for file in os.listdir(cwd) if file.endswith('.fits')]
    fits_files = sorted(fits_files, key=numericalSort)

    image_list = np.empty((len(fits_files), 512, 512))  # Assuming images are 512x512 pixels
    atom_numbers = np.empty(len(fits_files))

    for idx, file in enumerate(fits_files):
        print(f"Processing file: {file}")
        filepath = os.path.join(cwd, file)
        od_image = load_image(filepath)
        image_list[idx, :, :] = od_image

    for idx in range(len(fits_files)):
        od_image = image_list[idx, :, :]

        sigma_x_guess, sigma_y_guess = guess_widths(od_image)
        amp_guess = guess_amplitude(od_image)
        x0_guess, y0_guess = guess_center(od_image)
        offset_guess = guess_offset(od_image)

        initial_guesses = [sigma_x_guess, sigma_y_guess, amp_guess, x0_guess, y0_guess, offset_guess]

        y_idx, x_idx = np.indices(od_image.shape)
        popt, pcov = curve_fit(
            fit_2D_Gaussian,
            (x_idx, y_idx),
            od_image.ravel(),
            p0=initial_guesses,
            maxfev=20000,
        )

        sigma_x_fit, sigma_y_fit, amp_fit, x0_fit, y0_fit, offset_fit = popt

        atom_numbers[idx] = calculate_atom_number(od_image, sigma_x_fit, sigma_y_fit, amp_fit)
    
    popt, pcov = curve_fit(linear, t_array, atom_numbers)
    m_fit, c_fit = popt
    print(f"Fitted linear parameters: m = {m_fit:.2e}, c = {c_fit:.2e}")

    plt.plot(t_array, atom_numbers, 'o')
    plt.plot(t_array, linear(t_array, *popt), 'r-', label=f'Fit: N = {m_fit:.2e} * t + {c_fit:.2e}')
    plt.xlabel('Time held (s)')
    plt.ylabel('Atom Number')
    plt.title('Atom Number vs Time held')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()