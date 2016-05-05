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

# alias name, context in which it is used, PV name
Table_alias="CREATE TABLE alias ("+ \
  "id serial PRIMARY KEY,"+ \
  "alias varchar (32) NOT NULL,"+ \
  "rw varchar (32) NOT NULL,"+ \
  "context varchar (32) NOT NULL,"+ \
  "PVname varchar (32) NOT NULL,"+ \
  "comment varchar (256))"            

f = open('aliasdefs','r')
try:
  cur.execute("DROP TABLE alias")
except:
  print ""
cur.execute(Table_alias)

for line in f:
  dbstring = "INSERT INTO alias (alias,rw,context,pvname,comment) VALUES ("
  line = re.sub('\n','',line)
  if re.match("^\s*\#",line) :
    continue
  words = line.split(", ")
  args = ""
  for w in words:
    w=w.strip() # remove leading, trailing whitespace
    if len(args) > 0 :
      args = args + ","
    args = args + "'"+w+"'"
  dbstring = dbstring + args + ")"
  try: 
    cur.execute(dbstring)
  except:
    print dbstring