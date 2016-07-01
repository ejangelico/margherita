import numpy as np
import matplotlib.pyplot as plt 
import time
#from matplotlib.dates import DateFormatter
from datetime import datetime
import subprocess
import glob
import os.path
import re




print "pulling from servers"

subprocess.call(["/local/data2/margherita/data/rga_data/pull_data.sh"])

#list of files which do not already have a plot
filelist=filter(lambda x: (os.path.isfile(x))&(not(os.path.exists('/local/data2/margherita/data/rga_data/plots/'+x[-16:-4]+'.png'))),glob.glob('/local/data2/margherita/data/rga_data/text_files/RGA-*.txt'))

for scanfile in filelist:

	#if you just pulled together a half finished rga scan
	if(len(filelist) < 2): break

	#this is the half pullsed rga scan
	if(scanfile == filelist[-1]): break	

	scan=np.genfromtxt(scanfile,delimiter=',',dtype=None, invalid_raise=False)
	plt.figure(figsize=(19,20))
	plt.semilogy(scan[:,0], scan[:,1])
	plt.grid(True,'both')
	plt.minorticks_on()
	plt.xlabel('M/Q (amu/e)')
	plt.ylabel('P (mbar)')
	plt.ylim((2e-11,2e-6))
	thedate=re.findall('\d\d',scanfile)
	plt.title('RGA scan from {3}:{4}:{5} {0}/{1}/{2}'.format(*thedate))
	plotname='/local/data2/margherita/data/rga_data/plots/'+scanfile[-16:-4]+'.png'
	plt.savefig(plotname)

	if(scanfile == filelist[-2]):
		#push the most recent plot to the web
		subprocess.call(["cp", plotname, "/psec/web/psec/margdata/rgaplot.png"])
