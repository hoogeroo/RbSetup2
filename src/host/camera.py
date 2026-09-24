'''
camera.py: responsible for connecting to the camera server running on the windows computer in the lab
'''

import os
import time
import socket
import numpy as np
import struct
from PIL import Image
import io
import threading

from astropy.io import fits

#TCPIP = '10.103.154.4'
TCPIP= '130.216.51.122'
PORT = 54321
TMPFITS = '/home/lab/Documents/zdrive/kuroTemp/temp.fit'
BFFITS = '/home/lab/Documents/zdrive/kuroTemp/BFtemp.fits'

BF_PORT = 54322
VIDEO_PORT = 54323

'''
when this class is instantiated it tries to connect to the camera server
'''
class CameraConnection:
    # try to connect to the camera server
    def __init__(self):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.settimeout(1)
        conn.connect((TCPIP,PORT))

        self.conn_bf = None
        self.conn_video = None

        self.bf_connected = False
        self.bf_cycling = False

        self.video_thread = None
        self.video_running = False
        self.latest_frame = None
        self.video_frame_number = 0

        # message = 'alive?'
        # conn.send(message.encode())

        # server only responds the first time?
        # print(conn.recv(5))

        conn.close()

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

    def read_bf(self, timeout=10):
        t = 0
        while not (os.path.exists(BFFITS)):
            time.sleep(0.1)
            t = t + 1
            if (t > timeout * 10): 
                raise TimeoutError(f"Timeout waiting for BF image file: {BFFITS}")
        
        hdu = fits.open(BFFITS)
        print(f"BF image opened: {BFFITS}")
        imgdata = hdu[0].data
        outdata = np.array(imgdata)
        hdu.close()

        os.remove(BFFITS)

        return outdata
    
    def connect_bf(self, timeout=10):
        if self.conn_bf is not None:
            return
        self.conn_bf = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_bf.settimeout(timeout)
        self.conn_bf.connect((TCPIP, BF_PORT))
        self.bf_connected = True

        print("BF connected successfully")

    def start_cycle(self, timeout=10):
        message = "CYCLE"
        self.conn_bf.send(message.encode())
        self.bf_cycling = True

    def stop_cycle(self, timeout=10):
        message = "STOP_CYCLE"
        self.conn_bf.send(message.encode())
        self.bf_cycling = False
        print("BF cycle stopped")

    def get_fluo_bf(self, timeout=10):
        message = 'FLUO'
        self.conn_bf.send(message.encode())

        response = self.conn_bf.recv(64)
        if not response:
            raise ConnectionError("Blackfly socket did not send message")
        
        return float(response.decode().strip())

    def close_bf(self, timeout=10):
        self.conn_bf.close()
        self.conn_bf = None

    def bf_shoot(self, timeout=10):
        message = 'TAKE_PICS'
        self.conn_bf.send(message.encode())
        print("BF images taken")

    def connect_video(self, timeout=1):
        if self.conn_video is not None:
            return
        
        self.conn_video = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_video.settimeout(timeout)
        self.conn_video.connect((TCPIP, VIDEO_PORT))

        self.video_running = True
        self.latest_frame = None
        self.video_frame_number = 0

        self.video_thread = threading.Thread(target=self._video_loop, args=(self.conn_video,), daemon=True)
        self.video_thread.start()
    
    def close_video(self, timeout=10):
        self.video_running = False

        if self.video_thread is not None:
            try:
                self.conn_video.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
        
        self.conn_video.close()
        self.conn_video = None

        if self.video_thread is not None:
            self.video_thread.join(timeout=1)
            self.video_thread = None

        self.latest_frame = None
        print('BF video closed')

    @staticmethod
    def recv_exact(sock, n):
        """Receive exactly n bytes from the socket."""
        data = bytearray()

        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                raise ConnectionError("Socket connection closed unexpectedly")
            data.extend(packet)

        return bytes(data)
    
    def _video_loop(self, sock):
        while self.video_running:
            try:
                header = self.recv_exact(sock, 4)
                frame_length = struct.unpack("!I", header)[0]

                jpeg_data = self.recv_exact(sock, frame_length)

                self.latest_frame = jpeg_data
                self.video_frame_number += 1

            except (ConnectionError, socket.timeout, OSError):
                break
        
        self.video_running = False

if __name__ == '__main__':
    camera = CameraConnection()
    camera.shoot(1)

    # need to trigger the camera here

    picture = camera.read()

    import matplotlib.pyplot as plt

    plt.imshow(picture[0, :, :], aspect='auto')
    plt.show()
