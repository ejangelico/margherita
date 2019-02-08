import serial, time, wiringpi, sys

ttlOutputChannel=2
numSwitches=400 # The number of times the LED switches on and off
# Note that the total number of measurements is only half of this because
# the first half of each set of measurements is thrown out for the sake
# of reducing the rms variance
period=0.1

board_type = sys.argv[-1]
if board_type == "m":
    poss_channels = 7
else:
    poss_channels = 6

def reset_ports():
    wiringpi.digitalWrite(4, 0)         # switches off LED
    wiringpi.pinMode(4,0)               # set LED back to input mode

def readWithDelay(delay,instrument):
    instrument.write('read?\r')
    now = time.time()
    while (instrument.inWaiting() < 14) or (time.time()-now < delay):
        time.sleep(1e-3)
    return instrument.read(instrument.inWaiting())

wiringpi.wiringPiSetupGpio()                        # Initialise GPIO
wiringpi.pinMode(4, 1)                              # set up LED for output

a=serial.Serial('/dev/ttyUSB0',baudrate=57600,bytesize=8,parity='N',timeout=None,xonxoff=False,stopbits=1)
time.sleep(0.1)
a.flushInput()

a.write('\r*cls\r*idn?\r')
time.sleep(1.5)
print a.read(a.inWaiting())
a.write('*rst\r')
a.write('form:elem read\r')
if period>0.166:
    a.write('curr:nplc 10\r')
elif period<1.67e-4:
    a.write('curr:nplc 0.01\r')
else:
    a.write('curr:nplc {0:.2f}\r'.format(period*60.0))
print('{0:.2f}'.format(period*60.0))
a.write('syst:zch on\r')
time.sleep(0.2)
a.write('curr:rang 2e-9\r')
time.sleep(0.2)
a.write('init\r')
time.sleep(0.2)
a.write('syst:zcor:acq\r')
a.write('syst:zcor on\r')
a.write('curr:rang:auto on\r')
a.write('syst:zch off\r')
time.sleep(0.2)
#a.write('curr:rang:auto off\r')
#a.write('curr:rang 2e-5\r')
time.sleep(0.2)

try:
    loglist=[]
    now0=time.time()
    for _ in range(numSwitches):
        now=time.time()
        wiringpi.digitalWrite(4,1)
        time.sleep(1e-3)
        reading=readWithDelay(period,a)
        print(reading[0:-1])
        loglist.append(float(reading[0:-1]))
        wiringpi.digitalWrite(4,0)
        time.sleep(1e-3)
        reading=readWithDelay(period,a)
        print(reading[0:-1])
        loglist.append(float(reading[0:-1]))
    print('total time per measurement is: ' + str((time.time()-now0)/period/numSwitches/2) +
'integration times')
    on_curr_list=[loglist[2*i+1] for i in range(numSwitches/2,numSwitches)]
    off_curr_list=[loglist[2*i] for i in range(numSwitches/2,numSwitches)]
    on_curr=sum(on_curr_list)/len(on_curr_list)
    off_curr=sum(off_curr_list)/len(off_curr_list)
    diff_curr_list=[on_curr_list[i]-off_curr_list[i] for i in range(len(on_curr_list))]
    diff_curr=sum(diff_curr_list)/len(diff_curr_list)
    var_diff=(sum((diff_curr_list[i]-diff_curr)**2 for i in range(len(diff_curr_list)))/len(diff_curr_list))**0.5
    var_on_curr = (sum((loglist[2*i+1]-on_curr)**2 for i in range(numSwitches/2,numSwitches))*2/numSwitches)**0.5
    var_off_curr = (sum((loglist[2*i]-off_curr)**2 for i in range(numSwitches/2,numSwitches))*2/numSwitches)**0.5
    print('On current: ' + str(on_curr))
    print('Off current: ' + str(off_curr))
    print('Difference current: ' + str(diff_curr))
    print('Difference current variance: ' + str(var_diff))
    print('On current variance: ' + str(var_on_curr))
    print('Off current variance: ' + str(var_off_curr))

except KeyboardInterrupt:                   # trap a CTRL+C keyboard interrupt
    reset_ports()                           # reset ports

reset_ports()       # reset ports on normal exit
