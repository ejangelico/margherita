# version 1 by Yushi Hu (UChicago) Feb 8 2018

import serial
import sys
import time
import threading


class Motor:
    def __init__(self, port):
        self.port = port  # string specifying serial port, ex: "/dev/ttyUSB0"
        self.ser = None  # the serial port that will be opened and closed during operation
        self.isopen = False  # is the serial port open
        self.pos = (0,0)  # current motor position
        self.natstep = 3.211 # commandstep/cm. measured. default in gcode
        self.basicInstruction = "G17 G21 G91 G54 "
        # unit cm s
        self.step = 1 # default step 1cm/step
        self.vel2 = 1.0231
        self.vel3 = 1.4935  # these speed are measured, unit cm/s, I use vel3 as default to calculate time
        self.vel4 = 1.9072
        # need measurement
        self.upperBoundx = 10
        self.upperBoundy = 10
        self.lowerBoundx = -10
        self.lowerBoundy = -10

    def __str__(self):
        st = ''
        if (self.isopen):
            st += "Port: " + self.port + "\n"
            st += "Position: " + self.pos + " step \n"
            st += "Step: " + self.step + " cm\step \n"
            st += "Velocity: " + (self.vel3/self.step) + " steps/s\n"
            st += "Is Open?: " + str(self.isopen) + "\n"
            return st
        else:
            print("Please open communications with the motor using motorOpen()")
            return "ERR"


    def setBoundaries(self, xrang, yrang):
        if(len(xrang) != 2 or len(xrang) != 2):
            print "Pass [xlower, xupper] and [ylower, yupper]"
            return
        else:
            self.upperBoundx = max(xrang)
            self.lowerBoundx = min(xrang)
            self.upperBoundy = max(yrang)
            self.lowerBoundy = min(yrang)

    # set current position as origin
    #maintains boundary even after changing origin
    def setOrigin(self):
        if (self.isopen):
            self.upperBoundx = self.upperBoundx - self.pos[0]
            self.upperBoundy = self.upperBoundy - self.pos[1]
            self.lowerBoundx = self.lowerBoundx - self.pos[0]
            self.lowerBoundy = self.lowerBoundy - self.pos[1]
            self.pos = (0,0)
        else:
            print("Please first open the serial communication before executing commands")
            return

    # move motor to absolute point (x0,y0)
    # if code works fine, it will return the estimated time of the movement
    def takeCor(self,x0,y0):
        if (self.isopen):
            if x0 > self.upperBoundx or x0 < self.lowerBoundx or y0 > self.upperBoundy or y0 < self.lowerBoundy:
                print "your move instruction is out of bounds.\nNo change made. Either change your origin or change your bounds"
                return
            x_disp = (x0 - self.pos[0])*self.step
            y_disp = (y0 - self.pos[1])*self.step
            time_x = x_disp/self.vel3
            time_y = y_disp/self.vel3
            time_real = max(abs(time_x),abs(time_y)) + 2.5 # time estimated to finish movement. 2.5 is for motor initiate
            print("estimated time: " + str(time_real) + " s\n")
            commandline = self.basicInstruction + "G1 X" + '%.03f'%(x_disp*self.natstep) + " Y" + '%.03f'%(y_disp*self.natstep) + " F300\n"
            print(commandline)
            self.ser.flush()
            self.pos = ((float('%.03f'%(x_disp*self.natstep))/self.natstep + self.pos[0])/self.step,(float('%.03f'%(y_disp*self.natstep))/self.natstep + self.pos[1])/self.step)
            self.ser.write(commandline.encode())
            self.ser.flush()
            # flowing is a timer that shows when movement is finish
            timer = threading.Timer(time_real,self.printFinish)
            timer.start()
            return time_real
        else:
            print("Please open communications with the motor using motorOpen()")
            return "ERR"

    def printFinish(self):
        print("Movement Finished\n")

    # move motor to relative distance (x0,y0)
    def moveRel(self, x0, y0):
        self.takeCor(x0 + self.pos[0], y0 + self.pos[1])

    def returnPos(self):
        if (self.isopen):
            print("x position is " + '%.03f'%(self.pos[0]) + " steps (" + '%.03f'%(self.pos[0] * self.step) + " cm )\n")
            print("y position is " + '%.03f'%(self.pos[1]) + " steps (" + '%.03f'%(self.pos[1] * self.step) + " cm )\n")
            # return in absolute coordinate
            return self.pos
        else:
            print("Please open communications with the motor using motorOpen()")
            return "ERR"


    # redefines the current absolute step number
    # must be greater than 0
    def redefineStep(self, s):
        if (self.isopen):
            if (s < 0):
                print("Tried redefining absolute position to a negative number!")
                print("Keeping current abs position definition the same")
                return
            else:
                x_new = self.pos[0]*self.step/s
                y_new = self.pos[1]*self.step/s
                self.lowerBoundx = self.lowerBoundx *self.step/s
                self.lowerBoundy = self.lowerBoundy *self.step/s
                self.upperBoundx = self.upperBoundx *self.step/s
                self.upperBoundy = self.upperBoundy *self.step/s
                self.pos = (x_new,y_new)
                self.step = s
                print("Now the step is" + str(s) + " cm/step\n")
                return
        else:
            print("Please first open the serial communication before executing commands")
            return

    # ----------Serial and Attribute Functions-----------#

    # opens serial communication with motor
    def motorOpen(self):
        self.ser = serial.Serial(self.port, baudrate=115200)
        b = self.ser.isOpen()
        if (b == True):
            self.ser.flush()
            self.isopen = True
            print("Motor communication port has been opened")
        else:
            self.isopen = False
            print("Could not open motor serial port, please check serial configuration")
            sys.exit()

    def motorClose(self):
        if (self.isopen == False):
            print("Motor communication port has been closed")
            return
        else:
            self.isopen = False
            self.ser.close()
            print("Motor communication port has been closed")
