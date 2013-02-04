class Vehicle:
    numVehiclesMade = 0

    def __init__( self, arrivalTime, depTime, chargeNeeded, currentCharge, chargeRate, maxCapacity ):
        self.id = Vehicle.numVehiclesMade
        Vehicle.numVehiclesMade += 1
        self.arrivalTime = arrivalTime
        self.depTime = depTime
        self.chargeNeeded = chargeNeeded
        self.currentCharge = currentCharge
        self.chargeRate = chargeRate
        self.maxCapacity = maxCapacity

    def failedToString():
        print "ID: " , self.id , "  current charge: " , self.currentCharge , "  charge needed: " , self.chargeNeeded , "   departure time: " , self.depTime

#    def getInfo(self):
#        return [self.arrivalTime, self.depTime, self.chargeNeeded, self.currentCharge, self.chargeRate, self.maxCapacity]
