#!/usr/bin/python

# read a temperature
# usage rtm <SP no 1..6> <value>
# HA level 1

import sys
import subprocess
#import subprocess32 # more recent, for POSIX
import psycopg2  # needed to access database to get path to HA Level 0
import re
import os
os.chdir(os.path.dirname(sys.argv[0]))

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
if len(sys.argv) <> 2:
  raise Exception('rtm needs 1 argument')
  
TMno = "TM"+sys.argv[1]
# TMx is a PV alias (look into file aliasdefs or database table "alias")
# call pvw: write to PV
#cmd = cmdpath+"pvw.py ssp.py "+SPno+" "+value
#print cmd
#print TMno
res=subprocess.check_output([cmdpath+"pvr.py","rtm.py",TMno])
print res
#                                  ^ 
#                                  traceback


