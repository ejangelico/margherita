import rgadev4 as rga
import time
import os
import subprocess




# the following sequence verifies communication with the rga
# completion marker set to false to indicate noncompletion
handshake=False
# try to intialize communications with RGA until successful
while not(handshake):
    try:
        # this initializes an RGA object AND verifies communication
        #srsrga=rga.RGA(serialno='17708') #id number for m1
        srsrga=rga.RGA(serialno='15754') #id number for m2
        # set completion marker to true
        handshake=True
    except:
        raise 
	print "The RGA failed to respond when queried for its model and serial numbers."
        time.sleep(1)
            
			
srsrga.Degas()
print "Done"
