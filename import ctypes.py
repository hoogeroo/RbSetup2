import ctypes

try:
    picam = ctypes.CDLL("/opt/PrincetonInstruments/picam/runtime/libpicam.so.5.14.7")
    print("PICAM library loaded successfully.")
except OSError as e:
    print(f"Error loading PICAM: {e}")