# a chargingEvent is the basic object used for logging what's going on with each chargePort
# We will be using an array that's the same length of chargePorts
# each index will contain an array of chargingEvents
# the first index of this array will be the chargePort's log of the first vehicle that it dealth with
# the last index of these arrays will log the most recent chargingEvent for that specific chargePort

# to create, pass in the vehicle and currentTime
# when a vehicle is done charging, it will need the updated version of the same vehicle and again the currentTime

# readouts of -1 for endTime, endVehicle, and elapsedTime will denote that it's either still listening or something went very wrong

import vehicle

class ChargeEvent:
	numEvents = 0

    def __init__( self, vehicle, startTime ):

        # parameters for each vehicle, not all are used for each algorithm implementation
        self.id			 		=	  chargingEvent.numEvents 
        self.startTime   		=     startTime					# the time that this vehicle began charging
        self.initialVehicle     =     vehicle 					# we wil have all the stats of our vehicle object when it entered
        self.endTime			=     -1						# update to endTime
        self.endVehicle			=     -1						# and will write its properties when it exits
        self.elapsedTime        =     -1
        self.endVehicle			=     -1						# will write its properties when it exits
        self.timeCharging       =     -1


        # keep tabs of the number of vehicles that have entered the model
        chargingEvent.numEvents += 1

    # when the vehicle is done charging, we'll gather its stats
    def terminateCharge( self, vehicle, currentTime ):
    	self.endTime 	    = 	currentTime
    	self.endVehicle     = 	vehicle
    	self.elapsedTime   =   currentTime - self.startTime

    # probably useful to have
    def toString( self ):

    	vehicleEnd = "No endVehicle"

    	if self.endVehicle != -1:
    		vehicleEnd = self.endVehicle.toString()

        body =  "ID: " , self.id , \
        		"  starting time : " , self.startTime , \
              	"  initial vehicle properties : " , self.initialVehicle.toString() , \
              	"  ending time : " , self.endTime , \
              	"  ending vehicle properties : " , vehicleEnd , \
              	"  elapsedTime : " , self.elapsedTime

        return body

    # this will be a line in the CSV file, just have writerow jot down this stuff
    # FIXME: add some vehicle properties like chargeReceived, etc
    def csvPrep():
    	row = [ self.id , \
                self.startTime , \
                self.endTime , \
                self.timeCharging , \
              ]
        return row

