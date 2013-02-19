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
        self.initialCharge  =   currentCharge
        self.chargeRate     =   chargeRate
        self.maxCapacity    =   maxCapacity
        self.timeToCharge   =   ( chargeNeeded - currentCharge ) / chargeRate  #linear
        self.totalTime      =   depTime - arrivalTime
        self.freeTime       =   self.totalTime - self.timeToCharge
        self.laxity         =   self.freeTime / self.totalTime
        self.originalLaxity  =   self.freeTime / self.totalTime

    def toString( self ):
        body =  "ID: " , self.id , \
                "  current charge: " , self.currentCharge , \
                "  charge needed: " , self.chargeNeeded , \
                "  departure time: " , self.depTime , \
                "  laxity: ", self.laxity
        return body

    # updates the laxity for vehicle. Requires the current time of the simulation
    def updateLaxity( self, currentTime ):
        timeToCharge =  ( self.chargeNeeded - self.currentCharge ) / self.chargeRate
        totalTime    =  self.depTime - currentTime
        freeTime     =  totalTime - timeToCharge

        # in case time ends up, we can't divide by 0
        if totalTime == 0:
            self.laxity = 1
        else:
            self.laxity  =  freeTime / totalTime


#    def getInfo(self):
#        return [self.arrivalTime, self.depTime, self.chargeNeeded, self.currentCharge, self.chargeRate, self.maxCapacity]
