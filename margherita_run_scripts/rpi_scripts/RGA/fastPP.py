import rgadev4 as rga
import time
import os
import subprocess

interlock=open('interlock_for_rga.txt','w')
interlock.write('To stop continuous scanning processes by the RGA, delete this file.')
interlock.close()

pplist=[2,28,40]
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

try:
    while os.path.isfile('./interlock_for_rga.txt'):
        if not(filament_lit):
			print 'Igniting the filament to take measurements.'
			srsrga.Ignite()
			filament_lit=True
                
        else:
			for m in pplist:
				pp=srsrga.singleMassRead(m)
				print pp
				ppFile=open('../data/rga_notscan/{0}/log{1}.txt'.format(m,time.strftime('%y%m%d')),'a')
				ppFile.write('{0},{1}\n'.format(str(pp),time.strftime('%m-%d-%y %H:%M:%S')))
				ppFile.close()
    srsrga.Extinguish()
except:
    srsrga.Extinguish()
    raise
