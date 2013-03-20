from chargePorts import resetChargePorts, resetChargePortListeners
import vehicle

# ---- storage lots ------

doneChargingLot = []
failedLot = []

# adding a lot of cars that don't need to be charged
# might help when we're trying to pick distribution values
cantChargeLot = []

numberOfVehiclesInSimulation = 0

# ----- global time vars ------
currentTime = 0 
interval = 0

# -------- price per kilowatt*hour -------
electricityPrice = .1   # in dollars
penaltyThreshold = .8	# ratio of how much charging costs vs how much the penalty is worth

# used in main.py to set the common interval variable
def setInterval( newInterval ):
	global interval
	interval = newInterval

def setNumberOfVehiclesInSimulation( n ):
	global numberOfVehiclesInSimulation
	numberOfVehiclesInSimulation = n

# function to reset time, failed/done lots etc. Called at start of every algorithm simlulation
def updateGlobals( arrayOfVehicleArrivals ):
    global currentTime
    currentTime = 0
    global doneChargingLot
    doneChargingLot = []
    global failedLot
    failedLot = []
    global cantChargeLot
    cantChargeLot = []
    resetChargePorts()	# function in chargePorts.py to empty all chargePorts
    resetChargePortListeners()
    
    # reset charge for each vehicle
    for minute, numVehiclesPerMin in enumerate( arrayOfVehicleArrivals ):
        for vehicle in numVehiclesPerMin:
        	vehicle.resetVehicleCharge()


# returns string representation of all vehicles in a list by id in form [0,1,2,3,4...] 
# with one id highlighted which is useful for viewing llfIndex or earliestDLIndex, etc
# pass in -1 for highlight for no highlight
def vehicleIdsInList( list, highlight ):
	output = "["
	for index, item in enumerate( list ):
		if index == highlight:
			output += "***"
		if item is not None:
			output += str( item.id )
		else:
			output += "None"
		if index != len( list ) - 1:
			output += ", "
	output += "]"
	return output

# returns string representation of all vehicles in 2d array, most notably simulationInterval in main.py
def vehicleIdsIn2DList( list ):
	output = "["
	count = 0
	for row in list:
		if row is not None:
			for item  in row:
				if item is not None:
					output += str(item.id)
					count += 1
					if count != numberOfVehiclesInSimulation:
						output += ", "
	output += "]"
	return output
