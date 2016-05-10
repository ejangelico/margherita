#!/opt/rh/python27/root/usr/bin/python

# get active zones of temp controller
# usage stczn 
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
except: raise Exception("Can't connect to database "+dbase+" as user "+unixuser)
cur = conn.cursor()
try: cur.execute("SELECT value FROM admin WHERE key = 'HSpath'")
except: raise Exception("Can\'t find level-0 path in table admin")

rows = cur.fetchall()
if len(rows) == 1:
  cmdpath = rows[0][0]
#    
  
cmd = "OmegaZones"

# TMx is a PV alias (look into file aliasdefs or database table "alias")
# call pvw: write to PV
#cmd = cmdpath+"pvw.py ssp.py "+SPno+" "+value
#print cmd
subprocess.call([cmdpath+"pvr.py","stczn.py",cmd], shell=True)
#                                  ^ 
#                                  traceback


