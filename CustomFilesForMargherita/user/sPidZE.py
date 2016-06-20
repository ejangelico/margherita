#!/usr/bin/python

import sys
import subprocess
#import subprocess32 # more recent, for POSIX
import psycopg2  # needed to access database to get path to HA Level 0
import re

helpA = "set zones active under PID control"
helpB = "usage sPidD.py <0|1> <0|1> <0|1> <0|1> <0|1> <0|1> "
helpC = "to (de)activate zones 1 .. 6"

# HA level 1

nargs=6 # not counting sys.argv[0]
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
if len(sys.argv) <> (nargs+1) or sys.args[1] == "help":
  print helpA
  print helpB
  print helpC
  sys.exit()

# if len(sys.argv) <> 2: raise Exception(this+"needs "+str(nargs)+" argument(s)")
zonestring = sys.argv[1]+" "+sys.argv[2]+" "+sys.argv[3]+" "+sys.argv[4]+" "+sys.argv[5]+" "+sys.argv[6]  
subprocess.call([cmdpath+"pvw.py",this,"htr.pidpar.PidZEn.W",zonestring])
#                                  ^ 
#                                  traceback


