#shebang here

helpA = "set-up and start autotune or stop autotune"
helpB = "usage: auto <on | off > to start/stop autotune" 
helpC = "auto use <zone> <setpoint>"
helpD = "auto <pars> to read parameters from CN616 (zone, setpoint)"
# HA level 1

import sys
import subprocess
#import subprocess32 # more recent, for POSIX
import psycopg2  # needed to access database to get path to HA Level 0
import re

f = open('./userinfo','r')
unixuser = f.readline()
unixuser = re.sub('\n','',unixuser)
dbase    = f.readline()
dbase    = re.sub('\n','',dbase)

# get path to level 0
try: conn = psycopg2.connect("dbname='"+dbase+"' user='"+unixuser+"' ")
except: raise Exception("Can't connect to database "+dbase)

cur = conn.cursor()
try: cur.execute("SELECT value FROM admin WHERE key = 'HSpath'")
except: raise Exception("Can\'t find level-0 path in table admin")

rows = cur.fetchall()
if len(rows) == 1:
  cmdpath = rows[0][0]
#
if len(sys.argv) == 1 or sys.argv[1] == "help":
  print helpA
  print helpB
  print helpC
  print helpD
  sys.exit()
# 
if sys.argv[1] <> "on" and sys.argv[1] <> "off" and sys.argv[1] <> "pars"\
and sys.argv[1] <> "use":
  raise Exception('auto needs 1 (on/off/pars) or 3 (use <zone> <setpoint> arguments')
if sys.argv[1] == "on":
  subprocess.call([cmdpath+"pvw.py","auto.py","htr.autotune.run.W","1"])
if sys.argv[1] == "off":
  subprocess.call([cmdpath+"pvw.py","auto.py","htr.autotune.run.W","0"])
if sys.argv[1] == "pars":
  res=subprocess.check_output([cmdpath+"pvr.py","auto.py","htr.autotune.zone.R"])
  print "autotune zone: "+res  
  res=subprocess.check_output([cmdpath+"pvr.py","auto.py","htr.autotune.setp.R"])
  print "autotune setpoint: "+res  
if sys.argv[1] == "use":
  if len(sys.argv) <> 4: # 
    raise Exception('syntax is: auto use <zone> <setpoint>')  
  if (int(sys.argv[2])<1 or int(sys.argv[2])>6):
    raise Exception("invalid zone "+sys.argv[2]+" for autotune")
  if (int(sys.argv[3])<10 or int(sys.argv[3])>500):
    raise Exception("invalid setpoint "+sys.argv[2]+" for autotune; must be in [10 .. 500]")
  subprocess.call([cmdpath+"pvw.py","auto.py","htr.autotune.zone.W",sys.argv[2]])
  subprocess.call([cmdpath+"pvw.py","auto.py","htr.autotune.setp.W",sys.argv[3]])

#SPno = "SP"+sys.argv[1]
#value = sys.argv[2]

# call pvw: write to PV
#cmd = cmdpath+"pvw.py ssp.py "+SPno+" "+value
#print cmd
#subprocess.call([cmdpath+"pvw.py","ssp.py",SPno,value])

