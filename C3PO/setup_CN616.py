#!/usr/bin/python

import psycopg2
import re

f = open('./database','r')
dbase=f.readline()
dbase = re.sub('\n','',dbase)

try:
  conn = psycopg2.connect("dbname='"+dbase+"' user='marg' ")
  conn.autocommit = True
  # need to autocommit - otherwise entries visible only to this script
  # but not to psql interactive session
except:
  print "I am unable to connect to the database"
 
cur = conn.cursor()


Table_CN616="CREATE TABLE CN616 ("+ \
  "id serial PRIMARY KEY,"+ \
  "PVname varchar (32) NOT NULL,"+ \
  "type varchar (32) NOT NULL,"+ \
  "interface varchar (32) NOT NULL,"+ \
  "commpars varchar (32) NOT NULL,"+ \
  "contrno varchar (8) NOT NULL,"+ \
  "parameter varchar (32) NOT NULL,"+ \
  "zone varchar (8) NOT NULL,"+ \
  "comment varchar (256))"            

f = open('./CN616defs','r')
try:
  cur.execute("DROP TABLE CN616")
except:
  print ""
      
cur.execute(Table_CN616)

for line in f:
  dbstring = "INSERT INTO CN616 (pvname,type,interface,commpars,contrno,parameter,zone,comment) VALUES ("
  line = re.sub('\n','',line)
  if re.match("^\s*\#",line) :
    #f.next()
    continue
  words = line.split(", ")
  args = ""
  for w in words:
    if len(args) > 0 :
      args = args + ","
    args = args + "'"+w+"'"
  dbstring = dbstring + args + ")"
  #print dbstring
  try: 
    cur.execute(dbstring)
  except:
    print "Can\'t execute:\n"+dbstring
