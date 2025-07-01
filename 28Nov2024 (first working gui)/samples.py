from AIOUSB import *
from time import sleep


# procedure ADCallback(pBuf: PWord; BufSize, Flags, Context: UInt32); cdecl;
def myADCCallback(data, length, flags, context):
    """ local callback function """
    print("data, length, flags, context:", data, length, flags, context)
    return 1
             

                 
if __name__ == "__main__":# main code section
    if True:
        print("AIOUSB Python introductory sample using AIOUSB.py\n")

        boardsMask = AIOUSB.GetDevices()
        if boardsMask == 0:
            print("No valid AIOUSB devices were detected.\nPlease confirm your USB device is connected, powered,\nand the drivers are installed correctly (check Device Manager).")
            exit()
    
        boardsFound = 0
        for di in range(0, 31):
            if 0 != boardsMask & (1 << di):
                boardsFound = boardsFound + 1
                displayBoardInfo(di)
        print("\nAIOUSB Boards found:", boardsFound)


#
# ?_maybe_TODO: convert this series of if False: statements into a menu selection prompt? ?instead split off into individual files?
#
# Custom EEPROM sample
    if False:
        status = CustomEEPROMWrite(diOnly, 0, 1, 0xAA)
        if status == 0:
            print("CustomEEPROMWrite() worked, wrote 0xAA")
        else:
            print("CustomEEPROMWrite() failed with status = ", status)
        status, data = CustomEEPROMRead(diOnly, 0, 1)
        if status == 0:
            print("CustomEEPROMRead() worked, data = {0:X}".format(data[0]))
        else:
            print("CustomEEPROMRead() failed with status = ", status)



# DAC Waveform sample
    if False:
        DACSetBoardRange(diOnly, 0)
        status, Hz = DACOutputProcess(diOnly, 10000.0, 14, [1,10,100,1000,10000,20000,30000,40000,50000,60000,65535,0,65535,0])
        if status == 0:
            print("DACOutputProcess() worked, actual Hz = ", Hz)
        else:
            print("DACOutputProcess() failed with status = ", status)
        DACDirect(diOnly, 0, 0)



# DAC MultiDirect sample
    if False:
        DACSetBoardRange(diOnly, 0)
        dacData = [0,0, 1,0, 2,0, 3,0, 4,0, 5,0, 6,0, 7,0]
        status = DACMultiDirect(diOnly, dacData, 8)
        if status == 0:
            print("DACMultiDirect() worked")
        else:
            print("DACMultiDirect() failed with status = ", status)
        
# ADC Continuous sample (USB-AI16-2A)
    if False:
        config = [0, 0]
        status = ADC_SetConfig(diOnly, config)
        if status == 0:
            print("ADC_SetConfig() was successful.")
        else:
            print("ADC_SetConfig() status:", status)  
            
        status = AIOUSB_ClearFIFO(diOnly, 0)
        if status == 0:
            print("AIOUSB_ClearFIFO() was successful.")
        else:
            print("AIOUSB_ClearFIFO() status:", status)  

        status = ADC_BulkContinuousRingStart(diOnly)
        if status == 0:
            print("ADC_BulkContinuousRingStart() was successful.")
        else:
            print("ADC_BulkContinuousRingStart() status:", status)

        while True:
            status, data = ADC_ReadData(diOnly, config, 1, -9)
            if status == 0:
                print( "{: 0.3f} {: 0.3f} ".format(data[0], data[1]))
            else:
               print("ADC_ReadData status is bad:", status)    # possible timeout

# ADC Continuous sample (USB-AIO16-16F Family)
    if False:
        config = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 5, 0xF0, 0, 0x00]
        status = ADC_SetCal(diOnly, b":NONE:")

        status, Hz = ADC_FullStartRing(diOnly, config, b":NONE:", 101.01, 1024*1024, 1)
        print("Acquiring at", Hz, "(requested 101.01 Hz)")

        while True:
            status, data = ADC_ReadData(diOnly, config, 1, -999)
            if status == 0:
                print( "{: 0.3f} {: 0.3f} {: 0.3f} {: 0.3f} {: 0.3f} {: 0.3f} {: 0.3f} {: 0.3f} {: 0.3f} {: 0.3f} {: 0.3f} {: 0.3f} {: 0.3f} {: 0.3f} {: 0.3f} {: 0.3f}".format(
                    data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11], data[12], data[13], data[14], data[15])
                )
            else:
               print("ADC_ReadData status is bad:", status)    # possible timeout


# ADC GetScanV sample (USB-AI16-2A)
    if False:
        print("ADC_GetScanV() sample for USB-AI16-2A")
        config = [0, 0]
        status = ADC_SetConfig(diOnly, config)
        print("ADC_SetConfig status was ", status)
    
        for i in range(100):
            status, data = ADC_GetScanV(diOnly)
            print ("First channel data was ", data[0], "Volts.  Second channel data was", data[1] )


# ADC Continuous sample (USB-AIx Family)
    if True:
        print("ADC_BulkContinuousCallbackStart() sample for USB-AIx Family")
        config = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 5, 0xF0, 0, 0x00]
        status = ADC_SetConfig(diOnly, config)
        print("ADC_SetConfig status was ", status)

        status, Hz = CTR_StartOutputFreq(diOnly, 0, 100001.01)
        print("Acquiring at", Hz, "(requested 100001.01 Hz)")

        status = ADC_BulkContinuousCallbackStart(diOnly, myADCCallback, 231)
        print ("ADC_BulkContinuousCallbackStart() status was", status)
        
        print("callCallback returned:", callCallback(diOnly))
        
        status, IOStatus = ADC_BulkContinuousEnd(diOnly)
        print ("ADC_BulkContinuousEnd() status was", status, "IOStatus was",IOStatus)
        
        sleep(1)

# ADC Continuous sample (USB-AI16-2A)
    if False:
        print("ADC_BulkContinuousCallbackStart() sample for USB-AI16-2A")
        config = [0, 0]
        status = ADC_SetConfig(diOnly, config)
        print("ADC_SetConfig status was ", status)
            
        status = AIOUSB_ClearFIFO(diOnly, 0)
        if status == 0:
            print("AIOUSB_ClearFIFO() was successful.")
        else:
            print("AIOUSB_ClearFIFO() status:", status)  

        status = ADC_BulkContinuousCallbackStart(diOnly, myADCCallback, 1) # this runs at 1MHz on this board
        print ("ADC_BulkContinuousCallbackStart() status was", status)
        print("callCallback returned:", callCallback(diOnly))
        sleep(10)
        print("callCallback returned:", callCallback(diOnly))

        status, IOStatus = ADC_BulkContinuousEnd(diOnly)
        print ("ADC_BulkContinuousEnd() status was", status, "IOStatus was",IOStatus)


    print("Done.")
    input("Press <ENTER> to Exit.")
