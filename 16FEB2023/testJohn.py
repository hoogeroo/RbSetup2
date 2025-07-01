from ctypes import *
AIOUSB = cdll.LoadLibrary("/usr/local/lib/libaiousb.so")

def GetDevices():
    """Return a bitmask of all detected deviceIndices."""
    return AIOUSB.GetDevices()

def DACOutputProcess(index, Hz, numSamples, sampleData):
    """The simplest way to output one or more simultaneous analog output waveforms (buffers of periodically-timed DAC values)."""
    writeHz = c_double(Hz)
    dataBuf = (c_short * numSamples)()
    for i in range(numSamples):
        dataBuf[i] = sampleData[i]
    status = AIOUSB.CSA_DACOutputProcess(index, byref(writeHz), numSamples, byref(dataBuf))
    return status, writeHz.value

if __name__ == "__main__":
        boardsMask = GetDevices()
        if boardsMask == 0:
            print("No valid AIOUSB devices were detected.\nPlease confirm your USB device is connected, powered,\nand the drivers are installed correctly (check Device Manager).")
            exit()

        for iFrame in range(100000//14):
            status, Hz = DACOutputProcess(0, 10000.0, 14, [1,10,100,1000,2000,3000,4000,4095,4000,3000,2000,1000,100,0])
            if status == 0:
                print("DACOutputProcess() worked, actual Hz = ", Hz)
            else:
                print("DACOutputProcess() failed with status = ", status)


