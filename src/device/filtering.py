import numpy as np
from scipy.signal import convolve2d

def low_pass(pictures: np.ndarray):
    '''
    Apply a low-pass filter to the input pictures.
    '''
    kernel = np.array([[1, 2, 1],
                       [2, 4, 2],
                       [1, 2, 1]]) / 16

    pictures = convolve2d(pictures, kernel, mode='same', boundary='wrap')

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

def fft_filter(od_image: np.ndarray):
   remove_atom_mask = np.ones(od_image.shape, dtype = float)
   remove_atom_mask[200:-200, 200:-200] = 0
   empty_mean = np.mean(od_image * remove_atom_mask)

   od_image -= empty_mean
   fft_od = np.fft.fftshift(np.fft.fft2(od_image))
   fft_od[160:230, 0:140] = 0
   fft_od[512-230:512-160, 512-140:512] = 0
   fft_od[130:156, 302:328] = 0
   fft_od[512-156:512-130, 512-328:512-302] = 0
   fft_od[253:257, 240:247] = 0
   fft_od[512-257:512-253, 512-247:512-240] = 0
   od_image = np.abs(np.fft.ifft2(np.fft.ifftshift(fft_od)))
   od_image = filter_mask(od_image)

   return od_image

def filter_mask(z):

    na=z.shape[0];nb=z.shape[1]
    out=np.zeros([na-2,nb-2])

    for i in [-1,0,1]:
        for j in [-1,0,1]:
            out+=0.1*(1+(i==j and not i))*z[1+i:na-1+i,1+j:nb-1+j]

    return out

def prepare_bgmask(dims=[512,512],bgcor=100):
  # Comparing background images at the corners - each square uses (bgcor)x(bgcor) pixels
    bgmask = np.full(dims, 0.0)
    bgmask[0:(bgcor),0:(bgcor)] = 1.0
    bgmask[0:(bgcor),-bgcor:] = 1.0
    bgmask[-bgcor:,0:(bgcor)] = 1.0
    bgmask[-bgcor:,-bgcor:] = 1.0
    return bgmask