from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import os
import math
import re
from scipy.ndimage import gaussian_filter, label, find_objects

# -------- Control Parameters --------
skip_points = 2
magnification = 2.6
px_size = 16e-6  # Pixel size in meters
Rb_cross_section = 1.3e-13  # Cross-section of Rb in m^2
area_px = (px_size / magnification)**2  # Area per pixel in m^2

mass_rubid = 86.909184 * 1.66E-27
boltzmann = 1.380649E-23
hbar = 1.0545718E-34

cross_sections = True

# Fit mode: set True to use bimodal (thermal Gaussian + BEC TF) model.
# If False, uses a single 2D Gaussian model (as before).
bimodal_fit = True

ODT = True

# Aliases used later in PSD helper (avoid NameError)
mRb = mass_rubid
kB = boltzmann

t_array = np.linspace(20, 35.5, 8) * 1e-3  # time of flight in s

fits_folder = "runs/multigo_2026-05-13_11-41-39"

# -------- Main calculations --------
def find_ROI(image, smooth_sigma=1.0, threshold_factor=0.15, pad=8):
    """Find the region of interest (ROI) containing the atomic cloud."""
    image = np.array(image, copy=True)
    image[image < 0] = 0
    smoothed = gaussian_filter(image, sigma=smooth_sigma)

    threshold = threshold_factor * np.max(smoothed)
    mask = smoothed > threshold

    lab, _nlab = label(mask)
    slices = find_objects(lab)
    if not slices:
        # Fallback: take full frame if nothing detected
        h, w = image.shape
        return (0, h, 0, w), mask, smoothed

    areas = []
    for i, sl in enumerate(slices, start=1):
        areas.append((np.sum(lab[sl] == i), i, sl))

    _, best_label, best_slice = max(areas, key=lambda x: x[0])

    ys, xs = best_slice
    y0 = max(ys.start - pad, 0)
    y1 = min(ys.stop + pad, image.shape[0])
    x0 = max(xs.start - pad, 0)
    x1 = min(xs.stop + pad, image.shape[1])

    return (y0, y1, x0, x1), (lab == best_label), smoothed


def fit_2D_Gaussian(xy, sigma_x, sigma_y, amp, x0, y0, offset):
    x, y = xy
    return (
        offset
        + amp
        * np.exp(
            -(
                (x - x0) ** 2 / (2 * sigma_x**2)
                + (y - y0) ** 2 / (2 * sigma_y**2)
            )
        )
    ).ravel()


def fit_TF(xy, amp, x0, y0, R_x, R_y, offset):
    """2D Thomas-Fermi column-density-like profile (clipped to 0 outside ellipse)."""
    x, y = xy
    inside = 1.0 - ((x - x0) / R_x) ** 2 - ((y - y0) / R_y) ** 2
    inside = np.clip(inside, 0.0, None)
    return (offset + amp * inside ** (3 / 2)).ravel()


def fit_bimodal_TF_Gaussian(xy, sigma_x, sigma_y, amp_th, amp_bec, x0, y0, R_x, R_y, offset):
    """Bimodal model: thermal 2D Gaussian + BEC TF, with shared center and shared offset."""
    x, y = xy

    thermal = amp_th * np.exp(
        -((x - x0) ** 2 / (2 * sigma_x**2) + (y - y0) ** 2 / (2 * sigma_y**2))
    )

    inside = 1.0 - ((x - x0) / R_x) ** 2 - ((y - y0) / R_y) ** 2
    inside = np.clip(inside, 0.0, None)
    bec = amp_bec * inside ** (3 / 2)

    return (offset + thermal + bec).ravel()


def linear_fit(x, m, c):
    return m * x + c


def calculate_atom_number(image, sigma_x, sigma_y, amp):
    atom_number_2D = 2 * area_px * np.pi * abs(sigma_x) * abs(sigma_y) * amp / Rb_cross_section
    return atom_number_2D


