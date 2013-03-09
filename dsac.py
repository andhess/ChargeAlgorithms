import Queue
import common
import csvGen
import chargePorts
import chargeEvent
import itertools
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

	leastProfitConflict = vehicle.profit
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

		duplicate.startTime = vehicle.depTime 
		duplicate.timeToCharge -= splitVehicle.timeToCharge
		duplicate.currentCharge += splitVehicle.timeToCharge * duplicate.chargeRate

		appendedIndex = len(tempSched)
		tempSched.append(duplicate)
		tempSched.append(vehicle)

		profitChange = vehicle.profit
		for i, task in enumerate(tempSched[appendedIndex + 1:]:
			task.startTime = tempSched[i-1].startTime + tempSched[i-1].timeToCharge
			if task.startTime + task.timeToCharge <= task.depTime:
				profitChange += task.profit
			else:
				profitChange -= common.penaltyThreshold * ( task.depTime - (task.startTime + task.timeToCharge) ) * chargeRate

		if profitChange >= leastProfitConflict:
			leastProfitConflict = profitChange
			leastProfitConflictPort = index

		# brute force

def maxProfitCombination( subSchedule, newVehicle ):
	numLargerVehicles = 0
	if chargeable(vehicle) for vehicle in subSchedule:
		return subSchedule
	else:
		for index, vehicle in enumerate(subSchedule):
			if vehicle.depTime < newVehicle.startTime:
				if vehicle.profit > newVehicle.profit:
					# this means a more profitable vehicle will not be charged regardless of schedule changes
					return -1
				subSchedule.remove(index) # remove all vehilcles that will have left by this time anyway

			#keep track of larger vehicles to create a minimum permutation size for the next step
			if vehicle.profit > newVehicle.profit:
				numLargerVehicles += 1

		
		listOfSubSchedules = getAllPossibleSubSchedules(subSchedule, numLargerVehicles)

		# have to convert to tuples to add to a set
		


	# remove all vehicles that will never be able to pass to save time and RAM
	# use itertools permutations (order matters) to get all permutations (of all sizes [1...len(subSchedule -1) ] )
	# never remove vehicles larger than new vehicle (can use this to find smallest possible permuatation size)
	# for each new subschedule correct all start times
	# eliminate subschedules that fail
	# from existing passable subschedules find most profitable

def getAllPossibleSubSchedules( schedule, minSize):
	fullSet = set()
	curSet = set()
	curSet.add(schedule)
	for i in range(minSize, len(schedule)):
		permutations = itertools.permutations(curSet, i)
		curSet = set(permutations)
		for permutation in permutations:
			fullSet.add(permutation)
	return fullSet

# # recursive method to get all sub-schedules (order matters) of sizes: (n-1, n-2, ... , numLargerVehicles)
# # works by iterating through list, removing one element and finding all permutations of each smaller list
# # while recursively calling the method again on each smaller list, this method will return duplicates so that has to be checked
# def getAllPossibleSubSchedulesHelper( schedule, minSize, fullList ):
# 	if len(schedule) == minSize:
# 		return fullList
# 	else:
# 		newSubSchedules = []
# 		for index,vehicle in enumerate(schedule):
# 			schedule.remove(vehicle)
# 			for combo in itertools.permutations(schedule):
# 				newSubSchedules.append(list(combo))
# 				fullList.append(list(combo))
# 			schedule.insert(index, vehicle)
# 		for newSubSchedule in newSubSchedules:
# 			getAllPossibleSubSchedulesHelper( newSubSchedule, minSize, fullList)





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


