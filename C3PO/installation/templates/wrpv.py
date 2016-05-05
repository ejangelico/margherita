#!/usr/bin/python

# write raw PV - for debugging
# usage wrpv <PV name> <value>
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
try:
  conn = psycopg2.connect("dbname='"+dbase+"' user='"+unixuser+"' ")
except: raise Exception("Can't to connect to database "+dbase)

cur = conn.cursor()
try:
  cur.execute("SELECT value FROM admin WHERE key = 'HSpath'")
except:
  print "Can\'t find level-0 path in table admin"
rows = cur.fetchall()
if len(rows) == 1:
  cmdpath = rows[0][0]
#    
if len(sys.argv) <> 3:
  raise Exception('wrpv needs 2 arguments')
  
pvname = sys.argv[1]
value = sys.argv[2]

# call pvw: write to PV
#cmd = cmdpath+"pvw.py ssp.py "+SPno+" "+value
#print cmd
subprocess.call([cmdpath+"pvw.py","wrpv.py",pvname,value])
