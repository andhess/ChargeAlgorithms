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
    updateGlobals()
    global currentTime
    global llfIndex
    llfIndex =  -1

    # initialize a CSV document for storing all data
    generateCSV( "llfSmart" )

    # iterate through each vehicle in each minute
    for minute, numVehiclesPerMin in enumerate( arrayOfVehicleArrivals ):
        for vehicle in numVehiclesPerMin:
            port = openChargePort()

            # there is an open chargePort, add vehicle to it
            if port is not None:
                chargePorts[ port ] = vehicle

            # no open chargePort, append to llfQueue
            else:
                llfQueue.append( vehicle )

                # update the llfIndex if this vehicle is better
                if llfIndex == -1 or vehicle.laxity < llfQueue[ llfIndex ].laxity:
                    llfIndex = len( llfQueue ) - 1

        updateVehiclesLLF()
        currentTime += 1

    # vehicles done arriving, now continue with the simulation
    while chargePortsEmpty() == False or not len( llfQueue ) == 0:
        updateVehiclesLLF()
        currentTime += 1

    print "LLF Complex:  total number of cars: ", numberOfVehiclesInSimulation , \
          "  current time: " , currentTime , \
          "  done charging lot: " , len( doneChargingLot ) , \
          "  failed charing lot: " , len( failedLot ) , \
          "  llfQueue size:  " , len( llfQueue ) , \
          "  chargePort " , chargePorts
        

# called to update the vehicles for each minute of simulation
def updateVehiclesLLF():
    global currentTime
    global llfIndex

    # update chargePortCSV
    exportChargePortsToCSV()

    # increment the charge for the cars that were charging
    for index, vehicle in enumerate( chargePorts ):

        # add one minute of charge
        if vehicle is not None:
            vehicle.currentCharge += ( vehicle.chargeRate ) / 60

            # print "Charge:  " , vehicle.currentCharge , "   " , vehicle.chargeNeeded
            # print "Timing:  " , currentTime , "   ",  vehicle.depTime 
    
    # update the laxity for all the peeps
    updateLaxityForAll()

    # now move cars around so the laxity property is maintained
    for index, vehicle in enumerate( chargePorts ):
        if vehicle is not None:

            #check if done charging
            if vehicle.currentCharge >= vehicle.chargeNeeded:
                exportVehicleToCSV( vehicle, "SUCCESS" )
                doneChargingLot.append( vehicle )
                
                if len( llfQueue ) > 0:
                    chargePorts[ index ] = llfQueue[ llfIndex ]
                    del llfQueue[ llfIndex ]  
                    llfIndex = lowestLaxity()
                else:
                    chargePorts[ index ] = None
            

            # check if deadline reached
            if currentTime >= vehicle.depTime:
                exportVehicleToCSV( vehicle, "FAILURE" )
                failedLot.append( vehicle )
                
                if len( llfQueue ) > 0:
                    chargePorts[ index ] = llfQueue[ llfIndex ]
                    del llfQueue[ llfIndex ]
                    llfIndex = lowestLaxity()
                else:
                    chargePorts[ index ] = None

            # print "the laxity index is   :    "  ,  llfIndex  , "    the queue size is   :   "  , len( llfQueue )

            # check if all cars in chargePorts still have lowest laxity
            if llfIndex != -1 and vehicle.laxity > llfQueue[ llfIndex ].laxity:

                # swap vehicle of llfIndex with the current vehicle in the loop
                temp = vehicle
                chargePorts[ index ] = llfQueue[ llfIndex ]
                llfQueue[ llfIndex ] = temp

                # llfIndex is unchanged and still correctly points to the next lowest laxity

# gets index for the vehicle with the lowest laxity from llf
def lowestLaxity():
    if len( llfQueue ) == 0:
        return -1
    return llfQueue.index( min( llfQueue, key = attrgetter( 'laxity' ) ) )


# laxity constantly changes as time advances and certain cars are charged
def updateLaxityForAll():

    # first do chargePorts
    for index, vehicle in enumerate( chargePorts ):
        if vehicle is not None:
            vehicle.updateLaxity( currentTime )

    # now do the llfQueue
    for index, vehicle in enumerate( llfQueue ):
        vehicle.updateLaxity( currentTime )
