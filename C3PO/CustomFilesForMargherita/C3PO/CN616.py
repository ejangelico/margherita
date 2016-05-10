#!/opt/rh/python27/root/usr/bin/python

# interface to Omega CN616 temperature controller
# Uses database table CN616
# args are: callfrom action pvname [value]

version  = 1.0
date     = 2016-04-19
author   = 'BWA'

import sys
import subprocess
import psycopg2
import serial
import time
import re

action   = sys.argv[1]
callfrom = sys.argv[2] # for debugging

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
#if action == 'DBT':
#  print tb_in_db
#  sys.exit(0)
########################################
if action == 'EXEC': 
  tb_in_db  = sys.argv[3]
  pvname  = sys.argv[4]

#print "debug: "+action+" "+pvname+" "+value

f = open('./userinfo','r')
unixuser = f.readline()
unixuser = re.sub('\n','',unixuser)
dbase    = f.readline()
dbase    = re.sub('\n','',dbase)

# find PV in database, CN616-specific table
try:
  conn = psycopg2.connect("dbname='"+dbase+"' user='"+unixuser+"' ")
  conn.autocommit = True
except: raise Exception("I am unable to connect to database '"+dbase+"'")

cur = conn.cursor()

#dbg="SELECT * FROM "+tb_in_db+" WHERE pvname = '"+pvname+"'"
#print dbg

try: cur.execute("SELECT * FROM "+tb_in_db+" WHERE pvname = '"+pvname+"'")
except: raise Exception("Can\'t find PV name "+pvname+" in "+tb_in_db+" database")

rows = cur.fetchall()

rw        = rows[0][2]
interface = rows[0][3]
commpars  = rows[0][4]
contrno   = rows[0][5] # controller no. .. on the bus
parameter = rows[0][6] # controller no. .. on the bus
zn        = rows[0][7]
intPV     = rows[0][8] # internal PV

cp=commpars.split()
baud = cp[0]
bits = cp[1]
prty = cp[2]
stop = cp[3]

#print "DCH: interface, motorname = "+interface+" "+baud+", "+motorname+": "+value
#print rw

if rw == 'W':
  value   = sys.argv[5]

ser = serial.Serial(interface,baud)

# print "PARAMETER "+parameter

####################################
if parameter == 'MODL': # get ID string
  cmd = "L"+contrno+'J' # get temps
  ser.write(cmd)        # 
  res = ser.read(16)
  rr= res[4:7]
  print rr
####################################
if parameter == 'IDST': # get ID string
  cmd = "L"+contrno+'J' # get temps
  ser.write(cmd)        # 
  res = ser.read(16)
  rr= res[8:9]
  print rr
####################################
if parameter == 'ZONS': # set active zones
  cmd = "L"+contrno+'J' # 
  ser.write(cmd)        # 
  res = ser.read(16)
  if rw == 'R':
    print res[0:2]    
  if rw == 'W':
    if len(value) <> 2:
      raise Exception('wrong value string in ZONS')
    res=re.sub('^..',value,res)
    cmd = "L"+contrno+'j' # 
    cmd=cmd+res
    ser.write(cmd)        # 
####################################
if parameter == 'SETP' or parameter == 'TEMP':
  zone = int(zn)
  if zone < 1 or zone > 6:
    raise Exception("invalid zone "+zn)
  zone-=1  # zones are numbered 1..6, but indices 0..5
####################################  
if parameter == 'SETP': # read/write 1 of 6 setpoints
  cmd = "L"+contrno+'B' # get setpoints
  ser.write(cmd)        # 
  res = ser.read(24)
  rr = re.findall('....',res) # regex to split into chunks of 4
  if rw == 'W':
    value=value[-4:]
    value=value.zfill(4)
    rr[zone]=value
    ret = rr[0]+rr[1]+rr[2]+rr[3]+rr[4]+rr[5]
    cmd = "L"+contrno+'b'+ret
    ser.write(cmd)
  if rw == 'R':
    print re.sub('^0{1,3}','',rr[zone])
####################################
if parameter == 'TEMP': # read 1 of 6 temperatures
  cmd = "L"+contrno+'T' # get temps
  ser.write(cmd)        # 
  res = ser.read(28)
  rr = re.findall('....',res)
  print re.sub('^0{1,3}','',rr[zone])
#####################################
if parameter == "ATZN": # set zone to do autotune on
  if rw == 'W':
    dbstring = "INSERT INTO "+tb_in_db+" (pvname,type,parameter) VALUES ('"+intPV+"','I','"+value+"')"
    try: # insert zone number into database table
#      print dbstring
      cur.execute(dbstring)
    except:
      print "Can't insert auto zone into table"
  if rw == 'R':
    try:
      cur.execute("SELECT * FROM "+tb_in_db+" WHERE pvname = '"+intPV+"'")
    except:
      print "Can\'t find entry "+intPV+" in "+tb_in_db+" database"
#####################################
if parameter == "ATSP": # setpoint for autotune
  if rw == 'W':
    dbstring = "INSERT INTO "+tb_in_db+" (pvname,type,parameter) VALUES ('"+intPV+"','I','"+value+"')"
    try: # insert zone number into database table
#      print dbstring
      cur.execute(dbstring)
    except:
      print "Can't insert auto setpoint into table"
  if rw == 'R':
    try:
      cur.execute("SELECT * FROM "+tb_in_db+" WHERE pvname = '"+intPV+"'")
    except:
      print "Can\'t find entry __ATSP in "+tb_in_db+" database"
##################################  
if parameter == 'ATRN': # start/stop autotune
  try:
    cur.execute("SELECT * FROM "+tb_in_db+" WHERE pvname = '__ATSP'")
  except:
    print "Can\'t find entry __ATSP in "+tb_in_db+" database"
  
  
  cmd = "L"+contrno+'S' # 
  ser.write(cmd)        # 
  res = ser.read(6)
  
      
  
#  if value < 1:
  
 
  cmd = cmd + '0' + atzn
  
ser.close()
