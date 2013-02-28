import chargeEvent
# charge port constants
numChargePorts = 3
chargePorts = [ None ] * numChargePorts
chargePortListeners = [ ]

# setup the chargePortListeners data structure
for i in range( numChargePorts ):
    chargePortListeners.append( [  ] )

# print "listener object  " ,  chargePortListeners

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

def addChargeEvent( portNum, vehicle, time ):
    chargeEvents[ portNum ] = chargeEvent.ChargeEvent(vehicle, time)

def terminateChargeEvent( portNum, vehicle, time ):
    mostRecentChargeEvent = len(chargeEvents[ portNum ]) - 1
    chargeEvents[ portNum ][ mostRecentChargeEvent ].terminateChargeEvent( vehicle, time )


# visualization of vehicle ids in chargeports
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