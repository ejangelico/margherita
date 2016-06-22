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
import trace

spitout=1
##################
def trace_calls(frame, event, arg):
  if event != 'call':
    return
  func_line_no = frame.f_lineno
  caller = frame.f_back
  caller_line_no = caller.f_lineno
  if spitout == 1:
#    print "TRACE: line = "+str(func_line_no)
    print "TRACE: line = "+str(caller_line_no)
 
# sys.settrace(trace_calls)

#MODE = "simulate"
MODE = "run"

# format an int number nr to be exactly nd digits
def fint(nr,nd):
  res=str(nr)[-4:]
  res=res.zfill(nd)
  return res      
# for debugging
def SerOutput(cmd):
  if MODE == "run":
    ser.write(cmd) 
  else:
    print "DEBUGGING, sent: "+cmd
#
def SerInput(nc,default):
  if MODE == "run":
    return ser.read(nc)
  else:
    print "DEBUGGING, received: "+default
    return default
#
def lastValueToDb(tb_in_db,value,pvname):
#  print "UPDATE "+tb_in_db+" SET lastaccess = '"+value+"' WHERE pvname = '"+pvname+"'"  
  try: cur.execute("UPDATE "+tb_in_db+" SET lastaccess = '"+value+"' WHERE pvname = '"+pvname+"'")
  except: raise Exception("Can\'t find PV name "+pvname+" in "+tb_in_db+" database")  

################################# 
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

if rw == 'W':
  value   = sys.argv[5]

#lint
if MODE == "run": # run or simulate
  ser = serial.Serial(interface,baud)

####################################
if parameter == 'MODL': # get ID string
  cmd = "L"+contrno+'J' # get temps
#  ser.write(cmd)        # 
#  res = ser.read(16)
  SerOutput(cmd)
  res=SerInput(16,'0123456789ABCDEF')
  rr= res[4:7]
  print rr
####################################
if parameter == 'IDST': # get ID string
  cmd = "L"+contrno+'J' # get temps
#  ser.write(cmd)        # 
#  res = ser.read(16)
  SerOutput(cmd)
  res=SerInput(16,'0123456789ABCDEF')  
  rr= res[8:9]
  print rr
####################################
if parameter == 'ZONS': # set active zones
  cmd = "L"+contrno+'J' # 
#  ser.write(cmd)        # 
#  res = ser.read(16)
  SerOutput(cmd)
  res=SerInput(16,'0123456789ABCDEF')  
  if rw == 'R':
    print res[0:2]    
  if rw == 'W':
    if len(value) <> 2:
      raise Exception('wrong value string in ZONS')
    res=re.sub('^..',value,res)
    cmd = "L"+contrno+'j' # 
    cmd=cmd+res
#    ser.write(cmd)        # 
    SerOutput(cmd) 
####################################
if parameter == 'SETP' or parameter == 'TEMP':
  zone = int(zn)
  if zone < 1 or zone > 6:
    raise Exception("invalid zone "+zn)
  zone-=1  # zones are numbered 1..6, but indices 0..5
####################################  
if parameter == 'SETP': # read/write 1 of 6 setpoints
  cmd = "L"+contrno+'B' # get setpoints
  SerOutput(cmd)
  res=SerInput(24,'0123456789ABCDEF01234567')  
  rr = re.findall('....',res) # regex to split into chunks of 4
  if rw == 'W':
    value=value[-4:]
    value=value.zfill(4)
    rr[zone]=value
    ret = rr[0]+rr[1]+rr[2]+rr[3]+rr[4]+rr[5]
    cmd = "L"+contrno+'b'+ret
    SerOutput(cmd)
    lastValueToDb(tb_in_db,value,pvname)
  if rw == 'R':
    rsp = re.sub('^0{1,3}','',rr[zone])
    print rsp
    lastValueToDb(tb_in_db,rsp,pvname)
####################################
if parameter == 'TEMP': # read 1 of 6 temperatures
  cmd = "L"+contrno+'T' # get temps
  #ser.write(cmd)        # 
  #res = ser.read(28)
  SerOutput(cmd)
  res=SerInput(28,'0123456789ABCDEF0123456789AB')
  rr = re.findall('....',res)
  rtm = re.sub('^0{1,3}','',rr[zone])
  print rtm
  lastValueToDb(tb_in_db,rtm,pvname)
####################################
# alarms
if parameter == 'HALM' or parameter == 'LALM':
  zone = int(zn)
  if zone < 1 or zone > 6:
    raise Exception("invalid zone "+zn)
  zone-=1  # zones are numbered 1..6, but indices 0..5
####################################  
if parameter == 'HALM': # read/write 1 of 6 high alarms
  cmd = "L"+contrno+'C' # get alarms
  SerOutput(cmd)
  res=SerInput(24,'0123456789ABCDEF01234567')  
  rr = re.findall('....',res) # regex to split into chunks of 4
  if rw == 'W':
    value=value[-4:]
    value=value.zfill(4)
    rr[zone]=value
    ret = rr[0]+rr[1]+rr[2]+rr[3]+rr[4]+rr[5]
    cmd = "L"+contrno+'c'+ret
    SerOutput(cmd)
    lastValueToDb(tb_in_db,value,pvname)
  if rw == 'R':
    rsp = re.sub('^0{1,3}','',rr[zone])
    print rsp
    lastValueToDb(tb_in_db,rsp,pvname)
