#!/usr/bin/python
import time
import os



def updatePoints(modtime):
	print "File was modified at " + str(time.ctime(modtime))
	return 




setfile = "setpoints.txt"
	

(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(setfile)
lastmod =  mtime

while True:
	print "Checking for modification"
	(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(setfile)
	if (lastmod != mtime):
		updatePoints(mtime)
		lastmod = mtime

	time.sleep(1)

	
	
