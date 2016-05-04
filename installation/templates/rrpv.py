#!/usr/bin/python

# read raw PV - for debugging purposes
# usage rrpv <PV name>
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
if len(sys.argv) <> 2:
  raise Exception('rrpv needs 1 argument')
  
pvname=sys.argv[1]
# SPx is a PV alias (look into file aliasdefs or database table "alias")

# call pvw: write to PV
#cmd = cmdpath+"pvw.py ssp.py "+SPno+" "+value
#print cmd
subprocess.call([cmdpath+"pvr.py","rrpv.py",pvname])
#                                  ^ 
#                                  traceback

