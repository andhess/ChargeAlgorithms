import Queue
import common
import csvGen
import chargePorts
import chargeEvent

#fcfs
schedules = [ [ ] for y in range( chargePorts.numChargePorts ) ]


# ------ FCFS ------

# the main implementation of the First Come First Serve algorithm
# takes in an array of arrays of vehicle minutes ( 2-level )
def simulateFCFS( arrayOfVehicleArrivals ):
	
	# reset global variables such as time, done/failed lots
	common.updateGlobals( arrayOfVehicleArrivals )
	global currentTime

	# initialize a CSV document for storing all data
	csvGen.generateCSV( "fcfs" )

	# iterate through each vehicle in each minute
	for minute, numVehiclesPerMin in enumerate( arrayOfVehicleArrivals ):
		for vehicle in numVehiclesPerMin:       
			port = chargePorts.openChargePort()

			if vehicle.currentCharge > vehicle.chargeNeeded:
				csvGen.exportVehicleToCSV( vehicle, "Charge Not Needed" )
				common.cantChargeLot.append( vehicle )
				continue

			# a port is open so start charging the vehicle
			if port is not None:

				# add to chargePort
				chargePorts.chargePorts[ port ] = vehicle
				schedules[ port ].append(vehicle)
			
				# initialize a listener object for its charging activity
				chargePorts.chargePortListeners[ port ].insert( 0 , chargeEvent.ChargeEvent( vehicle, common.currentTime ) )
				
			# no ports are available so put the vehicle in the queue
			else:
				# queue.put( vehicle )

				bestPortInfo = findEarliestEndingSchedule()
				bestPortIndex = bestPortInfo[0]	# index
				bestPortEndTime = bestPortInfo[1] #end time

				# vehicle declined
				if vehicle.depTime - bestPortEndTime < vehicle.timeToCharge:
					csvGen.exportVehicleToCSV( vehicle, "DECLINED" )
					common.declinedLot.append( vehicle )

				# vehicle appended
				else:
					schedules[ bestPortIndex ].appended( vehicle )
		updateVehiclesFCFS()
		common.currentTime += 1

	# print "status:  " , openChargePort() , "  " , queue.empty()
	
	# run the clock until all vehicles have ran through the simulation
	while chargePorts.chargePortsEmpty() == False or not queue.empty():
		updateVehiclesFCFS()
		common.currentTime += 1

	# print "FCFS: total number of cars: ", common.numberOfVehiclesInSimulation , \
	#       "  elapsed time: " , common.currentTime , \
	#       "  done charging lot: " , len( common.doneChargingLot ) , \
	#       "  failed charging lot: " , len( common.failedLot ) , \
	#       "  cant charge lot: " , len( common.cantChargeLot ) , \
	#       "  fcfsQueue size:  " , queue.qsize() , \
	#       "  chargePort " , chargePorts.toString()

	# write a CSV for all the chargePort logs
	csvGen.exportChargePortsToCSV( "fcfs" )

	return ( 1.0 * len( common.doneChargingLot ) / common.numberOfVehiclesInSimulation )

# called to update the vehicles for each minute of simulation
def updateVehiclesFCFS():

	# check each chargePort
	for index, vehicle in enumerate( chargePorts.chargePorts ):        

		# add 1 minute of charge
		if vehicle is not None:
			vehicle.currentCharge +=  ( vehicle.chargeRate ) / 60.0
			removed = False;

			# check if done charging
			if vehicle.currentCharge >= vehicle.chargeNeeded:

				# this vehicle is on the out, so wrap up its listener
				chargePorts.chargePortListeners[ index ][ 0 ].terminateCharge( vehicle , common.currentTime )

				# remove finished vehicle from grid and document it
				csvGen.exportVehicleToCSV( vehicle, "SUCCESS" )
				common.doneChargingLot.append( vehicle )
				del schedules[ index ][ 0 ] # remove the vehicle for the schedule
				
				# the next vehicle
				if len(schedules[ index ]) != 0:

					nextVehicle = schedules[ index ][ 0 ]
					chargePorts.chargePorts[ index ] = nextVehicle

					# and then make a new listener
					chargePorts.chargePortListeners[ index ].insert( 0 , chargeEvent.ChargeEvent( nextVehicle , common.currentTime ) )

				else:
					chargePorts.chargePorts[ index ] = None
				removed = True;


			# check if deadline reached, should never happen with admission control           
			if common.currentTime >= vehicle.depTime and not removed:

				# this vehicle is on the out, so wrap up its listener
				chargePorts.chargePortListeners[ index ][ 0 ].terminateCharge( vehicle , common.currentTime )
				
				# remove finished vehicle from grid and document it
				csvGen.exportVehicleToCSV( vehicle, "FAILURE" )               
				common.failedLot.append( vehicle )
				
				# the next vehicle
				if len(schedules[ index ]) != 0:

					nextVehicle = schedules[ index ][ 0 ]
					chargePorts.chargePorts[ index ] = nextVehicle

					# and then make a new listener
					chargePorts.chargePortListeners[ index ].insert( 0 , chargeEvent.ChargeEvent( nextVehicle , common.currentTime ) )

				else:
					chargePorts.chargePorts[ index ] = None

def findEarliestEndingSchedule():
	earliestIndex = -1;
	earliestEndTime = float("inf");
	for index, portSchedule in enumerate(schedules):
		length = len(portSchedule);
		if lastIndex == 0:
			return index
		endTime = portSchedule[0].timeLeftToCharge()	# this car is already in the chargePort and may have started charging
		for i in range (1, length):
			endtime += portSchedule[i].timeToCharge
		if endtime < earliestEndTime:
			earliestIndex = index
			earliestEndTime = endtime
	return ( earliestIndex, earliestEndTime )