def calculate_peak_PSD(
    peak_od_first, T, peak_od_extrap=None, sz_extrap=None, sz=None, ODT_w=40e-6
):
    # T is expected in Kelvin
    lambda_dB = math.sqrt((2 * math.pi * hbar**2) / (mass_rubid * boltzmann * T))

    n_col_extrap = peak_od_extrap / Rb_cross_section
    n_col = peak_od_first / Rb_cross_section
    if ODT is False:
        n0_extrap = n_col_extrap / (math.sqrt(2 * math.pi) * sz_extrap)
        n0 = n_col / (math.sqrt(2 * math.pi) * sz)
        peak_PSD_extrap = n0_extrap * lambda_dB**3
        peak_PSD = n0 * lambda_dB**3
    else:
        n0_extrap = n_col_extrap / (math.sqrt(2 * math.pi) * sz_extrap)
        n_col = peak_od_first / Rb_cross_section
        n0 = n_col / (math.sqrt(2 * math.pi) * ODT_w)
        peak_PSD = n0 * lambda_dB**3
        peak_PSD_extrap = (
            n0_extrap * lambda_dB**3
        )  # Not meaningful in ODT case since extrapolation is based on free expansion assumptions

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


def _fit_gaussian_roi(od_roi):
    """Gaussian pre-fit on ROI to seed the bimodal fit."""
    sigma_x_guess, sigma_y_guess = guess_widths(od_roi)
    amp_guess = guess_amplitude(od_roi)
    x0_guess, y0_guess = guess_center(od_roi)
    offset_guess = guess_offset(od_roi)

    initial_guesses = [sigma_x_guess, sigma_y_guess, amp_guess, x0_guess, y0_guess, offset_guess]

    y_idx, x_idx = np.indices(od_roi.shape)

    # Bounds for a sane Gaussian fit:
    h, w = od_roi.shape
    px_min = 0.5
    lower = [px_min, px_min, 0.0, 0.0, 0.0, -np.inf]
    upper = [max(h, w), max(h, w), 2.0 * np.max(od_roi) + 1e-12, w - 1, h - 1, np.inf]

    popt, pcov = curve_fit(
        fit_2D_Gaussian,
        (x_idx, y_idx),
        od_roi.ravel(),
        p0=initial_guesses,
        bounds=(lower, upper),
        maxfev=200000,
    )
    return popt, pcov


def _fit_bimodal_roi(od_roi):
    """Bounded bimodal fit on ROI. Returns popt in the bimodal parameter order."""
    # Step 1: Gaussian pre-fit for decent initial values
    g_popt, _ = _fit_gaussian_roi(od_roi)
    sigma_x_g, sigma_y_g, amp_g, x0_g, y0_g, offset_g = g_popt

    # Step 2: seed bimodal parameters
    amp_th0 = 0.6 * max(amp_g, 0.0)
    amp_bec0 = 0.4 * max(amp_g, 0.0)

    # TF radii initial guess: a few sigmas
    R_x0 = max(2.0 * float(abs(sigma_x_g)), 2.0)
    R_y0 = max(2.0 * float(abs(sigma_y_g)), 2.0)

    p0 = [
        float(abs(sigma_x_g)),
        float(abs(sigma_y_g)),
        float(amp_th0),
        float(amp_bec0),
        float(x0_g),
        float(y0_g),
        float(R_x0),
        float(R_y0),
        float(offset_g),
    ]

    y_idx, x_idx = np.indices(od_roi.shape)
    h, w = od_roi.shape
    max_od = float(np.max(od_roi))

    # Bounds: keep broad, just prevent nonsense
    px_min = 0.5
    lower = [
        px_min,  # sigma_x
        px_min,  # sigma_y
        0.0,  # amp_th
        0.0,  # amp_bec
        0.0,  # x0
        0.0,  # y0
        1.0,  # R_x
        1.0,  # R_y
        -np.inf,  # offset
    ]
    upper = [
        max(h, w),  # sigma_x
        max(h, w),  # sigma_y
        3.0 * max_od + 1e-12,  # amp_th
        3.0 * max_od + 1e-12,  # amp_bec
        w - 1,  # x0
        h - 1,  # y0
        float(w),  # R_x
        float(h),  # R_y
        np.inf,  # offset
    ]

    popt, pcov = curve_fit(
        fit_bimodal_TF_Gaussian,
        (x_idx, y_idx),
        od_roi.ravel(),
        p0=p0,
        bounds=(lower, upper),
        maxfev=400000,
    )
    return popt, pcov, g_popt


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


