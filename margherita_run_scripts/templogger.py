#!/opt/rh/python27/root/usr/bin/python

import sys
import subprocess
import time
import os

zones = [1,2,3,4,5,6]

filecount = 0
#while os.path.exists('controlrun%s.txt' % filecount):
#	filecount+=1

while True:
	if(int(time.strftime('%S')) % 2 == 0):
		outfile = open('controlrun%s.txt' % filecount, 'a')
		for chNum in zones:
			process = subprocess.Popen(['./rtm.py', str(chNum)], stdout=subprocess.PIPE)
			out, err = process.communicate()
			outfile.write(str(out.split('\n')[0]))
			outfile.write(',')
		outfile.write(str(time.strftime("%m-%d-%y %H:%M:%S")))
		outfile.write('\n')
		outfile.close()
		time.sleep(1)

			
