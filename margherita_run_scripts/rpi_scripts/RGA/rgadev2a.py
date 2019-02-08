import serial
import time
import struct

class RGA(object): # Instantiate one of these as an interface to the real RGA
	def __init__(self, portname='/dev/ttyUSB0', baudrateset=28800, mytimeout=1, responsetime=1,
			start_mz=1, end_mz=200, points_per_amu=25, scan_speed=1,
			t_pressure_sensitivity=2.72e-5,p_pressure_sensitivity=1.833e-4, filament_init=0.0,
			model='SRSRGA200VER0.24', serialno='15754'):
		# portname is the USB port you should have plugged into
		# baudrateset is the baudrate the RGA needs to use; don't change this param
		# responsetime is a standard pause for the RGA microcontroller to respond to queries
		# mytimeout is just the timeout delay for the serial port
		self.responsetime=responsetime
		self.port=serial.Serial(portname, baudrate=baudrateset, timeout=mytimeout)# open a channel on the serial port
		self.start_mz = start_mz # starting mass in analog scan
		self.end_mz = end_mz # finishing mass in analog scan
		self.points_per_amu = points_per_amu # points per amu of m/z in analog scan
		self.scan_speed = scan_speed # scan speed in analog scan
		self.t_pressure_sensitivity = t_pressure_sensitivity # convert ion current to total pressure, in A/torr
		self.p_pressure_sensitivity = p_pressure_sensitivity # convert ion current to partial pressure, eg for analog scan, in A/torr
		self.IDCheck(model+'SN'+serialno) # If this fails after the RGA has been idle for a while, just try again to connect
		# I think the RGA might simply delay response under those circumstances
		self.CheckFilament(filament_init) # if the control software exited properly, there should be no current from the filament
		self.WriteParams()
		self.CheckParams() # Check that the internal parameters are in agreement with ours

	def IDCheck(self,expected_id): 
		'Check that the RGA is connected and correctly identifying itself.'
		# SRSRGA200VER0.24 is the model number, 15754 is the serial number
		print 'Querying RGA ID'
		no_comm=True
		while no_comm:
			if self.port.inWaiting() == 25:
				self.lastmessage=self.port.read(25)
				print self.lastmessage
				assert self.lastmessage==expected_id + '\n\r'
				no_comm=False
			elif self.port.inWaiting() == 0:
				self.port.write('id?\r')
				time.sleep(1)
			else:
				self.lastmessage=self.port.read(self.port.inWaiting())
				print self.lastmessage
				print 'This is a nonstandard response.'
				no_comm=False

	def CheckFilament(self,expected_value):
		'Check the value of the filament current'
		self.port.read(self.port.inWaiting())
		self.port.write('fl?\r') # fl denotes a filament-related message. ? denotes a query. \r indicates a completed message
		time.sleep(self.responsetime) # wait for reply
		# the expected reply of the RGA is the string of a number with 4 digits after the decimal, plus '\n\r' boilerplate
		# '{:.4f}\n\r'.format(expected_value) takes a floating point number and returns the properly formatted RGA reply
		self.lastmessage = self.port.read(len('{:.4f}\n\r'.format(expected_value)))
		if self.lastmessage== '{:.4f}\n\r'.format(expected_value):
			print 'The ionizing filament current is %s' % self.lastmessage
		else: # The filament current is very repeatable. If it is not at exactly the value you expect,
			# you should find out about it right away.
			self.Extinguish() # turning off the filament puts RGA in safe condition
			print 'Something unexpected happened. Extinguishing the filament.'
			print ('When the filament current was queried the response was: ' + repr(self.lastmessage))

	def WriteParams(self):
		'Write the local parameters to RGA internal storage'
		self.port.write('mi%s\r' % self.start_mz) # these four are the only parameters that the RGA stores which affect the ion
		# currents which it sends back as data
		self.port.write('mf%s\r' % self.end_mz)
		self.port.write('sa%s\r' % self.points_per_amu)
		self.port.write('nf%s\r' % (self.scan_speed - 1))

	def CheckParams(self):
		'Check the RGA internal parameters for synchrony with the local copy'
		self.port.write('mi?\r') # ask for the RGA's copy of self.start_mz
		self.port.write('mf?\r') # ask for self.end_mz
		self.port.write('sa?\r') # ask for self.points_per_amu
		self.port.write('nf?\r') # ask for noise_floor. noise_floor==self.scan_speed - 1
		self.port.write('ap?\r') # ask for the number of points an analog scan will generate
		time.sleep(self.responsetime)

		self.lastmessage = self.port.read(2+len('%s' % self.start_mz)) # the 2+len() device for matching %s\n\r is idiosyncratic,
		# but the %s\n\r is the precise response, don't alter that.
		# the remaining lines of this method are exactly paralllel to this first self.lastmessage...assert block
		print repr(self.lastmessage)
		assert self.lastmessage == '%s\n\r' % self.start_mz
		self.lastmessage = self.port.read(2+len('%s' % self.end_mz))
		print repr(self.lastmessage)
		assert self.lastmessage == '%s\n\r' % self.end_mz
		self.lastmessage = self.port.read(4)
		print repr(self.lastmessage)
		assert self.lastmessage == '%s\n\r' % self.points_per_amu
		self.lastmessage = self.port.read(3)
		print repr(self.lastmessage)
		assert self.lastmessage == '%s\n\r' % (self.scan_speed - 1)
		self.lastmessage = self.port.read(len('%s\n\r' % ((self.end_mz - self.start_mz)*self.points_per_amu + 1)))
		print repr(self.lastmessage)
		assert self.lastmessage == '%s\n\r' % ((self.end_mz - self.start_mz)*self.points_per_amu + 1)

	def HandleErrors(self,errorbyte):
		errtype={1:{'query':'ec','lookup':{
			1:'Bad command received',
			2:'Bad parameter received',
			4:'Command too long',
			8:'Overwrite in receiving',
			16:'Transmit buffer overwrite',
			32:'Jumper protection violation',
			64:'Parameter conflict'}},
		2:{'query':'ef','lookup':{
			1:'Single filament operation',
			32:'Vacuum chamber pressure too high',
			64:'Unable to set the requested emission current',
			128:'No filament detected'}},
		8:{'query':'em','lookup':{
			128:'No electron multiplier option installed'}},
		16:{'query':'eq','lookup':{
			16:'Power supply in current limited mode',
			64:'Primary current exceeds 2.0A',
			128:'RF_CT exceeds (V_EXT-2V) at M_MAX'}},
		32:{'query':'ed','lookup':{
			2:'op-amp input offset voltage out of range',
			8:'COMPENSATE fails to read -5nA input current',
			16:'COMPENSATE fails to read +5nA input current',
			32:'DETECT fails to read -5 nA input current',
			64:'DETECT fails to read +5 nA input current',
			128:'ADC16 Test failure'}},
		64:{'query':'ep','lookup':{
			64:'External 24V P/S error: Voltage <22V',
			128:'External 24V P/S error: Voltage >26V'}}}
		if errorbyte==0: # no errors
			pass
		for bit in errtype.keys():
			if bit & errorbyte ==1:
				print(self.port.read(self.port.inWaiting()))
				self.port.write(errtype[bit]['query'] + '?\r')
				time.sleep(self.responsetime)
				self.newerror=self.port.read(1)
				tag = self.port.read(2)
				assert tag == '\n\r'
				for foo in errtype[bit]['lookup'].keys():
					if foo & self.newerror ==1:
						print errtype[bit]['lookup'][foo]

	def Ignite(self):
		'Turn on the filament.'
		self.CheckFilament(0.000) # checks that the filament was off beforehand
		self.port.write('fl*\r') # ignite filament at default value ==.9976 mA
		time.sleep(6.0) # ignition takes 5 seconds, wait for completion
		if self.port.inWaiting()==3:
			self.lastmessage=self.port.read(1) # after this time, the RGA will send its error byte
			tag=self.port.read(2)
			assert tag =='\n\r'
			self.HandleErrors(int(self.lastmessage))
		else:
			print('Something unexpected occurred. Perhaps the filament is taking too long to ignite.')
			print('The filament is being extinguished, just in case.')
			self.lastmessage=self.port.read(self.port.inWaiting())
			print('The unexpected message was: ',repr(self.lastmessage))
			self.Extinguish()
		self.CheckFilament(.9976) # checks that filament is on now

	def Extinguish(self):
		'Turn off the filament on purpose.'
		self.port.read(self.port.inWaiting())
		self.port.write('fl0.0\r') # command the RGA to set filament current to 0
		time.sleep(1)
		if self.port.inWaiting()==3:
			self.lastmessage=self.port.read(1)
			tag=self.port.read(2)
			assert tag =='\n\r'
			self.HandleErrors(int(self.lastmessage))
		elif self.port.inWaiting()==0:
			print('The filament was already extinguished.')
		else:
			self.lastmessage=self.port.read(self.port.inWaiting())
			print('Something unexpected occurred. Please troubleshoot.')
			print('The unexpected message was: '+repr(self.lastmessage))

	def AScanStart(self):# this function performs an analog scan
		self.WriteParams()
		self.CheckParams()
		self.ap = (self.end_mz - self.start_mz) * self.points_per_amu + 1 # this is the number of data points we expect
		self.masses=[self.start_mz + float(i)/self.points_per_amu for i in range(self.ap)]# this is the set of masses measured
		self.measurement=0
		self.port.write('sc1\r') #sc triggers a number of scans. sc specifies one scan
		self.start=time.time()
		self.file = open('./data/RGA/RGA-{}.txt'.format(time.strftime('%m%d%y%H%M%S')),'a')
                self.scan_complete=False

	def AScanWrite(self):
		if self.measurement < self.ap+1:
			points = self.port.inWaiting() / 4
			if self.measurement+points < self.ap+1:
				self.lastmessage=self.port.read(4*points)
				self.file.write('\n'.join([str(self.masses[i+self.measurement])+','+str(((struct.unpack(
				'<I',self.lastmessage[4*i:4*i+4])[0]+1) % 2**32)*1e-16/self.p_pressure_sensitivity
				) for i in range(points)])+'\n')
				self.measurement += points
			elif self.measurement+points == self.ap+1:
				elapsed=time.time()-self.start
				self.lastmessage=self.port.read(4*points-4)
				self.file.write('\n'.join([str(self.masses[i+self.measurement])+','+str(((struct.unpack(
				'<I',self.lastmessage[4*i:4*i+4])[0]+1) % 2**32)*1e-16/self.p_pressure_sensitivity
				) for i in range(points)])+'\n')
				self.lastmessage = self.port.read(4)
				print('Measurement complete.')
				print('Total time to complete the measurement was: %s seconds.' % elapsed)
				self.file.close()
				self.lastmessage = self.port.read()	
				assert self.lastmessage == '' # should be nothing left to read
                                self.scan_complete=True
			else:
				print('Something unexpected occurred. There may be extra things in the buffer.')
		else:
			print('Something unexpected occurred. There are too many measurements in this scan.')
