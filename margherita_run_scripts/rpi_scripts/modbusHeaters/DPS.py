import minimalmodbus

class DPS:
    def __init__(self,port="/dev/ttyUSB1"):
	#immediately initialize a modbus instrument
	self.port = port
	self.inst = None
	self.initialize()



    def initialize(self):
	self.inst = minimalmodbus.Instrument(self.port, 1) #slave address 1
	self.inst.serial.baudrate = 9600
	self.inst.serial.bytesize = 8
	self.inst.serial.timeout = 2
	self.inst.mode = minimalmodbus.MODE_RTU
	return


    
    def print_all_info(self):

	b = self.inst.read_registers(0, 13)

	rv = {'U-Set': b[0] / 100.0,
	      'I-Set': b[1] / 1000.0,
	      'U-Out': b[2] / 100.0,
	      'I-Out': b[3] / 1000.0,
	      'P-Out': b[4] / 100.0,
	      'U-In': b[5] / 100.0,
	      'Locked': {0: 'OFF', 1: 'ON'}.get(b[6]),
	      'Protected': {0: 'ON', 1: 'OFF'}.get(b[7]),
	      'CV/CC': {0: 'CV', 1: 'CC'}.get(b[8]),
	      'ON_OFF': {0: 'OFF', 1: 'ON'}.get(b[9]),
	      'Backlight': b[10],
	      'Model': str(b[11]),
	      'Firmware': str(b[12] / 10.0),
	      }
	print rv
	return rv


    #returns the output voltage, current, and power
    #will be 0 if the unit is set to the off position
    def read_vcp_applied(self):
	v, c = self.inst.read_registers(2, 2)
	p = self.inst.read_register(4)
	v = v*0.01 #now in volts
	c = c*0.001 # now in amps
	p = p*.01 #now in Watts
	return v, c, p

    #returns the setpoint voltage and current
    def read_setvc(self):
	v, c = self.inst.read_registers(0,2)
	v = v*0.01 #now in volts
	c = c*0.001 # now in amps
	return v, c

    #turns applied power on
    def turn_on(self):
	self.inst.write_register(9, 1)

    #turns off applied power
    def turn_off(self):
	self.inst.write_register(9, 0)

    #sets the set voltage of the power supply
    #with v given in volts. Rounds such that you
    #can at most give 10mv decimals
    def set_v(self, v):
	doctored_v = int(v*100)
	self.inst.write_register(0, doctored_v)


    #sets the current limit with at most
    #ma precision. i given in amps
    def set_i(self, i):
	doctored_i = int(i*1000)
	self.inst.write_register(1, doctored_i)

    #set both v and i bounds with unit
    #conventions from above
    def set_iv(self, i, v):
	doctored_i = int(i*1000)
	doctored_v = int(v*100)
	self.inst.write_register(0, doctored_v)
	self.inst.write_register(1, doctored_i)
