# Usage hup_power.py N sets hup power to N watts
import sys
import subprocess
import time

def modSetfileUp(setfile,vup,iup):
    f = open(setfile, 'r')
    lines = f.readlines()   
    f.close()

    header= '#heater,on/off,voltage-set,current-set'
    upline = 'uppper,1,{0:.2f},{1:.2f}'.format(vup,iup)
    f = open(setfile, 'w')
    f.write('\n'.join([header,upline,lines[2]]))
    f.close()
    return

if __name__ == "__main__":
    setfile = "./setpoints.txt"
    logfile = "../data/marg2heater_data/marg2heaterLog%s.txt" % time.strftime('%y%m%d') 
    time.sleep(int(sys.argv[2]))
    process = subprocess.Popen(['tail','-1',logfile], stdout=subprocess.PIPE)
    out,err = process.communicate()
    [up_v,up_i,up_p]=[float(_) for _ in out.split(',')[3:6]]
    new_v = up_v * (float(sys.argv[1])/up_p)**0.5
    new_i = new_v / 18.0
    modSetfileUp(setfile,new_v,new_i)
