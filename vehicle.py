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
        timeToCharge        =   ( chargeNeeded - currentCharge ) / chargeRate  #linear
        totalTime           =   depTime - arrivalTime
        freeTime            =   totalTime - timeToCharge
        self.laxity         =   freeTime / totalTime

    def toString():
        print ( "ID: " , self.id ,
                "  current charge: " , self.currentCharge ,
                "  charge needed: " , self.chargeNeeded ,
                "  departure time: " , self.depTime ,
                "  laxity: ", self.laxity
            )

    # updates the laxity for vehicle. Requires the current time of the simulation
    def updateLaxity( currentTime ):
        timeToCharge =  ( self.chargeNeeded - self.currentCharge ) / self.chargeRate
        totalTime    =  self.depTime - currentTime
        freeTime     =  totalTime - timeToCharge
        self.laxity  =  freeTime / totalTime


#    def getInfo(self):
#        return [self.arrivalTime, self.depTime, self.chargeNeeded, self.currentCharge, self.chargeRate, self.maxCapacity]
