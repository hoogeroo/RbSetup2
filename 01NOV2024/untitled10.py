import json
import numpy as np

"""
with open("stages.json", "r") as f:
    stages = json.load(f)
voltage_arrays = [np.array(stage[0]) for stage in stages]
timesteps = [stage[2] for stage in stages]
channel_settings = [stage[1] for stage in stages]  # Channel settings
for i in range(len(voltage_arrays)):
    voltages = voltage_arrays[i]
    timestep = timesteps[i]
    channels = channel_settings[i]
    
    """
"""
first we have our length of t_range, we then multiply the entire array size by
that length so that they are consistent e.g

we start with 7 voltage values and a voltage ramp, we also need this to be
transformed into a 32bit array. 

So first we make the array for the voltage ramp, which has the length of the
total timesteps. this is then transformed into a 32bit array of 1s, with the other
dac values being multiplied.


"""
import numpy as np

rstart = 0.0
rend = 1.0
timesteps = 20.0
t1 = np.linspace(rstart, rend, int(timesteps))  # Ensure final value is `rend`
print(t1,len(t1))

import numpy as np
import matplotlib.pyplot as plt

# Define the Lorentzian curve
def lorentzian_decreasing(x, amp, offset, timeconstant):
    return amp / (1 + ((x - offset) / timeconstant)**2)

# Parameters
amp = 5.30          # Amplitude of the Lorentzian
offset = 5.0       # Offset along the x-axis
timeconstant = 4.0 # Time constant

# Generate x values for the decreasing section (right side of the peak)
x = np.linspace(offset, offset + 5*timeconstant, 500)
y = lorentzian_decreasing(x, amp, offset, timeconstant)

# Plot
plt.figure(figsize=(8, 5))
plt.plot(x, y, label="Lorentzian Decreasing Section", color="blue")
plt.title("Decreasing Section of Lorentzian Curve")
plt.xlabel("x")
plt.ylabel("y")
plt.axvline(offset, color="gray", linestyle="--", label="Offset")
plt.legend()
plt.grid()
plt.show()

