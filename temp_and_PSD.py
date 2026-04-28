from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import os
import math
import re

# -------- Control Parameters --------
skip_points = 5
magnification = 2.6
px_size = 16e-6  # Pixel size in meters
Rb_cross_section = 1.3e-13  # Cross-section of Rb in m^2
area_px = (px_size / magnification)**2  # Area per pixel in m^2

mass_rubid = 86.909184 * 1.66E-27
boltzmann = 1.380649E-23
hbar = 1.0545718E-34

cross_sections = False

# Aliases used later in PSD helper (avoid NameError)
mRb = mass_rubid
kB = boltzmann

t_array = np.linspace(20, 44, 8) * 1e-3  # time of flight in s

fits_folder = "runs/multigo_2026-04-28_10-21-50"

# -------- Main calculations --------

def fit_2D_Gaussian(xy, sigma_x, sigma_y, amp, x0, y0, offset):
    x, y = xy
    return (offset + amp * np.exp(-((x - x0) ** 2 / (2 * sigma_x**2) + (y - y0) ** 2 / (2 * sigma_y**2)))).ravel()


def linear_fit(x, m, c):
    return m * x + c


def calculate_atom_number(image, sigma_x, sigma_y, amp):
    atom_number_2D = 2 * area_px * np.pi * abs(sigma_x) * abs(sigma_y) * amp / Rb_cross_section
    return atom_number_2D


def calculate_peak_PSD(peak_od_first, peak_od_extrap, T, sz_extrap, sz):
    # T is expected in Kelvin
    lambda_dB = math.sqrt((2 * math.pi * hbar**2) / (mass_rubid * boltzmann * T))
    n_col_extrap = peak_od_extrap / Rb_cross_section
    n_col = peak_od_first / Rb_cross_section
    n0_extrap = n_col_extrap / (math.sqrt(2 * math.pi) * sz_extrap)
    n0 = n_col / (math.sqrt(2 * math.pi) * sz)
    peak_PSD_extrap = n0_extrap * lambda_dB**3
    peak_PSD = n0 * lambda_dB**3

    return peak_PSD_extrap, peak_PSD


def calculate_temperature(slope_x, slope_y):
    """Calculate temperatures from the slopes of the width^2 vs time^2 plots. Units in microkelvin."""
    temp_x = slope_x * mass_rubid / boltzmann * 1e6
    temp_y = slope_y * mass_rubid / boltzmann * 1e6
    mean_temp = 0.5 * (temp_x + temp_y)
    return temp_x, temp_y, mean_temp


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


# Load the image

def load_image(filepath):
    with fits.open(filepath) as hdul:
        image_data = hdul[1].data
    od_image = image_data[3, :, :]  # Extract the 2D image from the data cube
    return od_image


def plots(t_array, widths_x, widths_y, amplitudes, fit_x=None, fit_y=None):
    plt.figure(1)
    t2 = t_array**2
    plt.plot(t2, widths_x**2, 'o', label='Width X$^2$')
    plt.plot(t2, widths_y**2, 'o', label='Width Y$^2$')
    if fit_x is not None:
        plt.plot(t2[skip_points:], fit_x, 'r--', label='X fit')
    if fit_y is not None:
        plt.plot(t2[skip_points:], fit_y, 'b--', label='Y fit')
    plt.xlabel('Time of Flight$^2$ (s$^2$)')
    plt.ylabel('Width$^2$ (m$^2$)')
    plt.legend()

    plt.figure(2)
    plt.plot(t_array, amplitudes, 'o', label='Amplitude')
    plt.xlabel('Time of Flight (s)')
    plt.ylabel('Amplitude (OD)')
    plt.legend()

    plt.show()


