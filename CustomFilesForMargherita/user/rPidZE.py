#!/usr/bin/python

helpA =  "read PID enabled zones"
helpB = "usage rPidZE (no arguments)"
helpC = ""
# HA level 1

import sys
import subprocess
#import subprocess32 # more recent, for POSIX
import psycopg2  # needed to access database to get path to HA Level 0
import re
import os
os.chdir(os.path.dirname(sys.argv[0]))

nargs=0
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
#if len(sys.argv) <> 1: raise Exception(this+"needs "+str(nargs)+" argument(s)")

if len(sys.argv) <> (nargs+1) or sys.argv[len(sys.argv) -1 ] == "help":
  print helpA
  print helpB
  print helpC
  sys.exit()        

res=subprocess.check_output([cmdpath+"pvr.py",this,"htr.pidpar.PZEn.R"])
print res
#                                  ^ 
#                                  traceback


