import numpy as np
import matplotlib.pyplot as plt 
import time
#from matplotlib.dates import DateFormatter
from datetime import datetime
import subprocess
import glob
import os.path
import re

#list of files which do not already have a plot
#filelist=filter(lambda x: (os.path.isfile(x))&(not(os.path.exists('/local/data2/margherita/data/rga_data/plots/'+x[-16:-4]+'.png'))),glob.glob('/local/data2/margherita/data/rga_data/text_files/RGA-*.txt'))
filelist=['/local/data2/margherita/data/rga_data/text_files/RGA-070516093243.txt']
scanfile=filelist[0]

#if you just pulled together a half finished rga scan

#this is the half pullsed rga scan
print scanfile
scan=np.genfromtxt(scanfile,delimiter=',',dtype=None, invalid_raise=False)
plt.figure(figsize=(19,20))
plt.semilogy(scan[:,0], scan[:,1])
plt.grid(True,'both')
plt.minorticks_on()
plt.xlabel('M/Q (amu/e)')
plt.ylabel('P (mbar)')
plt.ylim((2e-11,2e-5))
thedate=re.findall('\d\d',scanfile)
plt.title('RGA scan from {3}:{4}:{5} {0}/{1}/{2}'.format(*thedate))
plotname='/local/data2/margherita/data/rga_data/plots/'+scanfile[-16:-4]+'.png'
plt.text(2,3e-7,'$H_{2}^{+}$',fontsize=14)
plt.text(10,1.5e-8,'$O^{+}$',fontsize=14)
plt.text(10,6e-8,'$HO^{+}$',fontsize=14)
plt.text(14,9e-8,'$H_{2}O^{+}$',fontsize=14)
plt.text(28,2e-7,'$CO^{+}$',fontsize=14)
plt.text(44,1.2e-8,'$CO_{2}^{+}$',fontsize=14)
plt.text(67,2e-6,'$Cs^{+2}$',fontsize=14)
plt.text(133,2e-6,'$Cs^{+}$',fontsize=14)

plt.show()

