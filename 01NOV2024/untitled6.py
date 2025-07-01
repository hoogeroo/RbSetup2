import numpy as np

# Initialize constants
num_subsets = 2
subset_size = 32
ramp_index = 15  # Index of the value that ramps up (0-based)

# Create an array of constant values (e.g., 1.0)
base_value = 1.0
subsets = []

for _ in range(num_subsets):
    subset = [base_value] * subset_size  # Start with all values constant
    ramp_values = np.linspace(1.0, 5.0, subset_size)  # Ramp values for one index
    for i in range(subset_size):
        subset[ramp_index] = ramp_values[i]
        subsets.append(subset.copy())  # Append the modified subset

print(subsets)