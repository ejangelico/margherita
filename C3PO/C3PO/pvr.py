#!/usr/bin/python

# read from a PV
# usage pvr <pv name>
# pvname can be an actual PV or an alias
# HA level 0

import sys
import subprocess
import psycopg2
import re
import serial

if len(sys.argv) <> 3:
  raise Exception('pvr needs 2 arguments')

calledfrom = sys.argv[1]
pvname  = sys.argv[2]
#value = sys.argv[3]

#print "CONTEXT = |"+calledfrom+"|"
#exit()
f = open('./userinfo','r')
unixuser = f.readline()
unixuser = re.sub('\n','',unixuser)
dbase    = f.readline()
dbase    = re.sub('\n','',dbase)

# look if 1st argument is an alias
try:
  conn = psycopg2.connect("dbname='"+dbase+"' user='"+unixuser+"' ")
except: raise Exception("Can't to connect to database "+dbase)

cur = conn.cursor()

dbstring = "SELECT pvname FROM alias WHERE alias = '"+pvname+"' AND rw = 'R'  AND "+"(context = '"+calledfrom+"' OR context = 'any' OR context = '')"
cur.execute(dbstring)
rows = cur.fetchall()
if len(rows) > 1:
  raise Exception('pvr found multiple alias correspondences')
if len(rows) == 1:
  pvname = rows[0][0]

#dbstring = "SELECT * FROM alias WHERE alias = '"+pvname+"' AND rw = 'R' "  
#cur.execute(dbstring)
#rows = cur.fetchall()
#print "ROWS = "
#print rows[0]


# find PV in database
cur.execute("SELECT * FROM pvs WHERE pvname = '"+pvname+"'")
rows = cur.fetchall()
if len(rows) > 1:
  raise Exception('pvr found multiple entries for PV '+pvname)
if len(rows) == 0:
#   print "PVNAME = "+pvname
  raise Exception("pvr did not find a PV named "+pvname+" or an alias "+pvname+" in context "+calledfrom)
# check if type permits writing to PV
if re.match('R',rows[0][2]) == False:  # rows[0][.]: we know there is only one PV
  raise Exception('can\'t read from PV '+pvname)  
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

#print(res,end="")
print res,  # the comma prevents \n
