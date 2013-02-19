# charge port constants
numChargePorts = 3
chargePorts = [ None ] * numChargePorts
chargePortListeners = [ None ] * numChargePorts

# reset the charge ports array, to be used in updateGlobals() in poissonGen.py
def resetChargePorts():
	chargePorts = [ None ] * numChargePorts

# returns open charge port ( if any )
def openChargePort():
    for index, port in enumerate( chargePorts ):
        if port is None:
            return index
    return None

# says if all charge ports are empty
def chargePortsEmpty():
	return all( port is None for port in chargePorts )


# visualization of vehicle ids in chargeporst
def toString():
    output = "["
    for index, vehicle in enumerate(chargePorts):
        if vehicle is None:
            output += "None"
        else:
            output += str( vehicle.id )
        if index != len( chargePorts ) - 1:
            output += ", "
    output += "]"
    return output