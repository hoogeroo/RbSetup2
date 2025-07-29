'''
camera.py: responsible for connecting to the camera server running on the windows computer in the lab
'''

import os
import time
import socket
import numpy as np

from astropy.io import fits

TCPIP = '10.103.154.4'
PORT = 54321
TMPFITS = 'zdrive/kuroTemp/temp.fit'

'''
when this class is instantiated it tries to connect to the camera server
'''
class CameraConnection:
    # try to connect to the camera server
    def __init__(self):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.settimeout(1)
        conn.connect((TCPIP,PORT))

        message = 'alive?'
        conn.send(message.encode())

        # server only responds the first time?
        # print(conn.recv(5))

        conn.close()

        print("camera connected")

    # send a command to the camera server to acquire nframes. doesn't actually trigger the camera, just sends a command to the server. camera needs to be triggered separately
    def shoot(self, nframes):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.settimeout(1)
        conn.connect((TCPIP, PORT))

        message = 'acquire' + str(nframes)
        conn.send(message.encode())

        conn.close()

    # read the file created by the camera server saved on the network drive. waits for `timeout` seconds for the file to appear
    def read(self, timeout=10):
        t = 0
        while not (os.path.exists(TMPFITS)):
            time.sleep(0.1)
            t = t + 1
            if (t > timeout * 10): break

        hdu = fits.open(TMPFITS)
        imgdata = hdu[0].data
        outdata = np.array(imgdata)
        hdu.close()

        os.remove(TMPFITS)

        return outdata

if __name__ == '__main__':
    camera = CameraConnection()
    camera.shoot(1)

    # need to trigger the camera here

    picture = camera.read()

    import matplotlib.pyplot as plt

    plt.imshow(picture[0, :, :], aspect='auto')
    plt.show()
