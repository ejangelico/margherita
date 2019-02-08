import serial
import os
import sys
import time
import Motor
import TwoMotors
from itertools import combinations
import numpy as np 

global motorSerX
global motorSerY
global motorIdX
global motorIdY


motorSerX = "/dev/ttyUSB1"
motorSerY = "/dev/ttyUSB2"
motorIdX = 1
motorIdY = 1




#this function 
#(1)moves to each point in a set of points
#(2)at each point, waits a short amount of time
#(3)logs the time and location after this short amount of time
#(4) and moves to the next point
def continuousScan(motors, positions):
	integrationTime = 10   #seconds, time to wait at each point

	posCounter = 0  #variable that indexes the current scan position
	
	#either +1 or -1 depending on which direction you are sweeping in the position array
	#must start as -1
	direction = -1 
	while True:
		motors.ma(positions[posCounter][0], positions[posCounter][1])
		print "Sleeping for " + str(integrationTime) + "s"
		time.sleep(integrationTime)
		curx, cury = motors.getPos()
		outfile = open('/local/data2/margherita/data/motor_data/motorLog{0}.txt'.format(time.strftime('%y%m%d')),'a')
		outfile.write(str(curx) + "," + str(cury) + "," + time.strftime('%m-%d-%y %H:%M:%S') + "\n")
		outfile.close()

		#do the next position
		#currently programmed to go
		#through each of the positions, then
		#go backwards along the same path
		if(posCounter == (len(positions) - 1) or posCounter == 0):
			#turn around
			direction = -1*direction
		
		posCounter += direction




#this function
#(1)moves to a point and stays there for a longer period of time
#(2)logs a position/time every 5 or so seconds at this fixed position
#(3)then moves to the next position
def sitAndWaitScan(motors, positions):
	waitTime = 5 				#minutes, total time logging data at each point
	measurementInterval = 5 	#seconds between logged measurements
	posCounter = 0  			#variable that indexes the current scan position
	
	#either +1 or -1 depending on which direction you are sweeping in the position array
	#must start as -1
	direction = -1 
	while True:
		motors.ma(positions[posCounter])
		#wait at the position and log
		starttime = int(time.strftime("%s"))
		endtime = starttime + waitTime*60
		while(int(time.strftime("%s")) < endtime):
			time.sleep(measurementInterval)
			curx, cury = motors.getPos()
			outfile = open('/local/data2/margherita/data/motor_data/motorLog{0}.txt'.format(time.strftime('%y%m%d')),'a')
			outfile.write(str(curx) + "," + str(cury) + "," + time.strftime('%m-%d-%y %H:%M:%S') + "\n")
			outfile.close()

		#do the next position
		#currently programmed to go
		#through each of the positions, then
		#go backwards along the same path
		if(posCounter == (len(positions) - 1) or posCounter == 0):
			#turn around
			direction = -1*direction
		
		posCounter += direction



#returns an array of positions
#for the laser to scan over
#WRITE this array in the order you want to scan
def config1Positions():
	pos = [
			[16,14],
			[15,13],
			[14,12],
			]
	return pos

#a bounding square for the spot
#near the copper tubulation
def config2Positions():
	# makes a rectangular grid with even spacing
	# Adjust xlims, ylims and stepSize
	pos = []
	xlims = [0, 15.7]
	ylims = [0, 16.9]
	stepSize = 3.12
	generateSquare(xlims, ylims, stepSize, pos)
	
	
	print len(pos)
	print stepSize
	return pos

#region that is the compliment
#to config2
def config3Positions():
	stepSize = 0.4 #cm
	pos = []

	#square region 1
	ylims = [9.4, 11]
	xlims = [16.7, 18.75]
	generateSquare(xlims, ylims, stepSize, pos)

	#triangle region 1
	ylims = [9.4, 11]
	xlims = [15.1, 16.7]
	rightvertex = [16.7, 9.4]
	generateTriangle(xlims, ylims, rightvertex, stepSize, pos)


	#square region 2
	ylims = [0, 9.4]
	xlims = [0, 18.75]
	generateSquare(xlims, ylims, stepSize, pos)

	#square region 3
	ylims = [9.4, 17.3]
	xlims = [0, 8]
	generateSquare(xlims, ylims, stepSize, pos)

	#triangle region 4
	ylims = [9.4, 12.4]
	xlims = [8, 11]
	rightvertex = [8, 9.4]
	generateTriangle(xlims, ylims, rightvertex, stepSize, pos)

	


		
	print len(pos)
	#print stepSize
	#sys.exit()
	return pos

