import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits

# Open the FITS file
filename = "temp.fit"
with fits.open(filename) as hdul:
    hdul.info()  # Show file structure
    data = hdul[0].data  # Get data array (shape: 2, 512, 512)

# Select one layer to display (e.g., the first layer)
layer_index = 0  # Change to 1 if you want the second layer
image_data = data[layer_index]

# Plot with blue-to-red colormap
plt.figure(figsize=(10, 8))
plt.imshow(image_data, cmap='bwr', origin='lower')  # 'bwr' is blue to red
plt.colorbar(label="Pixel Value")
plt.title(f"FITS Image - Layer {layer_index} (Blue to Red)")
plt.show()
