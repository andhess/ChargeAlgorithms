llfSimpleQueue = []

#  ------ LLF SIMPLE --------
# This algorithm runs under the same premise as the other LLF algorithm except in this instance laxity is only computed once
# upon arrival
# laxity is still defined as freeTime/totalTime where freeTime = (departure - arrival - chargeTime) and totalTime = (departure - arrival) 
# However, since laxity is only calculated once, if a car has a small laxity there is a good chance that it will never be charged 

llfSimpleIndex = -1

def simulateLLFSimple( arrayOfVehicleArrivals ):
    
    # reset global variables such as time, done/failed lots
    updateGlobals()
    global currentTime
    global llfSimpleIndex

    # initialize a CSV document for storing all data
    generateCSV( "llfSimple" )

    # iterate through each vehicle in each minute
    for minute, numVehiclesPerMin in enumerate( arrayOfVehicleArrivals ):
        for vehicle in numVehiclesPerMin:
            port = openChargePort()

            # there is an open chargePort, add vehicle to it
            if port is not None:
                chargePorts[ port ] = vehicle

            # no open chargePort, append to llfQueue
            else:

                llfSimpleQueue.append( vehicle )

                # update the llfIndex if this vehicle is better
                if llfSimpleIndex == -1 or vehicle.laxity < llfSimpleQueue[ llfSimpleIndex ].laxity:
                    llfSimpleIndex = len( llfQueue ) - 1

        updateVehiclesLLFSimple()
        currentTime += 1

    # vehicles done arriving, now continue with the simulation
    while chargePortsEmpty() == False or len( llfSimpleQueue ) != 0:
        updateVehiclesLLFSimple()
        currentTime += 1

    print "LLF Simple: total number of cars: ", numberOfVehiclesInSimulation , \
          "  current time: " , currentTime , \
          "  done charging lot: " , len( doneChargingLot ) , \
          "  failed charing lot: " , len( failedLot ) , \
          "  llfQueue size:  " , len( llfQueue ) , \
          "  chargePort " , chargePorts
        

# called to update the vehicles for each minute of simulation
def updateVehiclesLLFSimple():
    global currentTime
    global llfSimpleIndex
    print "--------------------"
    print "llfSimpleIndex: ",llfSimpleIndex

    # update chargePortCSV
    exportChargePortsToCSV()

    # increment the charge for the cars that were charging
    for index, vehicle in enumerate( chargePorts ):

        # add one minute of charge
        if vehicle is not None:
            vehicle.currentCharge += ( vehicle.chargeRate ) / 60

    # now move cars around so the laxity property is maintained
    for index, vehicle in enumerate( chargePorts ):
        if vehicle is not None:
            removed = False

            #check if done charging
            if vehicle.currentCharge >= vehicle.chargeNeeded:
                print "vehicle charged", vehicle.id
                exportVehicleToCSV( vehicle, "SUCCESS" )
                doneChargingLot.append( vehicle )
                
                if len( llfSimpleQueue ) > 0:
                    chargePorts[ index ] = llfSimpleQueue[ llfSimpleIndex ]
                    del llfSimpleQueue[ llfSimpleIndex ]  
                    llfSimpleIndex = lowestLaxity()
                else:
                    chargePorts[ index ] = None
                removed = True
            
            

            # check if deadline reached
            if currentTime >= vehicle.depTime and not removed:
                print "vehicle's departure time reached", vehicle.id
                exportVehicleToCSV( vehicle, "FAILURE" )
                failedLot.append( vehicle )
        
                if len( llfSimpleQueue ) > 0:
                    chargePorts[ index ] = llfSimpleQueue[ llfSimpleIndex ]
                    del llfSimpleQueue[ llfSimpleIndex ]
                    llfSimpleIndex = lowestLaxity() # function defined in LLF section, iterates through llfQueue for lowest laxity
                else:
                    chargePorts[ index ] = None

            # print "the laxity index is   :    "  ,  llfSimpleIndex  , "    the queue size is   :   "  , len( llfQueue )

            # check if all cars in chargePorts still have lowest laxity
            if llfSimpleIndex != -1 and vehicle.laxity > llfSimpleQueue[ llfSimpleIndex ].laxity:

                # swap vehicle of llfSimpleIndex with the current vehicle in the loop
                temp = vehicle
                chargePorts[ index ] = llfSimpleQueue[ llfSimpleIndex ]
                llfSimpleQueue[ llfSimpleIndex ] = temp

                # llfIndex is unchanged and still correctly points to the next lowest laxity


# gets index for the vehicle with the lowest laxity from llf
def lowestLaxity():
    if len( llfSimpleQueue ) == 0:
        return - 1
    return llfSimpleQueue.index( min( llfSimpleQueue, key = attrgetter( 'laxity' ) ) )

