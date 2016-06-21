#!/bin/bash

for i in {1..50}
do
   ./ssp.py 2 "$((150 + $i * 1))"
   echo setpoint T
   ./rsp.py 2 
   echo measured T
   ./rtm.py 2
   ./ssp.py 5 "$((150 + $i * 1))"
   echo setpoint T
   ./rsp.py 5 
   echo measured T
   ./rtm.py 5
   ./ssp.py 6 "$((150 + $i * 1))"
   echo setpoint T
   ./rsp.py 6 
   echo measured T
   ./rtm.py 6
   echo
   sleep 20
done


