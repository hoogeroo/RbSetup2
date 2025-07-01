import socket
#import testpicam as tp  #import test picam (big camera)
import testpicam_copy as tp #using the copy file
import matplotlib.pyplot as plt
import numpy as np
import threading
import sys
import os

HOST = "10.103.154.4"  # This IP address 
#HOST = "127.0.0.1"#Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

#camlist=bf.GetCamList()
#cam=camlist[0]
#print(camlist)
os.environ['FLIR_GENTL64_CTI_VS140']="c:\Program Files\FLIR Systems\Spinnaker\cti\vs2015\FLIR_GenTL_v140.cti"

roi = [[200,800], [750,1350]]
condition = None
#fig = plt.figure()

t1 = None
while True:
  print('Variable defined\nOpening socket...')
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    print(f'Listening at:\n HOST:{HOST}\nPORT={PORT}')
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected to {addr}")
        while True:
            cmd = conn.recv(32)
            if not cmd:
                break
            #conn.sendall(cmd)
            cmds=cmd.decode()
            print(cmds)
            
            if cmds=="TAKE_PICS":
                print("Taking pictures")
                try:
                    #result = bf.take_three(roi)
                    result = tp.take_three(roi)
                except Exception as err:
                    print(f'Error: {err}')
                    result = False
                print(f'Imaging successful: {result}')
                #conn.sendall(data)
            
            elif cmds=="CYCLE":
                if not bf.continue_recording:
                    condition = threading.Event()
                    #bf.continue_recording = True
                    t1=threading.Thread(target=bf.run, daemon = True, args=[roi, condition])#, fig])
                    print("Start cycling")
                    t1.start()
                else:
                    print('Thread already running!\n Please send "STOP_CYCLE" to remove it before using "CYCLE" again!')
            
            elif cmds=="STOP_CYCLE":
                if bf.continue_recording:
                    if condition:
                        condition.set()
                    #bf.continue_recording=False
                    bf.handle_close(condition)
                    #bf.fig_close()
                    condition = None
                    t1.join()
                    t1 = None
                    print("Stopped cycling")
                    
            elif cmds=="FLUO":
                if bf.continue_recording:
                    fluo = bf.GetFluo()
                    conn.sendall(str(fluo).encode())
                    #print("Returning fluorescence")
                    print(f'Fluorescence: {fluo}')
                else:
                    pass
                    #conn.sendall('0.00'.encode())
            
            elif cmds=="EXIT":
                #sys.exit(0)
                break
                
            elif cmds[:3]=="ROI":
                roistr = cmds.split(',')
                roi_raw = [int(x) for x in roistr[1:]]
                roirows = roi_raw[:2]; roicols = roi_raw[2:]
                roi = [roirows, roicols]
                
