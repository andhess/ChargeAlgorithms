import Queue
import common
import csvGen
import chargePorts
import chargeEvent
import copy

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
					vehicle.startTime = vehicle.depTime - vehicle.timeToCharge
					
					# least profit conflict



def leastProfitConflict( vehicle ):

	profitGained = 0
	leastProfitConflictPort = -1

	# iterate through each schedule
	for index, schedulePort in enumerate( schedules ):

		# make a temporary one since we'll be messing with this
		tempSched = copy.deepcopy(schedulePort)

		cutoffTime = vehicle.depTime - vehicle.timeToCharge

		# loop through all the scheduled tasks
		# looking for the car that cutOff time interrupts
		splitVehicleIndex = len( tempSched ) - 1

		while splitVehicleIndex >=0 and tempSched[ splitVehicleIndex ].startTime > vehicle.startTime:
			splitVehicleIndex += 1

		splitVehicle = schedulePort[ splitVehicleIndex ]

		duplicate = Vehicle.duplicate(splitVehicle) # represents the second half of the split vehicle	
		
		splitVehicle.timeToCharge = vehicle.startTime - splitVehicle.startTime

		# need to create a list of all vehicles (including the one that is split)
		# that gets appended to the end of the schedule

		duplicate.startTime = tempSched[ len(tempSched)-1 ].depTime # duplicate will be appended to the end of the schedule 
		duplicate.timeToCharge -= splitVehicle.timeToCharge
		duplicate.currentCharge += splitVehicle.timeToCharge * duplicate.chargeRate

		pushToEnd = [] # represents the part of the schedule that the new vehicle is kicking out
		pushToEnd.append(duplicate)

		#need to split the second vehicle that the new vehicle overlaps partially 

		secondSplitVehicleIndex = splitVehicleIndex + 1 # the index after the first split vehicle

		while secondSplitVehicleIndex < len(tempSched): 
			if tempSched[secondSplitVehicleIndex].startTime + tempSched[secondSplitVehicleIndex].timeToCharge > vehicle.depTime:
				break
			secondSplitVehicleIndex += 1

		if secondSplitVehicleIndex < len(tempSched):	
			secondSplitVehicle = tempSched[ secondSplitVehicleIndex ]

			duplicateSecondSplitVehicle = copy.deepcopy( secondSplitVehicle ) # represents second part of split vehicle

			duplicateSecondSplitVehicle.startTime = vehicle.depTime
			duplicateSecondSplitVehicle.timeToCharge -= vehicle.depTime

			# this will eventually be after duplicateSecondSplitVehicle in the schedule
			secondSplitVehicle.timeToCharge -= duplicateSecondSplitVehicle.timeToCharge
			secondSplitVehicle.currentCharge += duplicateSecondSplitVehicle.timeToCharge * secondSplitVehicle.chargeRate

			pushToEnd.append( duplicateSecondSplitVehicle )
			# pushToEnd now containts the 2nd half of the first split vehicle and the 1st half of the second split vehicle

		# now move everything that the new vehicle kicks out to the end of the list
		# first put the overlapped part into pushToEnd after the first split part and before the second split part (if it exists)
		pushToEnd[1:1] = tempSched[splitVehicleIndex + 1: secondSplitVehicleIndex] 

		# then delete the remove the overlapped part, add in the new vehicle and append the overlapped part to then end
		del tempSched[splitVehicleIndex+1 : secondSplitVehicleIndex] # remove the overlapped part of the list

		tempSched.insert(splitVehicleIndex + 1, vehicle)  # insert the new vehicle after split vehicle

		startOfMovedTasks = len(tempSched)

		tempSched += pushToEnd # move the ovelapped part to the end

		# update all start times
		for taskIndex, task in enumerate(tempSched[1:]):
			prevTask = tempSched[ taskIndex - 1 ]
			task.startTime = prevTask.startTime + prevTask.timeToCharge


		# now that tempSched is has been updated with the new vehicle and the overlapped part pushed to the end
		# check to see if the profit is better by checking if the 'pushed to end' tasks are finishable before their deadlines

		profitGained = vehicle.profit

		for task in tempSched[startOfMovedTasks:]
			if 












def chargeable( vehicle ):
	return (vehicle.depTime >= vehicle.startTime + vehicle.timeToCharge)

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


