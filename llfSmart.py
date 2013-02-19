import common
import csvGen
import chargePorts
from operator import attrgetter

llfQueue = []


#  ------ LLF ------

# laxity is defined as freeTime/totalTime where freeTime = (departure - arrival - chargeTime) and totalTime = (departure - arrival) initially )
# laxity needs to be updated each minute where freeTime = ( departure - current time - chargeTime ) and totalTime = ( departure - currentTime )
# 
# for both cases, caluclate totalTime, then free time will just be totalTime - chargeTime.
#
# this is going to work pretty much the same way as EDF, only difference is we need to constantly update the laxity values of each vehicle
# however we are still hanging on to the same index deal as before
#
#    total time =   departure time - current time
#    free time  =  total time - timeToCharge

llfIndex = -1

def simulateLLF( arrayOfVehicleArrivals ):
    
    # reset global variables such as time, done/failed lots
    common.updateGlobals()
    global currentTime
    global llfIndex

    # initialize a CSV document for storing all data
    csvGen.generateCSV( "llfSmart" )

    # iterate through each vehicle in each minute
    for minute, numVehiclesPerMin in enumerate( arrayOfVehicleArrivals ):
        for vehicle in numVehiclesPerMin:
            port = chargePorts.openChargePort()

            # there is an open chargePort, add vehicle to it
            if port is not None:
                chargePorts.chargePorts[ port ] = vehicle

            # no open chargePort, append to llfQueue
            else:
                llfQueue.append( vehicle )

                # update the llfIndex if this vehicle is better
                if llfIndex == -1 or vehicle.laxity < llfQueue[ llfIndex ].laxity:
                    llfIndex = len( llfQueue ) - 1

        updateVehiclesLLF()
        common.currentTime += 1

    # vehicles done arriving, now continue with the simulation
    while chargePorts.chargePortsEmpty() == False or not len( llfQueue ) == 0:
        updateVehiclesLLF()
        common.currentTime += 1

    print "LLF Complex:  total number of cars: ", common.numberOfVehiclesInSimulation , \
          "  elapsed time: " , common.currentTime , \
          "  done charging lot: " , len( common.doneChargingLot ) , \
          "  failed charging lot: " , len( common.failedLot ) , \
          "  llfQueue size:  " , len( llfQueue ) , \
          "  chargePort " , chargePorts.toString()
        

# called to update the vehicles for each minute of simulation
def updateVehiclesLLF():
    global currentTime
    global llfIndex

    # update chargePortCSV
    csvGen.exportChargePortsToCSV()

    # increment the charge for the cars that were charging
    for index, vehicle in enumerate( chargePorts.chargePorts ):

        # add one minute of charge
        if vehicle is not None:
            vehicle.currentCharge += ( vehicle.chargeRate ) / 60

            # print "Charge:  " , vehicle.currentCharge , "   " , vehicle.chargeNeeded
            # print "Timing:  " , currentTime , "   ",  vehicle.depTime 
    
    # update the laxity for all the peeps
    updateLaxityForAll()

    # now move cars around so the laxity property is maintained
    for index, vehicle in enumerate( chargePorts.chargePorts ):
        if vehicle is not None:
            removed = False

            #check if done charging
            if vehicle.currentCharge >= vehicle.chargeNeeded:
                csvGen.exportVehicleToCSV( vehicle, "SUCCESS" )
                common.doneChargingLot.append( vehicle )
                
                if len( llfQueue ) > 0:
                    chargePorts.chargePorts[ index ] = llfQueue[ llfIndex ]
                    del llfQueue[ llfIndex ]  
                    llfIndex = lowestLaxity()
                else:
                    chargePorts.chargePorts[ index ] = None
                removed = True

            # check if deadline reached
            if common.currentTime >= vehicle.depTime and not removed:
                csvGen.exportVehicleToCSV( vehicle, "FAILURE" )
                common.failedLot.append( vehicle )
                
                if len( llfQueue ) > 0:
                    chargePorts.chargePorts[ index ] = llfQueue[ llfIndex ]
                    del llfQueue[ llfIndex ]
                    llfIndex = lowestLaxity()
                else:
                    chargePorts.chargePorts[ index ] = None

            highestLaxityChargePortIndex = highestLaxityChargePort()

            # check if all cars in chargePorts still have lowest laxity
            while len( llfQueue ) > 0 and highestLaxityChargePortIndex != -1 and llfQueue[ llfIndex ].laxity > chargePorts.chargePorts[ highestLaxityChargePortIndex ].laxity:

                # make a swap
                temp = chargePorts.chargePorts[ highestLaxityChargePortIndex ]
                chargePorts.chargePorts[ highestLaxityChargePortIndex ] = llfQueue[ llfIndex ]
                llfQueue[ llfIndex ] = temp

                # now update values for comparison
                llfIndex = lowestLaxity()
                highestLaxityChargePortIndex = highestLaxityChargePort()

# gets index for the vehicle with the lowest laxity from llf
def lowestLaxity():
    if len( llfQueue ) == 0:
        return -1
    return llfQueue.index( min( llfQueue, key = attrgetter( 'laxity' ) ) )

# finds the chargePort with the highest laxity
def highestLaxityChargePort():
    highestLaxityIndex = -1
    highestLaxity = -1
    for index, port in enumerate(chargePorts.chargePorts):
        if port is not None:
            if port.laxity > highestLaxity:
                highestLaxity = port.laxity
                highestLaxityIndex = index
    return highestLaxityIndex  

# laxity constantly changes as time advances and certain cars are charged
def updateLaxityForAll():

    # first do chargePorts
    for index, vehicle in enumerate( chargePorts.chargePorts ):
        if vehicle is not None:
            vehicle.updateLaxity( common.currentTime )

    # now do the llfQueue
    for index, vehicle in enumerate( llfQueue ):
        vehicle.updateLaxity( common.currentTime )