def plot_cross_sections(od_image, popt, title=None):
    """Plot horizontal/vertical cross-sections through fitted center: data vs 2D fit."""
    sigma_x_fit, sigma_y_fit, amp_fit, x0_fit, y0_fit, offset_fit = popt

    x0_int = int(np.clip(round(x0_fit), 0, od_image.shape[1] - 1))
    y0_int = int(np.clip(round(y0_fit), 0, od_image.shape[0] - 1))

    # Build fit image once for clean cross-sections
    y_idx, x_idx = np.indices(od_image.shape)
    fit_img = fit_2D_Gaussian((x_idx, y_idx), *popt).reshape(od_image.shape)

    x = np.arange(od_image.shape[1])
    y = np.arange(od_image.shape[0])

    data_cross_x = od_image[y0_int, :]
    fit_cross_x = fit_img[y0_int, :]

    data_cross_y = od_image[:, x0_int]
    fit_cross_y = fit_img[:, x0_int]

    fig, axs = plt.subplots(1, 2, figsize=(12, 4))
    axs[0].plot(x, data_cross_x, 'b.', ms=3, label='Data')
    axs[0].plot(x, fit_cross_x, 'r-', lw=2, label='2D fit')
    axs[0].set_title('Horizontal cross-section')
    axs[0].set_xlabel('x (px)')
    axs[0].set_ylabel('OD')
    axs[0].legend()

    axs[1].plot(y, data_cross_y, 'b.', ms=3, label='Data')
    axs[1].plot(y, fit_cross_y, 'r-', lw=2, label='2D fit')
    axs[1].set_title('Vertical cross-section')
    axs[1].set_xlabel('y (px)')
    axs[1].set_ylabel('OD')
    axs[1].legend()

    if title:
        fig.suptitle(title)

    plt.tight_layout()
    plt.show()


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
    widths_x = np.empty(len(fits_files))
    widths_y = np.empty(len(fits_files))
    atom_numbers = np.empty(len(fits_files))
    amplitudes = np.empty(len(fits_files))

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
            maxfev=1000000,
        )

        sigma_x_fit, sigma_y_fit, amp_fit, x0_fit, y0_fit, offset_fit = popt

        atom_numbers[idx] = calculate_atom_number(od_image, sigma_x_fit, sigma_y_fit, amp_fit)
        widths_x[idx] = np.abs(sigma_x_fit) * (px_size / magnification)  # Convert from pixels to meters
        widths_y[idx] = np.abs(sigma_y_fit) * (px_size / magnification)  # Convert from pixels to meters
        amplitudes[idx] = amp_fit

        if cross_sections:
            plot_cross_sections(od_image, popt, title=f"Image {idx+1}: {fits_files[idx]}")

    # Calculate the slopes for temperature calculation (fit width^2 vs t^2)
    t2 = t_array[skip_points:] ** 2
    popt_x, pcov_x = curve_fit(linear_fit, t2, widths_x[skip_points:] ** 2)
    popt_y, pcov_y = curve_fit(linear_fit, t2, widths_y[skip_points:] ** 2)
    slope_x, intercept_x = popt_x
    slope_y, intercept_y = popt_y

    # For plotting fit lines on width^2 vs t^2
    t2_full = t_array**2
    fit_x = slope_x * t2_full[skip_points:] + intercept_x
    fit_y = slope_y * t2_full[skip_points:] + intercept_y
    

    # Initial (t=0) widths from width^2 fit intercepts
    sigma0_x = math.sqrt(max(intercept_x, 0.0))
    sigma0_y = math.sqrt(max(intercept_y, 0.0))

    print(f"Intercept X (width^2): {intercept_x:.6e} m^2  ->  sigma0_x = {sigma0_x*1e6:.2f} µm")
    print(f"Intercept Y (width^2): {intercept_y:.6e} m^2  ->  sigma0_y = {sigma0_y*1e6:.2f} µm")

    temp_x, temp_y, mean_temp_uK = calculate_temperature(slope_x, slope_y)
    print(f"Temperatures (X, Y, mean): {temp_x:.3g}, {temp_y:.3g}, {mean_temp_uK:.3g} µK")
    plots(t_array, widths_x, widths_y, amplitudes, fit_x, fit_y)

    # Use sigma0 values for an initial cloud size estimate
    mean_sigma0 = 0.5 * (sigma0_x + sigma0_y)
    print(f"Initial cloud size (mean sigma0 from width^2 intercepts): {mean_sigma0*1e6:.2f} µm")

    # Calculate peak PSD
    sz_approx_extrap = math.sqrt(sigma0_x * sigma0_y)
    sz_approx = np.sqrt(np.min(widths_x) * np.min(widths_y))

    popt_amplitude, pcov_amplitude = curve_fit(linear_fit, t_array[:skip_points], amplitudes[:skip_points])
    _, intercept_amplitude = popt_amplitude

    max_amp = float(np.max(amplitudes))

    # mean_temp_uK -> K
    mean_temp_K = mean_temp_uK * 1e-6

    peak_PSD_extrap, peak_PSD = calculate_peak_PSD(
        max_amp, intercept_amplitude, mean_temp_K, sz_approx_extrap, sz_approx
    )
    print(f"Peak PSD (extrapolated): {peak_PSD_extrap:.2e}")
    print(f"Peak PSD (approx): {peak_PSD:.2e}")

    # Plot things
    


if __name__ == "__main__":
    main()

