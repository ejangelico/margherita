import numpy as np
import matplotlib.pyplot as plt 
import time
#from matplotlib.dates import DateFormatter
from datetime import datetime
import subprocess
import glob
import os.path




print "pulling from servers"

subprocess.call(["/local/data2/margherita/data/rga_data/pull_data.sh"])
filelist=filter(os.path.isfile,glob.glob('/local/data2/margherita/data/rga_data/text_files/RGA-*.txt'))
filelist.sort(key=lambda x: os.path.getctime(x))
filelist.reverse()

scan0 = np.genfromtxt(filelist[0], delimiter=',',dtype=None, invalid_raise = False)
scan1 = np.genfromtxt(filelist[1], delimiter=',',dtype=None, invalid_raise = False)

plt.figure(1)
plt.subplot(211)
plt.semilogy(scan0[:,0],scan0[:,1])
plt.grid(True,'both')
plt.minorticks_on()
plt.ylim((1e-10,2e-6))

plt.subplot(212)
plt.semilogy(scan1[:,0],scan1[:,1])
plt.grid(True,'both')
plt.minorticks_on()
plt.ylim((1e-10,2e-6))


plt.show()
