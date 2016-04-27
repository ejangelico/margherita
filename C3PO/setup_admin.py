#!/usr/bin/python

import psycopg2
import re

f = open('./database','r')
dbase=f.readline()
dbase = re.sub('\n','',dbase)
print "Database: \n"+ dbase
exit(1)

try:
  conn = psycopg2.connect("dbname='"+dbase+"' user='marg' ")
  conn.autocommit = True
  # need to autocommit - otherwise entries visible only to this script
  # but not to psql interactive session
except:
  print "I am unable to connect to the database"
 
cur = conn.cursor()

# alias name, context in which it is used, PV name
Table_admin="CREATE TABLE admin ("+ \
  "id serial PRIMARY KEY,"+ \
  "key varchar (32) NOT NULL,"+ \
  "value varchar (128) NOT NULL,"+ \
  "comment varchar (256))"            

f = open('admindefs','r')
try:
  cur.execute("DROP TABLE admin")
except:
  print ""
cur.execute(Table_admin)

for line in f:
  dbstring = "INSERT INTO admin (key,value) VALUES ("
  line = re.sub('\n','',line)
  if re.match("^\s*\#",line) :
    f.next()
    continue
  words = line.split(", ")
  args = ""
  for w in words:
    if len(args) > 0 :
      args = args + ","
    args = args + "'"+w+"'"
  dbstring = dbstring + args + ")"
  #  print dbstring
  try: 
    cur.execute(dbstring)
  except:
    print "Cant execute:\n"+dbstring
