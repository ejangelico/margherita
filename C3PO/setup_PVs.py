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


Table_PVs="CREATE TABLE PVs ("+ \
  "id serial PRIMARY KEY,"+ \
  "PVname varchar (32) NOT NULL,"+ \
  "type varchar (32) NOT NULL,"+ \
  "Drname varchar (32) NOT NULL,"+ \
  "action varchar (32) NOT NULL,"+ \
  "Side1 varchar (32),"+ \
  "Side2 varchar (32),"+ \
  "Side3 varchar (32),"+ \
  "Side4 varchar (32),"+ \
  "Tval varchar (32),"+ \
  "Aval varchar (32),"+ \
  "comment varchar (256))"            

f = open('./pvsdefs','r')
try:
  cur.execute("DROP TABLE pvs")
except:
  print ""
      
cur.execute(Table_PVs)

for line in f:
  dbstring = "INSERT INTO pvs (pvname,type,drname,action,side1) VALUES ("
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
  # print dbstring
  try: 
    cur.execute(dbstring)
  except:
    print "Can\'t execute:\n"+dbstring
