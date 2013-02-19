# charge port constants
numChargePorts = 3
chargePorts = [ None ] * numChargePorts
chargePortListeners = [ ]

# setup the chargePortListeners data structure
for i in range( numChargePorts ):
    chargePortListeners.append( [  ] )

chargePortListeners[ 2 ].append( 12 )
chargePortListeners[ 2 ].append( 7 )
chargePortListeners[ 2 ].append( 5 )
chargePortListeners[ 0 ].append( 3 )
chargePortListeners[ 2 ].append( 3 )
chargePortListeners[ 2 ].append( 0 )
chargePortListeners[ 1 ].append( 1 )
chargePortListeners[ 1 ].append( 5 )
chargePortListeners[ 1 ].append( 3 )
chargePortListeners[ 2 ].append( 3 )
chargePortListeners[ 0 ].append( 4 )
chargePortListeners[ 0 ].append( 9 )
chargePortListeners[ 2 ].append( 3 )
chargePortListeners[ 1 ].append( 2 )
chargePortListeners[ 2 ].append( 3 )

print "listener object  " ,  chargePortListeners

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