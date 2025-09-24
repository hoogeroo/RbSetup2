import numpy as np
from scipy.signal import convolve2d

def low_pass(pictures: np.ndarray):
    '''
    Apply a low-pass filter to the input pictures.
    '''
    kernel = np.array([[1, 2, 1],
                       [2, 4, 2],
                       [1, 2, 1]]) / 16

    pictures = np.apply_along_axis(lambda m: convolve2d(m, kernel, mode='same', boundary='wrap'), axis=(1, 2), arr=pictures)

    return pictures

def fringe_removal(FG: np.ndarray, backgrounds: list[np.ndarray]):
    # This version just does one fringeremove "On the fly"
    # It takes one foreground but any number of backgrounds and a background mask
    bgmask = prepare_bgmask()
    flat_ref = np.nonzero(bgmask.flatten())
    
    nk = np.size(flat_ref)
    backgrounds = np.array(backgrounds)
    sx,sy,nimgs = backgrounds.shape
    all_backgrounds = backgrounds.reshape([sx*sy,nimgs]).astype(float)

    FG_flat = FG.reshape([sx*sy]).astype(float)
    O1 = np.zeros([sx*sy])
    Rk = all_backgrounds[flat_ref,:].reshape([nk,nimgs])
    b = np.dot(np.transpose(Rk),Rk)

    Ak = FG_flat[flat_ref].reshape(nk)
    c = np.dot(np.transpose(Rk), Ak)

    try:
      sol = np.linalg.solve(b,c)
      O1 = np.dot(all_backgrounds,sol)

      odimage = np.reshape(-np.log(FG_flat/O1),[sx,sy])
      opref = np.reshape(O1,[sx,sy])
      print('Fringe reduction success!')
    except:
      BG=backgrounds[:,:,-1]
      odimage=np.reshape(-np.log(FG_flat/all_backgrounds[:,-1]),[sx,sy])
      opref=BG
      print('Fringe reduction Failed!')
      pass

    return odimage, opref


def prepare_bgmask(dims=[512,512],bgcor=100):
  # Comparing background images at the corners - each square uses (bgcor)x(bgcor) pixels
    bgmask = np.full(dims, 0.0)
    bgmask[0:(bgcor),0:(bgcor)] = 1.0
    bgmask[0:(bgcor),-bgcor:] = 1.0
    bgmask[-bgcor:,0:(bgcor)] = 1.0
    bgmask[-bgcor:,-bgcor:] = 1.0
    return bgmask