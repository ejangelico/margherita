import rgadev4 as rga
import time
import os
import subprocess

run_anyway=True
interlock=open('interlock_for_rga.txt','w')
interlock.write('To stop continuous scanning processes by the RGA, delete this file.')
interlock.close()

pplist=[14,18,28,32,40]
pplist.sort()
for m in pplist:
    try:
        os.mkdir('../data/rga_notscan/{}'.format(m))
    except OSError:
        pass

# the following sequence verifies communication with the rga
# completion marker set to false to indicate noncompletion
handshake=False
# try to intialize communications with RGA until successful
while not(handshake):
    try:
        # this initializes an RGA object AND verifies communication
        srsrga=rga.RGA(serialno='15754')
        # set completion marker to true
        handshake=True
    except:
        print "The RGA failed to respond when queried for its model and serial numbers."
        time.sleep(1)

# The filament is assumed to be off. Check that this is true.
srsrga.CheckFilament(0.0)
filament_lit=False

scanflag=False
scan_range=[1,200]
scan_speed=1
try:
    while os.path.isfile('./interlock_for_rga.txt'):
        if not(filament_lit):
            pressure_file='../data/pressure_data/pressureLog{0}.txt'.format(time.strftime('%y%m%d'))
            t = subprocess.Popen(['tail','-1',pressure_file],\
                    stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            line = t.stdout.readline()
            stuff=line.split(',')
            p = float(stuff[0])
            print 'The filament is dark and the current pressure is {} Torr.'.format(p)
            if p < 3e-6 or run_anyway:
                print 'Igniting the filament to take measurements.'
                srsrga.Ignite()
                filament_lit=True
            else:
				time.sleep(10)
                
        else:
            tp=srsrga.totalPressureRead()
            tpFile=open('../data/rga_notscan/total_pressure/log{}.txt'.format(time.strftime('%y%m%d')),'a')
            tpFile.write('{0},{1}\n'.format(str(tp),time.strftime('%m-%d-%y %H:%M:%S')))
            tpFile.close()
            
            if tp < 3e-6 or run_anyway:
                for m in pplist:
                    pp=srsrga.singleMassRead(m)
                    print pp
                    ppFile=open('../data/rga_notscan/{0}/log{1}.txt'.format(m,time.strftime('%y%m%d')),'a')
                    ppFile.write('{0},{1}\n'.format(str(pp),time.strftime('%m-%d-%y %H:%M:%S')))
                    ppFile.close()
            else:
                srsrga.Extinguish()
                print 'The total pressure exceeded 3.00e-6 Torr and the filament was extinguished.'
                filament_lit=False
    srsrga.Extinguish()
except:
    srsrga.Extinguish()
    raise