def plot_cross_sections(od_image, model_fn, popt, title=None, components=None):
    """Plot horizontal/vertical cross-sections through fitted center: data vs model.

    components: optional dict of {name: (model_fn, popt_component)} plotted as dashed.
    """
    # Infer center location from parameter list.
    # Gaussian: [..., x0, y0, ...] at indices 3,4
    # Bimodal:  [..., x0, y0, ...] at indices 4,5
    if model_fn is fit_2D_Gaussian:
        x0_fit, y0_fit = popt[3], popt[4]
    else:
        x0_fit, y0_fit = popt[4], popt[5]

    x0_int = int(np.clip(round(x0_fit), 0, od_image.shape[1] - 1))
    y0_int = int(np.clip(round(y0_fit), 0, od_image.shape[0] - 1))

    y_idx, x_idx = np.indices(od_image.shape)
    fit_img = model_fn((x_idx, y_idx), *popt).reshape(od_image.shape)

    x = np.arange(od_image.shape[1])
    y = np.arange(od_image.shape[0])

    data_cross_x = od_image[y0_int, :]
    fit_cross_x = fit_img[y0_int, :]

    data_cross_y = od_image[:, x0_int]
    fit_cross_y = fit_img[:, x0_int]

    fig, axs = plt.subplots(1, 2, figsize=(12, 4))
    axs[0].plot(x, data_cross_x, 'k.', ms=3, label='Data')
    axs[0].plot(x, fit_cross_x, 'r-', lw=2, label='Fit')
    axs[0].set_title('Horizontal cross-section')
    axs[0].set_xlabel('x (px)')
    axs[0].set_ylabel('OD')

    axs[1].plot(y, data_cross_y, 'k.', ms=3, label='Data')
    axs[1].plot(y, fit_cross_y, 'r-', lw=2, label='Fit')
    axs[1].set_title('Vertical cross-section')
    axs[1].set_xlabel('y (px)')
    axs[1].set_ylabel('OD')

    if components:
        for name, (fn, p) in components.items():
            comp_img = fn((x_idx, y_idx), *p).reshape(od_image.shape)
            axs[0].plot(x, comp_img[y0_int, :], '--', lw=1.5, label=name)
            axs[1].plot(y, comp_img[:, x0_int], '--', lw=1.5, label=name)

    axs[0].legend()
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

    # Diagnostics: store amplitudes depending on fit used
    amplitudes_total = np.empty(len(fits_files))
    amplitudes_th = np.empty(len(fits_files))
    amplitudes_bec = np.empty(len(fits_files))

    atom_numbers = np.empty(len(fits_files))

    for idx, file in enumerate(fits_files):
        print(f"Processing file: {file}")
        filepath = os.path.join(cwd, file)
        od_image = load_image(filepath)
        image_list[idx, :, :] = od_image

    for idx in range(len(fits_files)):
        od_image_full = image_list[idx, :, :]

        # Always fit on an ROI for stability (especially important for bimodal)
        roi, _mask, od_smooth = find_ROI(od_image_full)
        y0r, y1r, x0r, x1r = roi
        od_roi = od_image_full[y0r:y1r, x0r:x1r]

        if bimodal_fit:
            b_popt, _b_pcov, g_seed = _fit_bimodal_roi(od_roi)
            (
                sigma_x_fit,
                sigma_y_fit,
                amp_th_fit,
                amp_bec_fit,
                x0_fit,
                y0_fit,
                R_x_fit,
                R_y_fit,
                offset_fit,
            ) = b_popt

            # Thermal widths used for temperature extraction
            widths_x[idx] = abs(sigma_x_fit) * (px_size / magnification)
            widths_y[idx] = abs(sigma_y_fit) * (px_size / magnification)

            amplitudes_th[idx] = float(amp_th_fit)
            amplitudes_bec[idx] = float(amp_bec_fit)
            amplitudes_total[idx] = float(amp_th_fit + amp_bec_fit)

            # Keep legacy "atom_numbers" as thermal-only estimate (Gaussian integral).
            # If you want N_BEC too, we can add proper TF integral later.
            atom_numbers[idx] = calculate_atom_number(od_roi, sigma_x_fit, sigma_y_fit, amp_th_fit)

            if cross_sections:
                # Build component curves for plotting on ROI
                # Thermal-only component = Gaussian with same center/offset
                th_p = [sigma_x_fit, sigma_y_fit, amp_th_fit, x0_fit, y0_fit, offset_fit]

                def _thermal_only(xy, sigma_x, sigma_y, amp_th, x0, y0, offset):
                    return fit_2D_Gaussian(xy, sigma_x, sigma_y, amp_th, x0, y0, offset)

                # TF-only component
                tf_p = [amp_bec_fit, x0_fit, y0_fit, R_x_fit, R_y_fit, offset_fit]

                plot_cross_sections(
                    od_roi,
                    fit_bimodal_TF_Gaussian,
                    b_popt,
                    title=f"ROI {idx+1}: {fits_files[idx]} (bimodal)",
                    components={
                        "Thermal": (_thermal_only, th_p),
                        "BEC(TF)": (fit_TF, tf_p),
                    },
                )
        else:
            # Legacy: single 2D Gaussian fit on ROI
            g_popt, _g_pcov = _fit_gaussian_roi(od_roi)
            sigma_x_fit, sigma_y_fit, amp_fit, x0_fit, y0_fit, offset_fit = g_popt

            widths_x[idx] = abs(sigma_x_fit) * (px_size / magnification)
            widths_y[idx] = abs(sigma_y_fit) * (px_size / magnification)

            amplitudes_th[idx] = float(amp_fit)
            amplitudes_bec[idx] = 0.0
            amplitudes_total[idx] = float(amp_fit)

            atom_numbers[idx] = calculate_atom_number(od_roi, sigma_x_fit, sigma_y_fit, amp_fit)

            if cross_sections:
                plot_cross_sections(
                    od_roi,
                    fit_2D_Gaussian,
                    g_popt,
                    title=f"ROI {idx+1}: {fits_files[idx]} (gaussian)",
                )

    # For temperature and your existing plots, use thermal widths.
    # For amplitude-time plots, use total amplitude by default.
    amplitudes = amplitudes_total

    # Calculate the slopes for temperature calculation (fit width^2 vs t^2)
    t2 = t_array[skip_points:] ** 2
    popt_x, _pcov_x = curve_fit(linear_fit, t2, widths_x[skip_points:] ** 2)
    popt_y, _pcov_y = curve_fit(linear_fit, t2, widths_y[skip_points:] ** 2)
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
    sz_approx_extrap = math.sqrt(sigma0_x * sigma0_y) / 2
    sz_approx = np.sqrt(np.min(widths_x) * np.min(widths_y)) / 2

    popt_amplitude, _pcov_amplitude = curve_fit(linear_fit, t_array[:skip_points], amplitudes[:skip_points])
    _, intercept_amplitude = popt_amplitude

    max_amp = float(np.max(amplitudes))

    peak_PSD_extrap, peak_PSD = calculate_peak_PSD(
        peak_od_first=max_amp,
        T=temp_y * 1e-6,
        peak_od_extrap=intercept_amplitude,
        sz_extrap=sz_approx_extrap,
        sz=sz_approx,
    )
    print(f"Peak PSD (extrapolated): {peak_PSD_extrap:.2e}")
    print(f"Peak PSD (approx): {peak_PSD:.2e}")


if __name__ == "__main__":
    main()

