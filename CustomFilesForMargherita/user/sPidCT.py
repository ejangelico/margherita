#!/usr/bin/python

# set PID hysteresis
# usage rPidH.py <hysteresis>
# HA level 1

import sys
import subprocess
#import subprocess32 # more recent, for POSIX
import psycopg2  # needed to access database to get path to HA Level 0
import re
import os
os.chdir(os.path.dirname(sys.argv[0]))

nargs=2
this = re.sub('^\.\/','',sys.argv[0])

f = open('./userinfo','r')
unixuser = f.readline()
unixuser = re.sub('\n','',unixuser)
dbase    = f.readline()
dbase    = re.sub('\n','',dbase)

# get path to level 0
try: conn = psycopg2.connect("dbname='"+dbase+"' user='"+unixuser+"' ")
except: raise Exception("Can't connect to database "+dbase+" as user "+unixuser)
cur = conn.cursor()
try: cur.execute("SELECT value FROM admin WHERE key = 'HSpath'")
except: raise Exception("Can\'t find level-0 path in table admin")

rows = cur.fetchall()
if len(rows) == 1:
  cmdpath = rows[0][0]
#    
if len(sys.argv) <> 2: raise Exception(this+"needs "+str(nargs)+" argument(s)")
  
subprocess.call([cmdpath+"pvw.py",this,"htr.pidpar.CycTm.W",sys.argv[1]])
#                                  ^ 
#                                  traceback


