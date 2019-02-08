import rgadev4 as rga
import time
import os
import subprocess

pplist=[18,133]
for m in pplist:
    try:
        os.mkdir('/home/pi/MargheritaCode/data/rga_notscan/{}'.format(m))
    except OSError:
        pass

# the following sequence verifies communication with the rga
# completion marker set to false to indicate noncompletion
handshake=False
# try to intialize communications with RGA until successful
while not(handshake):
    try:
        # this initializes an RGA object AND verifies communication
        #srsrga=rga.RGA(serialno='17708') #id number for manifold 
        srsrga=rga.RGA(serialno='15754') #id number for margherita
        # set completion marker to true
        handshake=True
    except:
        raise 
	print "The RGA failed to respond when queried for its model and serial numbers."
        time.sleep(1)

# The filament is assumed to be off. Check that this is true.
srsrga.CheckFilament(0.0)
filament_lit=False

scan_range=[1,200]
scan_speed=1
try:
    if not(filament_lit):
        pressure_file='/home/pi/MargheritaCode/data/pressure_data/pressureLog{0}.txt'.format(time.strftime('%y%m%d'))
        t = subprocess.Popen(['tail','-1',pressure_file],\
                stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        line = t.stdout.readline()
        stuff=line.split(',')
        p = float(stuff[0])
        print 'The filament is dark and the current pressure is {} Torr.'.format(p)
        if p < 3e-6:
            print 'Igniting the filament to take measurements.'
            srsrga.Ignite()
            filament_lit=True
        else:
            time.sleep(10)
            
    else:
        pass
    if filament_lit:
        print "Filament lit. Waiting for pressure to stabilize."
        time.sleep(30)
        tp=srsrga.totalPressureRead()
        tpFile=open('/home/pi/MargheritaCode/data/rga_notscan/total_pressure/log{}.txt'.format(time.strftime('%y%m%d')),'a')
        tpFile.write('{0},{1}\n'.format(str(tp),time.strftime('%m-%d-%y %H:%M:%S')))
        tpFile.close()
        
        if tp < 3e-6:
            srsrga.start_mz=scan_range[0]
            srsrga.end_mz=scan_range[1]
            srsrga.scan_speed=scan_speed
            srsrga.AScanStart()
            scanfinished=False
            print 'Initiated an analog scan from {0} amu to {1} amu.'.format(*scan_range)
            scanStart=time.time()
            lastUpdate=scanStart
            while not(scanfinished):
                srsrga.AScanWrite()
                if srsrga.scan_complete:
                    scanfinished=True
                    print 'The analog scan is complete.'
                elif time.time()-lastUpdate > 20.0:
                    lastUpdate=time.time()
                    completionPercent=(lastUpdate-scanStart)/4.0
                    print 'The scan is {0:.1f}% complete.'.format(completionPercent)
                time.sleep(0.5)
            srsrga.Extinguish()
        else:
            srsrga.Extinguish()
            print 'The total pressure exceeded 3.00e-6 Torr and the filament was extinguished.'
            filament_lit=False
except:
    srsrga.Extinguish()
    raise
