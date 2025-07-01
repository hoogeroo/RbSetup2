import time
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from pylablib.devices import PrincetonInstruments

def configure_camera_for_acquisition(cam, nframes, exposure_time=0.01, trigger_mode="ext"):
    """
    Set up the camera for a sequence acquisition with the given parameters.
    
    Parameters:
    cam: Camera object
    nframes: Number of frames to acquire
    exposure_time: Exposure time for each frame (in seconds)
    trigger_mode: Trigger mode ('ext' for external, 'int' for internal)
    """
    cam.setup_acquisition(mode="sequence", nframes=nframes)
    cam.set_exposure(exposure_time)  # Set exposure time (default: 10ms)
    
    if trigger_mode == "ext":
        # Set to external trigger mode if specified
        cam.set_trigger_mode("ext")
        print("Trigger mode set to external. Waiting for external trigger.")
    else:
        # In internal mode, no external trigger is required
        print("Trigger mode set to internal.")
    
    cam.start_acquisition()

def acquire_frames(cam, nframes):
    """
    Acquire 'nframes' from the camera and return as a 3D numpy array.
    
    Parameters:
    cam: Camera object
    nframes: Number of frames to acquire
    
    Returns:
    data: 3D numpy array containing the acquired frames
    """
    frames = np.zeros((nframes, 512, 512))  # Assuming frame size is 512x512
    for i in range(nframes):
        print(f"Waiting for frame {i+1}...")
        cam.wait_for_frame()  # Wait for the next frame to be ready
        frame = cam.read_oldest_image()  # Read the oldest frame
        frames[i, :, :] = np.array(frame)
    
    cam.stop_acquisition()  # Stop acquisition after reading all frames
    return frames

def save_frames_to_fits(data, filename="X:\\temp.fits"):
    """
    Save the acquired frames as a FITS file.
    
    Parameters:
    data: 3D numpy array containing the acquired frames
    filename: Output file path (default: 'X:\\temp.fits')
    """
    hdu = fits.PrimaryHDU(data)
    hdu.writeto(filename)
    print(f"Frames saved to {filename}")

def display_frames(data):
    """
    Display the acquired frames using matplotlib.
    
    Parameters:
    data: 3D numpy array containing the acquired frames
    """
    nframes = data.shape[0]
    plt.figure(figsize=(10, 8))
    
    # Create a grid of subplots (3 rows, 4 columns) for frame display
    for i in range(nframes):
        plt.subplot(3, 4, i + 1)
        plt.imshow(data[i, :, :], cmap='gray')
        plt.title(f"Frame {i+1}")
        plt.axis('off')
    
    plt.tight_layout()
    plt.show()

def main():
    # Initialize the camera
    cam1=PrincetonInstruments.PicamCamera()

    # Set up acquisition parameters
    nframes = 3
    trigger_mode = "ext"  # Set to "ext" for external trigger or "int" for internal

    # Configure camera for acquisition
    configure_camera_for_acquisition(cam1, nframes, trigger_mode=trigger_mode)

    # Acquire frames
    data = acquire_frames(cam1, nframes)

    # Save the acquired frames to a FITS file
    save_frames_to_fits(data)

    # Display the acquired frames
    display_frames(data)

    # Close the camera connection
    cam1.close()

if __name__ == "__main__":
    main()
