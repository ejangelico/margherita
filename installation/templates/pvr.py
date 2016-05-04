#!/usr/bin/python

# read from a PV
# usage pvw <pv name>
# pvname can be an actual PV or an alias
# HA level 0

import sys
import subprocess
import psycopg2
import re
import serial

if len(sys.argv) <> 3:
  raise Exception('pvr needs 2 arguments')

pvname  = sys.argv[2]
#value = sys.argv[3]

f = open('./userinfo','r')
unixuser = f.readline()
unixuser = re.sub('\n','',unixuser)
dbase    = f.readline()
dbase    = re.sub('\n','',dbase)

# look if 1st argument is an alias
try:
  conn = psycopg2.connect("dbname='"+dbase+"' user='"+unixuser+"' ")
except:
  print "Unable to connect to database xcap"
cur = conn.cursor()

cur.execute("SELECT pvname FROM alias WHERE alias = '"+pvname+"' AND rw = 'R'")
rows = cur.fetchall()
if len(rows) > 1:
  raise Exception('pvw found multiple alias correspondences')
if len(rows) == 1:
  pvname = rows[0][0]

# find PV in database
cur.execute("SELECT * FROM pvs WHERE pvname = '"+pvname+"'")
rows = cur.fetchall()
if len(rows) > 1:
  raise Exception('pvw found multiple entries for PV '+pvname)
if len(rows) == 0:
  raise Exception('pvw did not find a PV named '+pvname)
# check if type permits writing to PV
if re.match('R',rows[0][2]) == False:  # rows[0][.]: we know there is only one PV
  raise Exception('can\'t write to PV '+pvname)  
# get driver and secondary table
driver = rows[0][3]
sectb = rows[0][4]
# get path to driver
try:
  cur.execute("SELECT value FROM admin WHERE key = 'HSpath'")
except:
  print "Can\'t find level-0 path in table admin"
rows = cur.fetchall()
if len(rows) == 1:
  cmdpath = rows[0][0]
    
# call driver
res=subprocess.check_output([cmdpath+driver+".py",'EXEC',"pvr.py",sectb,pvname])

print res