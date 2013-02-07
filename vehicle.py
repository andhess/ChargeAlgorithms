class Vehicle:
    numVehiclesMade = 0

    def __init__( self, arrivalTime, depTime, chargeNeeded, currentCharge, chargeRate, maxCapacity ):
        self.id = Vehicle.numVehiclesMade
        
        # keep tabs of the number of vehicles that have entered the model
        Vehicle.numVehiclesMade += 1

        # parameters for each vehicle, not all are used for each algorithm implementation
        self.arrivalTime    =   arrivalTime
        self.depTime        =   depTime
        self.chargeNeeded   =   chargeNeeded
        self.currentCharge  =   currentCharge
        self.chargeRate     =   chargeRate
        self.maxCapacity    =   maxCapacity
        timeToCharge        =   ( chargeNeeded - currentCharge ) / chargeRate #linear
        timeWindow          =   depTime - arrivalTime
        self.laxity         =   ( timeWindow - timeToCharge ) / timeToCharge

    def toString():
        print ( "ID: " , self.id ,
                "  current charge: " , self.currentCharge ,
                "  charge needed: " , self.chargeNeeded ,
                "  departure time: " , self.depTime ,
                "  laxity: ", self.laxity
            )

    #need to write this
    def updateLaxity():
        return 0

#    def getInfo(self):
#        return [self.arrivalTime, self.depTime, self.chargeNeeded, self.currentCharge, self.chargeRate, self.maxCapacity]
