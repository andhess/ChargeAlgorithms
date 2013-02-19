import common
import csvGen
import chargePorts
from operator import attrgetter

llfSimpleQueue = []

#  ------ LLF SIMPLE --------
# This algorithm runs under the same premise as the other LLF algorithm except in this instance laxity is only computed once
# upon arrival
# laxity is still defined as freeTime/totalTime where freeTime = (departure - arrival - chargeTime) and totalTime = (departure - arrival) 
# However, since laxity is only calculated once, if a car has a small laxity there is a good chance that it will never be charged 

llfSimpleIndex = -1

def simulateLLFSimple( arrayOfVehicleArrivals ):
    
    # reset global variables such as time, done/failed lots
    common.updateGlobals()
    global currentTime
    global llfSimpleIndex

    # initialize a CSV document for storing all data
    csvGen.generateCSV( "llfSimple" )

    # iterate through each vehicle in each minute
    for minute, numVehiclesPerMin in enumerate( arrayOfVehicleArrivals ):
        for vehicle in numVehiclesPerMin:
            port = chargePorts.openChargePort()

            # there is an open chargePort, add vehicle to it
            if port is not None:
                chargePorts.chargePorts[ port ] = vehicle

            # no open chargePort, append to llfQueue
            else:

                llfSimpleQueue.append( vehicle )

                # update the llfIndex if this vehicle is better
                if llfSimpleIndex == -1 or vehicle.laxity < llfSimpleQueue[ llfSimpleIndex ].laxity:
                    llfSimpleIndex = len( llfSimpleQueue ) - 1

        updateVehiclesLLFSimple()
        common.currentTime += 1

    # vehicles done arriving, now continue with the simulation
    while chargePorts.chargePortsEmpty() == False or len( llfSimpleQueue ) != 0:
        updateVehiclesLLFSimple()
        common.currentTime += 1

    print "LLF Simple: total number of cars: ", common.numberOfVehiclesInSimulation , \
          "  elapsed time: " , common.currentTime , \
          "  done charging lot: " , len( common.doneChargingLot ) , \
          "  failed charing lot: " , len( common.failedLot ) , \
          "  llfQueue size:  " , len( llfSimpleQueue ) , \
          "  chargePort " , chargePorts.toString()
        

# called to update the vehicles for each minute of simulation
def updateVehiclesLLFSimple():
    global currentTime
    global llfSimpleIndex

    # update chargePortCSV
    csvGen.exportChargePortsToCSV()

    # increment the charge for the cars that were charging
    for index, vehicle in enumerate( chargePorts.chargePorts ):

        # add one minute of charge
        if vehicle is not None:
            vehicle.currentCharge += ( vehicle.chargeRate ) / 60

    # now move cars around so the laxity property is maintained
    for index, vehicle in enumerate( chargePorts.chargePorts ):
        if vehicle is not None:
            removed = False

            #check if done charging
            if vehicle.currentCharge >= vehicle.chargeNeeded:
                csvGen.exportVehicleToCSV( vehicle, "SUCCESS" )
                common.doneChargingLot.append( vehicle )
                
                if len( llfSimpleQueue ) > 0:
                    chargePorts.chargePorts[ index ] = llfSimpleQueue[ llfSimpleIndex ]
                    del llfSimpleQueue[ llfSimpleIndex ]  
                    llfSimpleIndex = lowestLaxity()
                else:
                    chargePorts.chargePorts[ index ] = None
                removed = True
            
            

            # check if deadline reached
            if common.currentTime >= vehicle.depTime and not removed:
                csvGen.exportVehicleToCSV( vehicle, "FAILURE" )
                common.failedLot.append( vehicle )
        
                if len( llfSimpleQueue ) > 0:
                    chargePorts.chargePorts[ index ] = llfSimpleQueue[ llfSimpleIndex ]
                    del llfSimpleQueue[ llfSimpleIndex ]
                    llfSimpleIndex = lowestLaxity() # function defined in LLF section, iterates through llfQueue for lowest laxity
                else:
                    chargePorts.chargePorts[ index ] = None

            highestLaxityChargePortIndex = highestLaxityChargePort()

            # check if all cars in chargePorts still have lowest laxity
            while len( llfSimpleQueue ) > 0 and highestLaxityChargePortIndex != -1 and llfSimpleQueue[ llfSimpleIndex ].laxity > chargePorts.chargePorts[ highestLaxityChargePortIndex ].laxity:

                # make a swap
                temp = chargePorts.chargePorts[ highestLaxityChargePortIndex ]
                chargePorts.chargePorts[ highestLaxityChargePortIndex ] = llfSimpleQueue[ llfSimpleIndex ]
                llfSimpleQueue[ llfSimpleIndex ] = temp

                # now update values for comparison
                llfSimpleIndex = lowestLaxity()
                highestLaxityChargePortIndex = highestLaxityChargePort()


# gets index for the vehicle with the lowest laxity from llf
def lowestLaxity():
    if len( llfSimpleQueue ) == 0:
        return - 1
    return llfSimpleQueue.index( min( llfSimpleQueue, key = attrgetter( 'laxity' ) ) )

# finds the chargePort with the highest laxity
def highestLaxityChargePort():
    highestLaxityIndex = -1
    highestLaxity = -1
    for index, port in enumerate( chargePorts.chargePorts ):
        if port is not None:
            if port.laxity > highestLaxity:
                highestLaxity = port.laxity
                highestLaxityIndex = index
    return highestLaxityIndex  

