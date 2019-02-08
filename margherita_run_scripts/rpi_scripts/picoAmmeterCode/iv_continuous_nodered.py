import serial, time, sys
import mysql.connector
from datetime import datetime

period = 0.1



def readWithDelay(delay,instrument):
    instrument.write('read?\r')
    now = time.time()
    while (instrument.inWaiting() < 14) or (time.time()-now < delay):
        time.sleep(1e-3)
    return instrument.read(instrument.inWaiting())



# connect to mysql
cnx = mysql.connector.connect(user='nodered',password ='LAPPD933e56th', host = '128.135.102.82', database='test')
cursor = cnx.cursor()

# open serial port
a=serial.Serial('/dev/kieth',baudrate=57600,bytesize=8,parity='N',timeout=None,xonxoff=False,stopbits=1)
time.sleep(0.1)
a.flushInput()

# clear some or other buffer and request instrument id
a.write('\r*cls\r*idn?\r')
time.sleep(1.5)
assert a.inWaiting()>0
print a.read(a.inWaiting())
a.write('*rst\r')
# set readout format
a.write('form:elem read\r')
# set integration time for readings
if period>0.166:
    a.write('curr:nplc 10\r')
elif period<1.67e-4:
    a.write('curr:nplc 0.01\r')
else:
    a.write('curr:nplc {0:.2f}\r'.format(period*60.0))
print('{0:.2f}'.format(period*60.0))
# zero check (read the manual)
a.write('syst:zch on\r')
time.sleep(0.2)
# set range
a.write('curr:range 2e-8\r')
time.sleep(0.2)
a.write('init\r')
time.sleep(0.2)


#set frequency
a.write('sys:lfr\r')
time.sleep(0.2)

# more picoammeter initialization, read the manual
a.write('syst:zcor on\r')
a.write('syst:zch off\r')
time.sleep(0.2)

try:
    while True:
        datafile=open('./data/ivLog{0}.txt'.format(time.strftime('%y%m%d')),'a')
        time.sleep(1e-3)
        reading=readWithDelay(period,a)
        cur = reading[0:-1]
        cur = str(abs(float(cur)*(10**6)))
        
        #cur is now a current and you want to send
        #that current to your mysql database
        
        entry='{0},{1}\n'.format(cur,datetime.now().strftime('%Y,%m,%d,%H,%M,%S,%Y%m%d%H%M%S'))

        add_data = ("INSERT INTO picoAmmeter(eCurrent,year,month,day,hour,minute,second,numTimeStamp) VALUES (%s)" % entry)
        cursor.execute(add_data)
        cnx.commit()
        

        datafile.write(entry)
        datafile.close()
        time.sleep(0.5)
        
except KeyboardInterrupt:                   # trap a CTRL+C keyboard interrupt
    pass

