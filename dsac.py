import Queue
import common
import csvGen
import chargePorts
import chargeEvent

schedules = [[]] * chargePorts.numChargePorts

def simulateDSAC( arrayOfVehicleArrivals ):

	# reset global variables such as time, done/failed lots
	common.updateGlobals()
	global currentTime

	# initialize a CSV document for storing all data
	csvGen.generateCSV( "dsac" )


	# iterate through each vehicle in each minute
	for minute, numVehiclesPerMin in enumerate( arrayOfVehicleArrivals ):
		for vehicle in numVehiclesPerMin:   
			port = chargePorts.openChargePort()

			# a port is open so start charging the vehicle
			if port is not None:

				# add to chargePort
				chargePorts.chargePorts[ port ] = vehicle
			
				# initialize a listener object for its charging activity
				chargePorts.chargePortListeners[ port ].insert( 0 , chargeEvent.chargingEvent( vehicle, common.currentTime ) )
                
			# no ports are available so put the vehicle in the queue
			else:

				# any appendables?
				appendable = findAppendableChargePort( vehicle )

				# add to schedule
				if appendable != -1:
					tempVehicle = schedules[ appendable ][ len( schedules[ appendable ] - 1 ) ]
					newStartTime = tempVehicle.startTime + tempVehicle.timeToCharge + 1
					vehicle.updateStartTime( newStartTime )
					schedules[ appendable ].append( vehicle )

				# an ugly conflict
				else:
					# least profit conflict

def leastProfitConflict( vehicle ):

	leastProfitConflict = vehicle.profit

	# iterate through each schedule
	for index, schedulePort in enumerate( schedules ):

		# make a temporary one since we'll be messing with this
		tempSched = schedulePort

		cutoffTime = vehicle.depTime - vehicle.timeToCharge

		# loop through all the scheduled tasks
		# looking for the car that cutOff time interrupts
		splitVehicleIndex = len( tempSched ) - 1

		while splitVehicleIndex >=0 and tempSched[ splitVehicleIndex ].startTime > vehicle.startTime:
			splitVehicleIndex += 1

		# split vehicle

		# make 2 "halves" of that vehicle.  duplicate it -> write a duplicate vehicle in vehicle.pyg

		# splice the vehilce in between the two halves
		# this split is going to be where the start time is

		# brute force



def updateVehicles():
	pass


# iterate through all schedules
# returns the index (if possible) of the schedule that will be able to
# accommodate a vehicle within it's deadline with the least amount of extra window
# returns -1 if none are possible
def findAppendableChargePort( vehicle ):
	 tightestWindow = -1

	 bestWindow = vehicle.deadline - currentTime

	# iterate througbh each schedule
	for index, portSchedule in enumerate( schedules ):

		# look at last vehicle in each schedule
		currentWindow = vehicle.depTime - scheduleEndTime( index )

		# is this window large enough to charge vehicle, and is it more optimal
		if currentWindow > vehicle.timeToCharge and currentWindow < bestWindow:
			bestWindow = currentWindow
			tightestWindow = index

	return tightestWindow


# gets the departure time for the last vehicle in a schedule
def scheduleEndTime( scheduleIndex ):
	lastItem = len( schedules[ scheduleIndex ] ) - 1
	
	if lastItem != -1:
		return schedules[ scheduleIndex ][ lastItem ].depTime

	# should never happen, make it break
	return false


