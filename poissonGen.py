import sys

if len(sys.argv) 1= 5:
	print 'Wrong Number of Arguments'
    print '[avgArrivalRate, avgStay, avgChargeNeed, timestep, interval]'
	sys.exit()



class Vehicle:
	numVehicles = 0

	def __init__(self, arrivalTime, depTime, chargeNeed):
		self.id = numVehicles
		numVehicles++
		self.arrivalTime = arrivalTime
		self.depTime = depTime
		self.chargeNeed = chargeNeed

	def getInfo(self):
		return [self.arrivalTime, self.depTime, self.chargeNeed]

avgArrivalRate = sys.argv[0]
avgStay = sys.argv[1]
avgChargeNeed = sys.argv[2]
timestep = sys.argv[3]
interval = sys.argv[4]






