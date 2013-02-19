from chargePorts import resetChargePorts
# ---- storage lots ------

doneChargingLot = []
failedLot = []

numberOfVehiclesInSimulation = 0

# ----- global time vars ------
currentTime = 0 
interval = 0

def setInterval( newInterval ):
	global interval
	interval = newInterval

def setNumberOfVehiclesInSimulation( n ):
	global numberOfVehiclesInSimulation
	numberOfVehiclesInSimulation = n

# function to reset time, failed/done lots etc. Called at start of every algorithm simlulation
def updateGlobals():
    global currentTime
    currentTime = 0
    global doneChargingLot
    doneChargingLot = []
    global failedLot
    failedLot = []
    resetChargePorts()

def vehicleIdsInList( list, highlight):
	output = "["
	for index, item in enumerate(list):
		if index == highlight:
			output += "***"
		if item is not None:
			output += str(item.id)
		else:
			output += "None"
		if index != len( list ) - 1:
			output += ", "
	output += "]"
	return output

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









