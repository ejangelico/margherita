import DPS

h1 = DPS.DPS('/dev/ttyUSB1')
v, c, p = h1.read_vcp()
print "v, c, p = " + str(v) + ", " + str(c) + ", " + str(p)

