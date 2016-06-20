#!/usr/bin/python

import psycopg2
import re

f = open('./userinfo','r')
unixuser = f.readline()
unixuser = re.sub('\n','',unixuser)
dbase    = f.readline()
dbase    = re.sub('\n','',dbase)

try:
  conn = psycopg2.connect("dbname='"+dbase+"' user='"+unixuser+"' ")
  conn.autocommit = True
  # need to autocommit - otherwise entries visible only to this script
  # but not to psql interactive session
except: raise Exception("Can't to connect to database "+dbase)
 
cur = conn.cursor()

Table_CN616="CREATE TABLE CN616 ("+ \
  "id serial PRIMARY KEY,"+ \
  "PVname varchar (32) NOT NULL,"+ \
  "type varchar (32) NOT NULL,"+ \
  "interface varchar (64) NOT NULL,"+ \
  "commpars varchar (64) NOT NULL,"+ \
  "contrno varchar (32),"+ \
  "parameter varchar (32),"+ \
  "value varchar (32),"+ \
  "lastAccess varchar (32),"+ \
  "intPV varchar (256),"+ \
  "comment varchar (256))"            

f = open('./CN616defs','r')
try:
  cur.execute("DROP TABLE CN616")
except:
  print ""
      
cur.execute(Table_CN616)

for line in f:
  dbstring = "INSERT INTO CN616 (pvname,type,interface,commpars,contrno,\
parameter,value,lastAccess,intPV,comment) VALUES ("
  line = re.sub('\n','',line)
  if re.match("^\s*\#",line) :
    #f.next()
    continue
  words = line.split(", ")
  args = ""
  for w in words:
    w=w.strip() # remove leading, trailing whitespace
    #print "w = "+w
    if len(args) > 0 :
      args = args + ","
    args = args + "'"+w+"'"
  dbstring = dbstring + args + ")"
  # print dbstring
  try: 
    cur.execute(dbstring)
  except:
    print "Can\'t execute:\n"+dbstring
