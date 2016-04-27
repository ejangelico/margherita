#!/usr/bin/python

# interface to Omega CN616 temperature controller
# Uses database table CN616
# args are: callfrom action pvname [value]

version  = 1.0
date     = 2016-04-19
author   = 'BWA'
tb_in_db = 'CN616'  # table in database

import sys
import subprocess
import psycopg2
import serial
import time
import re

callfrom = sys.argv[1] # for debugging
action   = sys.argv[2]

if action == 'ID':
  print "CN616"
  sys.exit(0)
if action == 'VER':
  print version
  sys.exit(0)
if action == 'date':
  print date
  sys.exit(0)
if action == 'AUT':
  print author
  sys.exit(0)
if action == 'DBT':
  print tb_in_db
  sys.exit(0)
########################################
if action == 'EXEC':
  pvname  = sys.argv[3]

#print "debug: "+action+" "+pvname+" "+value

f = open('./database','r')
dbase=f.readline()
dbase = re.sub('\n','',dbase)

# find PV in database, DCH-specific table
try:
  conn = psycopg2.connect("dbname='"+dbase+"' user='xxx' ")
except:
  print "I am unable to connect to the database"
cur = conn.cursor()

#dbg="SELECT * FROM "+tb_in_db+" WHERE pvname = '"+pvname+"'"
#print dbg


try:
  cur.execute("SELECT * FROM "+tb_in_db+" WHERE pvname = '"+pvname+"'")
except:
  print "Can\'t find PV name "+pvname+" in "+tb_in_db+" database"
rows = cur.fetchall()


rw        = rows[0][2]
interface = rows[0][3]
commpars  = rows[0][4]
contrno   = rows[0][5] # controller no. .. on the bus
parameter = rows[0][6] # controller no. .. on the bus
zn        = rows[0][7]
zone = int(zn)

cp=commpars.split()
baud = cp[0]
bits = cp[1]
prty = cp[2]
stop = cp[3]

#
if zone < 1 or zone > 6:
  raise Exception("invalid zone "+zn)

#print "DCH: interface, motorname = "+interface+" "+baud+", "+motorname+": "+value
#print rw

if rw == 'W':
  value   = sys.argv[4]

ser = serial.Serial(interface,baud)
# print "PARAMETER "+parameter
if parameter == 'SETP': # read/write 1 of 6 setpoints
  cmd = "L"+contrno+'B' # get setpoints
  ser.write(cmd)        # 
  res = ser.read(24)
#  print res
  rr = re.findall('....',res)
  # for i in rr:  print i
  if rw == 'W':
    value=value[-4:]
    value=value.zfill(4)
#    print value
    rr[zone]=value
    ret = rr[0]+rr[1]+rr[2]+rr[3]+rr[4]+rr[5]
#    print ret
    cmd = "L"+contrno+'b'+ret
    ser.write(cmd)
  if rw == 'R':
    print rr[zone].lstrip("0") # could have used a regex, too
ser.close()
