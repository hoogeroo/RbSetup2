import numpy as np
import matplotlib.pyplot as plt

# Parameters
start = 1.42  # Peak value
end = 1.23    # Asymptotic value
t0 = 0      # Peak position (center of Lorentzian)
gamma = 5   # Width parameter

# Compute parameters
C = end
A = start - end

# Lorentzian decay function
def lorentzian_decay(t, A, gamma, t0, C):
    return A * gamma**2 / ((t - t0)**2 + gamma**2) + C

# Generate time points, focusing only on the decay region
time = np.linspace(0, 20, 500)  # Only after the peak

# Generate Lorentzian decay curve
amplitude = lorentzian_decay(time, A, gamma, t0, C)
print(amplitude)
# Plot
plt.figure(figsize=(8, 6))
plt.plot(time, amplitude, label="Lorentzian Decay", color="blue")
plt.axhline(end, color="red", linestyle="--", label="End (23)")
plt.xlabel("Time")
plt.ylabel("voltage")
plt.title("Lorentzian Decay (Peak to Asymptote)")
plt.legend()
plt.show()
