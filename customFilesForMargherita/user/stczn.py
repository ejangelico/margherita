#!/usr/bin/python

# set active zones of temp controller
# usage stczn <list of active zones>
# will enable all zones listed, disable all other ones
# example stczn 1 3 6 will enable zones 1, 3, and 6, and disable 2, 4, 5
# HA level 1

import sys
import subprocess
#import subprocess32 # more recent, for POSIX
import psycopg2  # needed to access database to get path to HA Level 0
import re

f = open('./database','r')
dbase=f.readline()
dbase = re.sub('\n','',dbase)

# get path to level 0
try:
  conn = psycopg2.connect("dbname='"+dbase+"' user='xxx' ")
except:
  print "I am unable to connect to the database"
cur = conn.cursor()
try:
  cur.execute("SELECT value FROM admin WHERE key = 'HSpath'")
except:
  print "Can\'t find level-0 path in table admin"
rows = cur.fetchall()
if len(rows) == 1:
  cmdpath = rows[0][0]
#    
  
cmd = "OmegaZones"
zones = 0
for i in range(1,len(sys.argv)):
  zn=int(sys.argv[i])
  if zn<1 or zn>6:
    continue
  if zn<4:
    zn-=1
  zb = 1 << zn
#  print zb
  zones = zones | zb
  zonestring = format(zones, '02X')

# TMx is a PV alias (look into file aliasdefs or database table "alias")
# call pvw: write to PV
#cmd = cmdpath+"pvw.py ssp.py "+SPno+" "+value
#print cmd
subprocess.call([cmdpath+"pvw.py","stczn.py",cmd,zonestring])
#                                  ^ 
#                                  traceback


