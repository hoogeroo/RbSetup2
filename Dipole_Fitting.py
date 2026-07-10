import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d


aom_power = np.array([0.0, 1, 2, 3, 4, 4.5, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100])
output_power = np.array([381.2e-6, 382.5e-6, 404.1e-6, 471.8e-6, 705.5e-6, 947.2e-6, 1.293e-3, 2.371e-3, 4.012e-3, 6.233e-3, 8.948e-3, 12.24e-3, 16.17e-3,
                20.36e-3, 24.97e-3, 30.01e-3, 35.44e-3, 41.14e-3, 47.42e-3, 53.82e-3, 60.5e-3, 67.3e-3, 74.41e-3, 81.74e-3, 89.21e-3, 96.84e-3, 104.9e-3,
                145.5e-3, 189.7e-3, 235.1e-3, 277.2e-3, 318.4e-3, 353.6e-3, 385.4e-3, 412.0e-3, 431.2e-3, 448.1e-3, 464.5e-3, 474.0e-3, 482.6e-3, 490.1e-3, 495.9e-3])
output_power -= min(output_power)
max_power = max(output_power)

normalised_power = output_power / max_power * 100

interp_func = interp1d(normalised_power, aom_power, kind='cubic')
print(interp_func(0))  
# plt.plot(normalised_power, interp_func(aom_power), '--', label='?')
plt.plot(normalised_power, aom_power,'o', label='Data Points')
plt.plot(normalised_power, interp_func(normalised_power), '-', label='Cubic Interpolation')

plt.ylabel('AOM Power (%)')
plt.xlabel('Output Power (Normalized to Max, %)')
plt.title('Dipole Amplitude Calibration')
plt.legend()
plt.grid()
plt.show()