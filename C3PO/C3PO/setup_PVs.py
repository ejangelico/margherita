#!/opt/rh/python27/root/usr/bin/python

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

Table_PVs="CREATE TABLE PVs ("+ \
  "id serial PRIMARY KEY,"+ \
  "PVname varchar (32) NOT NULL,"+ \
  "type varchar (32) NOT NULL,"+ \
  "Drname varchar (32) NOT NULL,"+ \
  "Tbname varchar (32) NOT NULL,"+ \
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
  print "looking at line: " + line
  dbstring = "INSERT INTO pvs (pvname,type,drname,tbname,side1,side2,side3,side4,tval) VALUES ("
  line = re.sub('\n','',line)
  if re.match("^\s*\#",line) :
    #f.next()
    continue
  words = line.split(", ")
  args = ""
  for w in words:
    w=w.strip() # remove leading, trailing whitespace
    print "w = "+w
    if len(args) > 0 :
      args = args + ","
    args = args + "'"+w+"'"
    print "args = " + args
  dbstring = dbstring + args + ")"
  print dbstring
  try: 
    cur.execute(dbstring)
  except:
    print "Can\'t execute:\n"+dbstring
