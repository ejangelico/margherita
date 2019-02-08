import serial
import time
import struct

class RGA(object): # Instantiate one of these as an interface to the real RGA
	def __init__(self, portname='/dev/ttyUSB0', baudrateset=28800, mytimeout=3, responsetime=0.5, start_mz=1, end_mz=200, points_per_amu=25,
		 scan_speed=1, t_pressure_sensitivity=2.72e-5,p_pressure_sensitivity=1.833e-4):
		# portname is the USB port you should have plugged into
		#baudrateset is the baudrate the RGA needs to use; don't change this param
		#responsetime is how long I want to wait for responses on stuff the RGA should be able to do right away, without taking
		#any measurements
		self.responsetime=responsetime
		self.portname=portname
		self.baudrate=baudrateset
		self.port=serial.Serial(self.portname,baudrate=self.baudrate, timeout=mytimeout)# open a channel on the serial port
		self.start_mz = start_mz # starting mass in analog scan
		self.end_mz = end_mz # finishing mass in analog scan
		self.points_per_amu = points_per_amu # points per amu of m/z in analog scan
		self.scan_speed = scan_speed # scan speed in analog scan
		self.t_pressure_sensitivity = t_pressure_sensitivity # convert ion current to total pressure, in A/torr
		self.p_pressure_sensitivity = p_pressure_sensitivity # convert ion current to partial pressure, eg for analog scan, in A/torr
		self.IDCheck() # If this fails after the RGA has been idle for a while, just try again to connect
		# I think the RGA might simply delay response under those circumstances
		self.CheckFilament(0.0000) # if the control software exited properly, there should be no current from the filament
		self.WriteParams() # The RGA has internal storage for its scan parameters: here we write our parameters there
		self.CheckParams() # Check that the internal parameters are in agreement with ours

	def IDCheck(self,expected_id='SRSRGA200VER0.24SN15754'): 
		'Check that the RGA is connected and correctly identifying itself.'
		# SRSRGA200VER0 is the model number, 24SN15754 is the serial number
		print 'Querying RGA ID'
		self.port.write('id?\r')# command RGA to identify itself
		time.sleep(self.responsetime)#this is a hack so that we read the response to the command we sent, not the previous command
		self.lastmessage=self.port.read(25) # length of the ID plus \n\r is 25
		# self.lastmessage is a device for fetching the RGA output. The point is to grab it ahead of time
		# so that you can worry about what to do with the output separately.
		# It's not the most elegant solution. Perhaps a better solution can be found?
		print self.lastmessage
		assert self.lastmessage==expected_id + '\n\r' # \n\r follows all completed messages from the RGA 
	def CheckFilament(self,expected_value):
		'Check the value of the filament current'
		self.port.write('fl?\r') # fl denotes a filament-related message. ? denotes a query. \r indicates a completed message
		time.sleep(self.responsetime) # wait for reply
		# the expected reply of the RGA is the string of a number with 4 digits after the decimal, plus '\n\r' boilerplate
		# '{:.4f}\n\r'.format(expected_value) takes a floating point number and returns the properly formatted RGA reply
		self.lastmessage = self.port.read(len('{:.4f}\n\r'.format(expected_value)))
		print repr(self.lastmessage)
		if self.lastmessage== '{:.4f}\n\r'.format(expected_value):
			print 'The ionizing filament current is %s' % self.lastmessage
		else: # The filament current is very repeatable. If it is not at exactly the value you expect,
			# you should find out about it right away.
			self.Extinguish() # turning off the filament puts RGA in safe condition
			raise Exception('The filament should have been %s but replied instead: %r' % (expected_value, self.lastmessage))
			# Exception stops execution and informs you of the problem

	def Ignite(self):
		'Turn on the filament.'
		self.CheckFilament(0.000) # checks that the filament was off beforehand
		self.port.write('fl*\r') # ignite filament at default value ==.9976 mA
		time.sleep(6.0) # ignition takes 5 seconds, wait for completion
		self.lastmessage=self.port.read(3) # after this time, the RGA will send its error byte, plus \n\r
		# assert self.lastmessage == '0\n\r' 
		# Eric S 2016-01-30 commented this out for expedience
		print self.lastmessage
		# find the appropriate queries/interpretation in chapter 6 of the SRS RGA manual
		self.CheckFilament(.9976) # checks that filament is on now

	def Extinguish(self):
		'Turn off the filament on purpose.'
		self.port.write('fl0.0\r') # command the RGA to set filament current to 0
		time.sleep(1)
		self.lastmessage=self.port.read(3)
		# assert self.lastmessage == '0\n\r' # make sure error byte is OK
		# Eric S 2016-01-30 commented this out for expedience
		print self.lastmessage
		self.CheckFilament(0.000) # check that it really turned off.

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

	def WriteParams(self):
		'Write the local parameters to RGA internal storage'
		self.port.write('mi%s\r' % self.start_mz) # these four are the only parameters that the RGA stores which affect the ion
		# currents which it sends back as data
		self.port.write('mf%s\r' % self.end_mz)
		self.port.write('sa%s\r' % self.points_per_amu)
		self.port.write('nf%s\r' % (self.scan_speed - 1))

	def analogscan(self):# this function performs an analog scan
		self.WriteParams()
		self.CheckParams()
		ap = (self.end_mz - self.start_mz) * self.points_per_amu + 1 # this is the number of data points we expect
		masses=[self.start_mz + float(i)/self.points_per_amu for i in range(ap)]# this is the set of masses measured
		print repr(ap)
		self.port.write('sc1\r') #sc triggers a number of scans. sc specifies one scan
		time.sleep(20 + 4.0*(self.end_mz-self.start_mz)*float(2)**(-float(self.scan_speed))) # This is an upper bound on how long the RGA
		# requires to complete its analog scan. You might be able to tighten this
		file = open('./data/RGA/RGA-{}.txt'.format(time.strftime('%m%d%y%H%M%S')),'a')# open a text file for each scan
		
		self.lastmessage=self.port.read(ap*4)# I had some trouble when I tried to validate input in order to grab one data point
		# at a time. If you write code to grab the data as they become available, be sure you validate input because you can
		# grab fragments of the 4-byte integers, or stop collecting before you have all the points if you're not careful 
		for i in range(ap):
			file.write(str(masses[i]) + ',' +
				str(struct.unpack('<I',self.lastmessage[4*i:4*i+4])[0]*1e-16 / self.p_pressure_sensitivity) +
				'\n') # write the ith mass and the ith partial pressure
		self.lastmessage = self.port.read(4) # this one is supposed to be a total pressure measurement
		print repr(self.lastmessage)
		file.write(str(struct.unpack('<I',self.lastmessage)[0] * 1e-16 / self.t_pressure_sensitivity)) # append the total pressure to the end
		file.close()
		self.lastmessage = self.port.read()	
		assert self.lastmessage == '' # should be nothing left to read
		print 'Measurement complete.'
