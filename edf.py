import common
import csvGen
import chargePorts
from operator import attrgetter

edfQueue = []

#  ------ EDF ------

earliestDLIndex = -1;

# the main function for Earliest Deadline First Algorithm
# takes in an array of vehicle interval arrays
def simulateEDF( arrayOfVehicleArrivals ):
    
    # reset global variables such as time, done/failed lots
    common.updateGlobals()
    global currentTime
    global earliestDLIndex

    # initialize a CSV document for storing all data
    csvGen.generateCSV( "edf" )

    # iterate through each vehicle in each minute
    for minute, numVehiclesPerMin in enumerate( arrayOfVehicleArrivals ):
        for vehicle in numVehiclesPerMin:
            port = chargePorts.openChargePort()

            if port is not None:
                chargePorts.chargePorts[ port ] = vehicle
            else:
                edfQueue.append( vehicle )
                if earliestDLIndex == -1 or vehicle.depTime < edfQueue[ earliestDLIndex ].depTime:
                    earliestDLIndex = len( edfQueue ) - 1
        updateVehiclesEDF()
        common.currentTime += 1

    # vehicles done arriving, now continue with the simulation
    while chargePorts.chargePortsEmpty() == False or not len( edfQueue ) == 0:
        updateVehiclesEDF()
        common.currentTime += 1

    print "EDF: total number of cars: ", common.numberOfVehiclesInSimulation , \
          "  elapsed time: " , common.currentTime , \
          "  done charging lot: " , len( common.doneChargingLot ) , \
          "  failed charging lot: " , len( common.failedLot ) , \
          "  edfQueue size:  " , len( edfQueue ) , \
          "  chargePort " , chargePorts.toString()


# called to update the vehicles for each minute of simulation
def updateVehiclesEDF():
    global earliestDLIndex
    global latestChargePortDLIndex


    # update chargePortCSV
    csvGen.exportChargePortsToCSV()

    # cheack each chargePort
    for index, vehicle in enumerate( chargePorts.chargePorts ):

        # add one minute of charge
        if vehicle is not None:
            vehicle.currentCharge += ( vehicle.chargeRate ) / 60
            removed = False

            #check if done charging
            if vehicle.currentCharge >= vehicle.chargeNeeded:
                csvGen.exportVehicleToCSV( vehicle, "SUCCESS" )
                common.doneChargingLot.append( vehicle )
                
                if len( edfQueue ) > 0:
                    chargePorts.chargePorts[ index ] = edfQueue[ earliestDLIndex ]
                    del edfQueue[ earliestDLIndex ]  
                    earliestDLIndex = earliestDL()
                else:
                    chargePorts.chargePorts[ index ] = None
                removed = True

            # check if deadline reached
            if common.currentTime >= vehicle.depTime and not removed:
                csvGen.exportVehicleToCSV( vehicle, "FAILURE" )
                common.failedLot.append( vehicle )
                
                if len( edfQueue ) > 0:
                    chargePorts.chargePorts[ index ] = edfQueue[ earliestDLIndex ]
                    del edfQueue[ earliestDLIndex ]
                    earliestDLIndex = earliestDL()
                else:
                    chargePorts.chargePorts[ index ] = None


    # now we want to make sure that all the cars in the chargePorts are the best choices
    # we want to know the index of the worst car charging and compare that to the index of the best in the queue
    # also need to be able to cycle the queue so that it will put ALL the cars in the queue that are better into the chargePorts

    # edge cases to worry about: queue is empty, earliestDLIndex = -1

    # start out by grabbing the latest chargePort
    latestChargePortDLIndex = latestChargePortDL()
    
    # prioritize edge cases, loop until swap the top DL are all in the queue
    while len( edfQueue ) > 0 and latestChargePortDLIndex != -1 and edfQueue[ earliestDLIndex ].depTime < chargePorts.chargePorts[ latestChargePortDLIndex ].depTime:
                        
        # make a swap
        temp = chargePorts.chargePorts[ latestChargePortDLIndex ]
        chargePorts.chargePorts[ latestChargePortDLIndex ] = edfQueue[ earliestDLIndex ]
        edfQueue[ earliestDLIndex ] = temp

        # now update values for comparison
        earliestDLIndex = earliestDL()
        latestChargePortDLIndex = latestChargePortDL()

        # NOTE: we are explicitly choosing to grab a clean version of each index because accuracy cannot be guaranteed

# gets the index of earliest deadline of all the vehicles in edfQueue
def earliestDL():
    if len( edfQueue ) == 0:
        return -1
    return edfQueue.index( min( edfQueue, key = attrgetter( 'depTime' ) ) )

# gets the index of the vehicle in chargePorts with the latest deadline 
def latestChargePortDL():
    latestIndex = -1
    latestTime = -1
    for index, port in enumerate( chargePorts.chargePorts ):
        if port is not None:
            if port.depTime > latestTime:
                latestTime = port.depTime
                latestIndex = index
    return latestIndex  


