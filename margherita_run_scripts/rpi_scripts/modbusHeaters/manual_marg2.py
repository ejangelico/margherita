#Basic usage (Evan, 3/7/18)
#python -i manual_marg2.py
#
#
#hlow.set_iv(<i amps>, <v volts>)
#hup.set_iv(<i amps>, <v volts>)
#print_all_vcp_applied()
#
#
#logging to come shortly
######################################



import DPS


global hlow
global hup
global htest

hlow = DPS.DPS('/dev/ttyUSB3')
hup = DPS.DPS('/dev/ttyUSB2')
htest = DPS.DPS('/dev/ttyUSB1')



def print_all_vcp_applied():
    v, c, p = hlow.read_vcp_applied()
    print "Lower heater is applying : " + str(v) + " volts, " + str(c) + " amps, " + str(p) + " watts"
    v, c, p = hup.read_vcp_applied()
    print "Upper heater is applying : " + str(v) + " volts, " + str(c) + " amps, " + str(p) + " watts"

if __name__ == "__main__":

    print_all_vcp_applied()
    

