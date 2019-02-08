''' This code measures and logs temperature from 5 thermocouples, pressure 
from a Pfeiffer PK-251 gauge. The output files will be located in the
logs folder. The logging program can be stopped with a keyboard interrupt, but
will catch other errors and print them to console.

'''
import u6
import time
import typeKthermocouple
import typeEthermocouple
import os
import pfeiffer
from thermocoupleCalibrations import rt_offsets


#these channels are for measuring cold junction
#temperature from each CB37. 
#List structure: calChannel[Xi][differential?]
#for Xi = X2 X3 X4 X5 and differential? True or False
calChannels = [[127, False], [55, False], [87, True], [96, True]]


#channels for measurement
#muxChans[channel][channel#, differential?, Xi]

#muxChans = [[80,1,2],[82,1,2],[83,1,2],[84,1,2],[85,1,2],[86,1,2],[97,1,2],[98,1,2], 
#            [51,0,1],[126,0,0],[50,0,1],[48,0,1],[122,0,0],[123,0,0],
#            [121,0,0],[3,0,0],[2,0,0],[1,0,0],[124,0,0],
#            [125,0,0],[52,0,1],[53,0,1],[54,0,1],[56,0,1],[57,0,1],[58,0,1],
#            [59,0,1],[60,0,1],[61,0,1],[62,0,1],[63,0,1],[64,0,1]]
muxChans = [[96,1,3],[97,1,3],[98,1,3],[99,1,3],[100,1,3],[101,1,3],[102,1,3],[103,1,3],
            [51,0,1],[126,0,0],[50,0,1],[48,0,1],[122,0,0],[123,0,0],
            [121,0,0],[3,0,0],[2,0,0],[1,0,0],[124,0,0],
            [125,0,0],[52,0,1],[53,0,1],[54,0,1],[56,0,1],[57,0,1],[58,0,1],
            [59,0,1],[60,0,1],[61,0,1],[62,0,1],[63,0,1],[64,0,1]]


# Declare a labjack U6 object from the u6 module
labJack = u6.U6()


gaugebox=pfeiffer.TPG262(port='/dev/ttyUSB1')
time.sleep(1)
gaugebox.serial.flushInput()
test=gaugebox.rs232_communication_test()
print test


# This code will run indefinitely, it can be quit with a keyboard interrupt (Ctrl C)
while True:
	if(int(time.strftime('%S')) % 3 == 0):
		try:
			tempFile = open('./data/thermocouple_data/tcLog%s.txt' % time.strftime('%y%m%d'), 'a')
			pressureFile = open('./data/pressure_data/pressureLog%s.txt' % time.strftime('%y%m%d'), 'a')
			
                        # The cold junction temperature in celsius, compensating for the screw junction temperature
			# We measure the cold junction on each CB37 separately to correct the offset
			coldJunctionTemp = labJack.getTemperature() - 273.15
                        coldJunctionVolts = typeKthermocouple.tempToVolts(coldJunctionTemp)
                        print "Cold Junction: " + str(coldJunctionTemp)
                        print "Cold Junction volts: " + str(coldJunctionVolts)
                        calOffsets = []
                        for calchan in calChannels:
                            print "trying channel " + str(calchan[0])
                            if calchan[1]:
                                v=0
                            else:
                                v = labJack.getAIN(calchan[0], resolutionIndex = 9, gainIndex = 2, differential=calchan[1])*1000
                            t = typeKthermocouple.voltsToTemp(v)
                            print "Temp measured from channel " + str(calchan) + " = " + str(t)
                            calOffsets.append(v - coldJunctionVolts)


                        temps = []
                        for tc in muxChans:
                            channel = tc[0]
                            isDifferential = tc[1]
                            Xi = tc[2]
                            #temporarily ignore the following channels:
                            if(channel==63):
                                temps.append(str(22))
                                continue
                            
                            print "Trying channel " + str(channel)
                            v = (labJack.getAIN(channel, resolutionIndex = 9, gainIndex = 2, differential=isDifferential))*1000
                            print v
                            #print "calibration offset is " + str(rt_offsets[str(channel)])
                            T = typeKthermocouple.voltsToTemp(v - calOffsets[Xi])#+rt_offsets[str(channel)]
                            print "Channel " + str(channel) + " measured " + str(T) + " C"
                            temps.append('{0:.2f}'.format(T))
                        
			entry = (','.join(temps) + ',' + str(time.strftime("%m-%d-%y %H:%M:%S")) + '\n')
			
			tempFile.write(entry)
                       
                     
			gauge_output = gaugebox.pressure_gauges()
                        pressures=[]
                        for i in range(0,4,2):
                            #standard
                            if gauge_output[i+1][0] in {0,1}:
                                pressures.append(str(gauge_output[i]))
                                print gauge_output[i]
                            #overrange
                            elif gauge_output[i+1][0] == 2:
                                pressures.append(str(760))
                                print gauge_output[i]
                            #no sensor
                            elif gauge_output[i+1][0] == 5:
                                print "no sensor"
                            #the gauge is off? And anything else
                            else:
                                pressures.append(str(760))
                                print "gauge error or gauge is off"
                                pass
			entry = (','.join(pressures) + ',' + str(time.strftime("%m-%d-%y %H:%M:%S")) + '\n')
			pressureFile.write(entry)
			
                        tempFile.close()
                        pressureFile.close()
                        time.sleep(1)
		except Exception as e:
			# This will catch all exceptions and simply print them to console, allowing 
			# the program to indefinitely 
			#print e
			#pass
                        raise
		finally:
                    pass
