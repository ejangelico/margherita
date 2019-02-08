# Usage delay_hlow.py N M changes hlow power N watts
import sys
import subprocess
import time

def modSetfileLow(setfile,vlow,ilow):
    f = open(setfile, 'r')
    lines = f.readlines()   
    f.close()

    header= '#heater,on/off,voltage-set,current-set'
    lowline = 'lower,1,{0:.2f},{1:.2f}\n'.format(vlow,ilow)
    f = open(setfile, 'w')
    f.write('{0}{1}{2}'.format(lines[0],lines[1],lowline))
    f.close()
    return

if __name__ == "__main__":
    setfile = "./setpoints.txt"
    logfile = "../data/marg2heater_data/marg2heaterLog%s.txt" % time.strftime('%y%m%d') 
    time.sleep(int(sys.argv[2]))
    process = subprocess.Popen(['tail','-1',logfile], stdout=subprocess.PIPE)
    out,err = process.communicate()
    [low_v,low_i,low_p]=[float(_) for _ in out.split(',')[0:3]]
    new_v = low_v * (float(sys.argv[1])/low_p)**0.5
    new_i = new_v / 9.0
    modSetfileLow(setfile,new_v,new_i)
