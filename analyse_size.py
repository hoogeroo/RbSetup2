import numpy as np
from matplotlib import pyplot as plt
from astropy.io import fits
from scipy.optimize import curve_fit

path = 'runs/2026-06-30_15-29-57.fits'

# def guess_widths(od_image):
#     x_profile = np.sum(od_image, axis=0)
#     y_profile = np.sum(od_image, axis=1)

#     def estimate_width_from_profile(profile):
#         max_val = np.max(profile)
#         half_max = max_val / 2
#         indices = np.where(profile >= half_max)[0]
#         if len(indices) > 0:
#             return (indices[-1] - indices[0]) / 2.355
#         return 20.0

#     sigma_x = estimate_width_from_profile(x_profile)
#     sigma_y = estimate_width_from_profile(y_profile)
#     return sigma_x, sigma_y


# def guess_amplitude(od_image):
#     return float(np.max(od_image))


# def guess_center(od_image):
#     x_profile = np.sum(od_image, axis=0)
#     y_profile = np.sum(od_image, axis=1)
#     x0 = int(np.argmax(x_profile))
#     y0 = int(np.argmax(y_profile))
#     return x0, y0


# def guess_offset(od_image):
#     return float(np.mean(od_image[0:10, 0:10]))

# def fit_2D_Gaussian(xy, sigma_x, sigma_y, amp, x0, y0, offset):
#     x, y = xy
#     return (offset + amp * np.exp(-((x - x0) ** 2 / (2 * sigma_x**2) + (y - y0) ** 2 / (2 * sigma_y**2)))).ravel()

with fits.open(path) as hdul:
    image_data = hdul[1].data
    od_image = image_data[3, :, :]

# sigma_x_guess, sigma_y_guess = guess_widths(od_image)
# amp_guess = guess_amplitude(od_image)
# x0_guess, y0_guess = guess_center(od_image)
# offset_guess = guess_offset(od_image)

# initial_guesses = [sigma_x_guess, sigma_y_guess, amp_guess, x0_guess, y0_guess, offset_guess]

# popt = curve_fit(fit_2D_Gaussian, np.indices(od_image.shape), od_image.ravel(), p0=initial_guesses, maxfev=10000)[0]
# sigma_x, sigma_y, amp, x0, y0, offset = popt
# print(f"Fitted parameters: sigma_x={sigma_x}, sigma_y={sigma_y}, amp={amp}, x0={x0}, y0={y0}, offset={offset}")

# plt.figure(figsize=(12, 5))
# plt.subplot(1, 2, 1)
# plt.imshow(od_image, cmap='viridis', origin='lower')
# plt.title('Original OD Image')
# plt.colorbar()
# plt.subplot(1, 2, 2)
# plt.imshow(fit_2D_Gaussian(np.indices(od_image.shape), *popt).reshape(od_image.shape), cmap='viridis', origin='lower')
# plt.title('Fitted 2D Gaussian')
# plt.colorbar()
# plt.show()

rms = np.sqrt(np.mean(od_image**2))
std_dev = np.std(od_image)
print(f"RMS of the OD image: {rms}")
print(f"Standard deviation of the OD image: {std_dev}")