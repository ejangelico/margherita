import sys
import subprocess
import time

def setVI(setfile,vnew,inew,id):
    f = open(setfile, 'r')
    lines = f.readlines()   
    f.close()
    print('v {} i {}'.format(vnew,inew))

    if id==1:
	#header= '#heater,on/off,voltage-set,current-set'
	upline = 'uppper,1,{0:.2f},{1:.2f}\n'.format(vnew,inew)
	f = open(setfile, 'w')
	f.write('{0}{1}{2}'.format(lines[0],upline,lines[2]))
	#f.write('\n'.join([,upline,lines[2]]))
    elif id==0:
	lowline = 'lower,1,{0:.2f},{1:.2f}\n'.format(vnew,inew)
	f = open(setfile, 'w')
	f.write('{0}{1}{2}'.format(lines[0],lines[1],lowline))
    f.close()
    return

def setP(power,id):
    setfile = "./setpoints.txt"
    logfile = "../data/marg2heater_data/marg2heaterLog%s.txt" % time.strftime('%y%m%d') 
    process = subprocess.Popen(['tail','-1',logfile], stdout=subprocess.PIPE)
    out,err = process.communicate()
    if id==0:
	[old_v,old_i,old_p]=[float(_) for _ in out.split(',')[0:3]]
    elif id==1:
	    [old_v,old_i,old_p]=[float(_) for _ in out.split(',')[3:6]]
    new_v = old_v * (power/old_p)**0.5
    new_i = new_v / 9.0
    setVI(setfile,new_v,new_i,id)
    print('modified heater {} to power{:.1f}'.format(id,power))
    return

#lower_schedule=[67.6,69.5,71.8,74.5,77.8,81.7,86.3,91.6,97.8,104.9,113.0,122.2]
#upper_schedule=[11.9,12.4,13.1,14.7,15.8,17.1,18.6,20.4,22.4,24.7,27.2]
lower_schedule=[18,15,12,6,4,0.5,0.5]
upper_schedule=[4,4,3,3,2,2,1,1]
cs=list(zip(lower_schedule,upper_schedule))
    
for p in cs:
    setP(p[0],0)
    time.sleep(10)
    setP(p[1],1)
    time.sleep(1910)
