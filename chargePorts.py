# charge port constants
numChargePorts = 5
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