#generates a rectangle of lattice points given two
#bounding lines in x and y
def generateSquare(xlims, ylims, stepSize, pos):
	cury = max(ylims)
	curx = max(xlims)
	direction = -1
	while (cury >= ylims[0] and cury <= ylims[1]):
		pos.append([curx, cury])
		curx = curx + direction*stepSize
		while (curx >= xlims[0] and curx <= xlims[1]):
			pos.append([curx, cury])
			curx = curx + direction*stepSize
		
		direction = -1*direction
		curx = curx + direction*stepSize
		cury = cury - stepSize	
	print pos


#generates lattice points of a right triangle with
#a vertex point (which has the right angle) "v"
#and a diagonal that matches that vertex point based on
#the "square" limits xlims and ylims
def generateTriangle(xlims, ylims, v, stepSize, pos):
	sqPoints = []
	generateSquare(xlims, ylims, stepSize, sqPoints)

	#-------#
	#find all of the points in sqPoints
	#that exist inside the desired triangle
	#-------#

	#parametrize the line defined by the triangle's
	#hypotenus
	fourPoints = [[xlims[0], ylims[0]], [xlims[0], ylims[1]], [xlims[1], ylims[0]], [xlims[1], ylims[1]]]
	twopointCombos = [x for x in combinations(fourPoints, 2)]
	#parameters for hypotenus
	hypPoints = None
	hypSlope = None
	hx = None
	hy = None
	for comb in twopointCombos:
		if(comb[0] == v or comb[1] == v):
			continue
		else:
			x1 = comb[0][0]
			y1 = comb[0][1]
			x2 = comb[1][0]
			y2 = comb[1][1]
			if(x2 - x1 == 0 or y2 - y1 == 0):
				continue
			else:
				hypPoints = comb
				hypSlope = (y2 - y1)/(x2 - x1)
				hx = x1
				hy = y1

	if(hypPoints == None):
		print "Could not find hypotenuse of the desired triangle"
		return None

	#use the line parametrization of the hypotenus
	#to reject points that lie outside of the triangle
	for dot in sqPoints:
		#parametrize the line defined by the
		#dot coordinates and the right and vertex point
		if(dot[0] == v[0]):
			pos.append(dot)
			continue
		mp = (dot[1] - v[1])/(dot[0] - v[0])

		#find two lengths of line segments
		#which connect three points 
		#(1) the vertex point
		#(2) the test dot
		#(3) the intersection at the hypotenus
		Lintersect = abs(((1.0)/(hypSlope - mp))*(v[1] - v[0] + hx - hy))
		Ldot = abs(dot[0] - v[0])
		if(Ldot <= Lintersect):
			pos.append(dot)
		else:
			continue




def plotMapPoints(points):
	x = []
	y = []
	for p in points:
		x.append(p[0])
		y.append(p[1])

	fig, ax = plt.subplots(figsize=(10,10))
	ax.scatter(x, y)
	ax.set_xlim([max(x), min(x)])


if __name__ == "__main__":
	motx = Motor.Motor(motorSerX, motorIdX)
	moty = Motor.Motor(motorSerY, motorIdY)
	motors = TwoMotors.TwoMotors(motx, moty)
	motors.openMotors()
	#mapPositions = config2Positions()
	mapPositions = [[0, 0], [7, 7], [16, 16], [16, 0], [0, 16]]

	"""	
	#make a line specific for our "long distance"
	#cesiation on 7/26/17
	#line goes in y direction
	x = 8
	ystart = 16.5
	npoints = 8
	step = 2 #cm
	for i in range(npoints):
		mapPositions.append([x, ystart - i*step])
	"""


	continuousScan(motors, mapPositions)
