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




def findAppendableChargePort():
	
