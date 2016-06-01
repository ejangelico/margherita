#!/opt/rh/python27/root/usr/bin/python

# set-up and start autotune or stop autotune
# usage auto <0:stop, 1: start> [<zone> <setp>] 
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
if len(sys.argv) <> 2 and len(sys.argv) <> 3:
  raise Exception('auto needs 1 or 2 arguments')
  
if len(sys.argv) == 2: # just start/stop
  subprocess.call([cmdpath+"pvw.py","auto.py","htr.autotune.run.W",sys.argv[1]])
if len(sys.argv) == 3: # start with parameters
  subprocess.call([cmdpath+"pvw.py","auto.py","htr.autotune.zone.W",sys.argv[1]])
  subprocess.call([cmdpath+"pvw.py","auto.py","htr.autotune.setp.W",sys.argv[2]])
#  subprocess.call([cmdpath+"pvw.py","auto.py","htr.autotune.run.W",sys.argv[1]])


#SPno = "SP"+sys.argv[1]
#value = sys.argv[2]

# call pvw: write to PV
#cmd = cmdpath+"pvw.py ssp.py "+SPno+" "+value
#print cmd
#subprocess.call([cmdpath+"pvw.py","ssp.py",SPno,value])

