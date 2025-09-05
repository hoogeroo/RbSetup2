import numpy as np

def low_pass(pictures: np.ndarray):
    '''
    Apply a low-pass filter to the input pictures.
    '''
    kernel = np.array([[1, 2, 1],
                       [2, 4, 2],
                       [1, 2, 1]]) / 16

    pictures = np.apply_along_axis(lambda m: convolve2d(m, kernel, mode='same', boundary='wrap'), axis=(1, 2), arr=pictures)

    return pictures
