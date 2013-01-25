import sys

if len(sys.argv) > 5:
	print 'Too many arguments'
	sys.exit()
if len(sys.argv) < 5:
	print 'Too few arguments'
	sys.exit()

class Vehicle:
	numVehicles = 0

	def __init__(self, arrivalTime, depTime, chargeNeed)
		self.id = numVehicles
		numVehicles++
		self.arrivalTime = arrivalTime
		self.depTime = depTime
		self.chargeNeed = chargeNeed

	def getInfo(self):
		