####################################  
if parameter == 'LALM': # read/write 1 of 6 low alarms
  cmd = "L"+contrno+'D' # get alarms
  SerOutput(cmd)
  res=SerInput(24,'0123456789ABCDEF01234567')  
  rr = re.findall('....',res) # regex to split into chunks of 4
  if rw == 'W':
    value=value[-4:]
    value=value.zfill(4)
    rr[zone]=value
    ret = rr[0]+rr[1]+rr[2]+rr[3]+rr[4]+rr[5]
    cmd = "L"+contrno+'d'+ret
    SerOutput(cmd)
    lastValueToDb(tb_in_db,value,pvname)
  if rw == 'R':
    rsp = re.sub('^0{1,3}','',rr[zone])
    print rsp
    lastValueToDb(tb_in_db,rsp,pvname)
####################################
# PID parameters
if parameter == 'PPCT' or parameter == 'PPHY' or parameter == 'PPPZ' \
   or parameter == 'PPPB' or parameter == 'PPRS' or parameter == 'PPRT' \
   or parameter == 'PPCZ':
  #get current PID pars
  cmd = "L"+contrno+'K' # get PIDpars
#  ser.write(cmd)        # 
#  res = ser.read(22)
  SerOutput(cmd)
  res=SerInput(22,'0123456789012345012345')  
  CycleTime  = int(res[:4])
  Hystereses = int(res[4:6])
  PidZoneEna = int(res[6:8])
  PropBand   = int(res[8:12])
  PIDReset   = int(res[12:16])
  PIDRate    = int(res[16:20])
  PIDCoolZnE = int(res[20:22])
  if rw == 'R':
    if parameter == 'PPCT': print CycleTime
    if parameter == 'PPHY': print Hystereses
    if parameter == 'PPPZ': print PidZoneEna
    if parameter == 'PPPB': print PropBand
    if parameter == 'PPRS': print PIDReset
    if parameter == 'PPRT': print PIDRate
    if parameter == 'PPCZ': print PIDCoolZnE    
  if rw == 'W':
    if parameter == 'PPCT' or parameter == 'PPPB' or \
       parameter == 'PPRS' or parameter == 'PPRT':
         value=value[-4:]
         value=value.zfill(4)        
    if parameter == 'PPHY' or parameter == 'PPPZ' or parameter == 'PPCZ':
         value=value[-2:]
         value=value.zfill(2)        
    if value.isdigit():
      if parameter == 'PPCT':
        CycleTime = value
      if parameter == 'PPHY':
        Hystereses = value
      if parameter == 'PPPZ': # set zones active under PID
#        PidZoneEna = value  
        zones = value.split()
        PidZoneEna = zones[0]+2*zones[1]+4*zones[2]+\
          10*(zones[3]+2*zones[4]+4*zones[5])
      if parameter == 'PPPB': 
        PropBand = value
      if parameter == 'PPRS': 
        PIDReset = value
      if parameter == 'PPRT': 
        PIDRate = value
      if parameter == 'PPCZ': 
        PIDCoolZnE = value
      PIDstring = fint(CycleTime,4)+fint(Hystereses,2)+fint(PidZoneEna,2)+\
                  fint(PropBand,4)+fint(PIDReset,4)+fint(PIDRate,4)+\
                  fint(PIDCoolZnE,2)
      cmd = "L"+contrno+'k'+PIDstring # set PIDpars
#  ser.write(cmd)
    SerOutput(cmd)      
  if parameter == 'PPCT': lastValueToDb(tb_in_db,str(CycleTime),pvname)
  if parameter == 'PPHY': lastValueToDb(tb_in_db,str(Hysteresis),pvname)
  if parameter == 'PPPZ': lastValueToDb(tb_in_db,str(PidZoneEna),pvname)
  if parameter == 'PPPB': lastValueToDb(tb_in_db,str(PropBand),pvname)
  if parameter == 'PPRS': lastValueToDb(tb_in_db,str(PIDReset),pvname)
  if parameter == 'PPRT': lastValueToDb(tb_in_db,str(PIDRate),pvname)
  if parameter == 'PPCZ': lastValueToDb(tb_in_db,str(PIDCoolZnE),pvname)
    
    # if not a positive int number, do nothing
#####################################
if parameter == "ATZN" or parameter == 'ATSP': # set zone to do autotune on
  cmd = "L"+contrno+'S'
  SerOutput(cmd)
  res=SerInput(6,'012345')  
  autozone = int(res[:2])
  autosetp = int(res[2:6])
  if rw == 'R':
    if parameter == 'ATSP': print autosetp
    if parameter == 'ATZN': print autozone        
  if rw == 'W':
    if parameter == 'ATSP': autosetp = value
    if parameter == 'ATZN': autozone = value      
    cmd = "L"+contrno+'s'+fint(autozone,2)+fint(autosetp,4)+"00"
    SerOutput(cmd)
  if parameter == 'ATSP': lastValueToDb(tb_in_db,str(autosetp),pvname)
  if parameter == 'ATZN': lastValueToDb(tb_in_db,str(autozone),pvname)      
##################################  
if parameter == 'ATRN': # start/stop autotune
#  print "VALUE = "+ value
  if value == "1":
    cmd = 'L'+contrno+'G' # 
  if value == "0":
    cmd = 'L'+contrno+'H' # 
  SerOutput(cmd)  
############################
if MODE == "run": # run or simulate
  ser.close()
