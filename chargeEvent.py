# a chargingEvent is the basic object used for logging what's going on with each chargePort
# We will be using an array that's the same length of chargePorts
# each index will contain an array of chargingEvents
# the first index of this array will be the chargePort's log of the first vehicle that it dealth with
# the last index of these arrays will log the most recent chargingEvent for that specific chargePort

# to create, pass in the vehicle and currentTime
# when a vehicle is done charging, it will need the updated version of the same vehicle and again the currentTime

class chargingEvent:
	numEvents = 0

    def __init__( self, vehicle, startTime ):

        # parameters for each vehicle, not all are used for each algorithm implementation
        self.id			 		=	  chargingEvent.numEvent 
        self.startTime   		=     startTime					# the time that this vehicle began charging
        self.initialVehicle     =     vehicle 					# we wil have all the stats of our vehicle object when it entered
        self.endTime			=     -1						# update to endTime
        self.endVehicle			=     -1						# and will write its properties when it exits
        self.timeCharging       =     -1


        # keep tabs of the number of vehicles that have entered the model
        chargingEvent.numEvent += 1

    # when the vehicle is done charging, we'll gather its stats
    def terminateCharge( currentTime, vehicle ):
    	self.endTime 	    = 	currentTime
    	self.endVehicle     = 	vehicle
    	self.timeCharging   =   currentTime - self.startTime

    

