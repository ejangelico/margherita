#!/usr/bin/python

# write to a PV
# usage pvw <pv name> <value>
# pvname can be an actual PV or an alias
# HA level 0

import sys
import subprocess
import psycopg2
import re

if len(sys.argv) <> 4:
  raise Exception('pvw needs 3 arguments')

name  = sys.argv[2]
value = sys.argv[3]

# print "1PVW, name = "+name+" , value = "+value

f = open('./database','r')
dbase=f.readline()
dbase = re.sub('\n','',dbase)

# look if 1st argument is an alias
try:
  conn = psycopg2.connect("dbname='"+dbase+"' user='xxx' ")
except:
  print "Unable to connect to database "+dbase
cur = conn.cursor()

cur.execute("SELECT pvname FROM alias WHERE alias = '"+name+"' AND rw = 'W'")
rows = cur.fetchall()
if len(rows) > 1:
  raise Exception('pvw found multiple alias correspondences')
if len(rows) == 1:
  name = rows[0][0]

# print "PVW, name = "+name+" , value = "+value

# find PV in database
cur.execute("SELECT * FROM pvs WHERE pvname = '"+name+"'")
rows = cur.fetchall()
if len(rows) > 1:
  raise Exception('pvw found multiple entries for PV '+name)
if len(rows) == 0:
  raise Exception('pvw did not find a PV named '+name)
# check if type permits writing to PV
if re.match('W',rows[0][2]) == False:  # rows[0][.]: we know there is only one PV
  raise Exception('can\'t write to PV '+name)  
# get driver and action
driver = rows[0][3]
action = rows[0][4]
# get path to driver
try:
  cur.execute("SELECT value FROM admin WHERE key = 'HSpath'")
except:
  print "Can\'t find level-0 path in table admin"
rows = cur.fetchall()
if len(rows) == 1:
  cmdpath = rows[0][0]
    
    
# call driver
subprocess.call([cmdpath+driver+".py","pvw.py",action,name,value])

